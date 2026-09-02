"""Scope validation and authorization boundary enforcement."""

from pathlib import Path
from typing import Any
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
            raise ConfigurationError(f"Scope file not found: {self.config_path}")
        try:
            data = yaml.safe_load(self.config_path.read_text()) or {}
            return ScopeConfig(**data)
        except Exception as exc:
            raise ConfigurationError(f"Invalid scope file: {exc}") from exc

    def is_authorized(self, target: str) -> bool:
        """Check whether a target string falls within scope."""
        try:
            # IP/CIDR check
            if self._is_ip_or_cidr_target(target):
                return self._check_ip_scope(target)
            # Domain check
            if self._is_domain_target(target):
                return target in self.config.domains or any(
                    target.endswith("." + d) or d.endswith("." + target)
                    for d in self.config.domains
                    if target and d
                )
            # URL check
            if target.startswith(("http://", "https://")):
                return target in self.config.urls
            # Repository check
            if Path(target).exists() or target.startswith(("./", "/", ".git")):
                return target in self.config.repositories or any(
                    str(Path(repos)) == target or target.startswith(str(repos))
                    for repos in self.config.repositories
                )
        except Exception:
            return False
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
