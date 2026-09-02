"""Scope validation and authorization boundary enforcement."""

from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import yaml
import ipaddress

from nighthawk.core.exceptions import ScopeViolationError, ConfigurationError
from nighthawk.models.core import ScopeConfig
from nighthawk.logging.setup import get_logger

logger = get_logger("scope")


class ScopeManager:
    """Manages authorized assessment scope and validates targets."""

    def __init__(self, config_path: str | Path) -> None:
        self.config_path = Path(config_path)
        self.config = self._load()
        logger.info("scope_loaded", path=str(self.config_path), modules=self.config.allowed_modules)

    def _load(self) -> ScopeConfig:
        if not self.config_path.exists():
            # Auto-create a safe default scope for first-time users
            default_data = {
                "name": "default_scope",
                "domains": ["localhost", "127.0.0.1"],
                "ips": ["127.0.0.1"],
                "cidrs": ["127.0.0.0/8"],
                "urls": ["http://localhost"],
                "repositories": ["."],
                "allowed_modules": [
                    "dns", "http", "tls", "technology", "service_enumeration", "secret_scanning"
                ],
                "rate_limits": {"requests_per_second": 5},
            }
            self.config_path.write_text(yaml.safe_dump(default_data, default_flow_style=False))
            logger.info("scope_default_created", path=str(self.config_path))
        try:
            data = yaml.safe_load(self.config_path.read_text()) or {}
            if not isinstance(data, dict):
                data = {}

            normalized = dict(data)
            normalized.setdefault("name", "default_scope")

            legacy_modules = normalized.pop("modules", None)
            if "allowed_modules" not in normalized and legacy_modules:
                normalized["allowed_modules"] = legacy_modules
            elif isinstance(normalized.get("allowed_modules"), list) and not normalized["allowed_modules"] and legacy_modules:
                normalized["allowed_modules"] = legacy_modules

            normalized.pop("metadata", None)
            return ScopeConfig(**normalized)
        except Exception as exc:
            raise ConfigurationError(f"Invalid scope file: {exc}") from exc

    def is_authorized(self, target: str) -> bool:
        """Check whether a target string falls within scope."""
        try:
            normalized_target = self._normalize_target(target)

            # IP/CIDR check
            if self._is_ip_or_cidr_target(normalized_target):
                return self._check_ip_scope(normalized_target)

            # URL check
            if target.startswith(("http://", "https://")):
                url = self._normalize_url(target)
                hostname = urlparse(url).hostname or ""

                if self._domain_is_authorized(hostname):
                    return True

                for allowed in self.config.urls:
                    allowed_url = self._normalize_url(allowed)
                    if not allowed_url:
                        continue
                    if url == allowed_url or url.startswith(allowed_url.rstrip("/") + "/"):
                        return True
                    if allowed_url.endswith("/"):
                        allowed_url = allowed_url.rstrip("/")
                    if url.startswith(allowed_url) and (allowed_url.count("/") == 2):
                        return True
                return False

            # Domain check
            if self._is_domain_target(normalized_target):
                return self._domain_is_authorized(normalized_target)

            # Repository check
            if Path(target).exists() or target.startswith(("./", "/", ".git")):
                return target in self.config.repositories or any(
                    str(Path(repos)) == target or target.startswith(str(repos))
                    for repos in self.config.repositories
                )
        except Exception:
            return False
        return False

    def _normalize_target(self, target: str) -> str:
        if not target:
            return target
        if target.startswith(("http://", "https://")):
            return self._normalize_url(target)
        return target.strip().rstrip("/")

    def _normalize_url(self, url: str) -> str:
        value = (url or "").strip()
        if not value:
            return ""
        if "://" not in value:
            value = f"https://{value}"
        parsed = urlparse(value)
        hostname = (parsed.hostname or "").lower().rstrip(".")
        if not hostname:
            return ""
        scheme = (parsed.scheme or "https").lower()
        port = parsed.port
        if port is not None and ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
            port = None
        port_part = f":{port}" if port is not None else ""
        path = parsed.path or "/"
        if path != "/":
            path = path.rstrip("/")
        return f"{scheme}://{hostname}{port_part}{path}"

    def _domain_is_authorized(self, target: str) -> bool:
        target = (target or "").strip().lower().rstrip(".")
        if not target:
            return False
        host = target.split(":", 1)[0].split("/", 1)[0].lstrip(".")
        for allowed in self.config.domains:
            allowed_value = str(allowed).strip().lower().rstrip(".")
            if not allowed_value:
                continue
            allowed_host = allowed_value.split(":", 1)[0].split("/", 1)[0].lstrip(".")
            if allowed_host.startswith("*."):
                suffix = allowed_host[2:]
                if host == suffix or host.endswith("." + suffix):
                    return True
            if host == allowed_host or host.endswith("." + allowed_host) or allowed_host.endswith("." + host):
                return True
        return False

    def _is_ip_or_cidr_target(self, target: str) -> bool:
        try:
            ipaddress.ip_address(target)
            return True
        except ValueError:
            pass
        try:
            ipaddress.ip_network(target, strict=False)
            return True
        except ValueError:
            pass
        return False

    def _is_domain_target(self, target: str) -> bool:
        # Simple heuristic: contains a dot and no protocol/path indicators
        return "." in target and "/" not in target and ":" not in target

    def _check_ip_scope(self, target: str) -> bool:
        try:
            net = ipaddress.ip_network(target, strict=False)
            # Check against CIDR scopes
            for cidr in self.config.cidrs:
                scope_net = ipaddress.ip_network(cidr, strict=False)
                if net.overlaps(scope_net) or net.subnet_of(scope_net) or scope_net.subnet_of(net):
                    return True
            # Check individual IPs
            for ip in self.config.ips:
                if ipaddress.ip_address(target) == ipaddress.ip_address(ip):
                    return True
        except Exception:
            return False
        return False

    def validate_target(self, target: str) -> None:
        """Raise ScopeViolationError if target is unauthorized."""
        if not self.is_authorized(target):
            msg = f"Target '{target}' is not within the authorized scope."
            logger.warning("scope_violation", target=target, message=msg)
            raise ScopeViolationError(msg, target=target)

    def get_authorized_modules(self) -> list[str]:
        return self.config.allowed_modules or [
            "dns", "http", "tls", "technology", "service_enumeration", "secret_scanning"
        ]


class AuthorizationBoundary:
    """Boundary enforcement wrapper for scanners."""

    def __init__(self, scope_manager: ScopeManager) -> None:
        self.scope_manager = scope_manager

    def enforce(self, target: str, allowed_modules: list[str] | None = None) -> None:
        """Enforce scope and module authorization before scanning."""
        self.scope_manager.validate_target(target)
        if allowed_modules is not None:
            authorized = self.scope_manager.get_authorized_modules()
            for mod in allowed_modules:
                if mod not in authorized:
                    msg = f"Module '{mod}' is not authorized in current scope."
                    logger.warning("scope_module_violation", module=mod)
                    raise ScopeViolationError(msg, target=target)
