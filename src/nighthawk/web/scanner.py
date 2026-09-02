"""Website reconnaissance and security assessment."""

import ssl
import socket
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from typing import Any

import httpx
import httpcore

from nighthawk.logging.setup import get_logger
from nighthawk.scope.manager import ScopeManager
from nighthawk.core.exceptions import ScopeViolationError, ScannerTimeoutError

logger = get_logger("web")


class WebScanner:
    """Authorized website assessment scanner."""

    def __init__(self, timeout: float = 10.0, max_redirects: int = 5) -> None:
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.name = "web"
        self.version = "1.0.0"

    async def can_run(self, target: str, scope_config: Any = None) -> bool:
        return target.startswith(("http://", "https://")) or (":" not in target and "/" not in target)

    async def run(
        self,
        target: str,
        scope_manager: ScopeManager | None = None,
        **context: Any,
    ) -> dict[str, Any]:
        url = target if target.startswith("http") else f"https://{target}"
        if scope_manager is not None:
            scope_manager.validate_target(url)

        result: dict[str, Any] = {
            "url": url,
            "scan_time": datetime.now(timezone.utc).isoformat(),
            "headers": {},
            "cookies": [],
            "redirect_chain": [],
            "security_headers": {},
            "tls": {},
            "robots_sitemap": {},
        }
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=False,
                max_redirects=self.max_redirects,
                headers={"User-Agent": "NIGHTHAWK/1.0 (Ethical Security Assessment)"},
            ) as client:
                # Main request
                try:
                    resp = await client.get(url)
                    result["status_code"] = resp.status_code
                    result["headers"] = dict(resp.headers)
                    result["content_type"] = resp.headers.get("content-type")
                    result["body"] = resp.text
                    result["html_text"] = resp.text
                    result["cookies"] = [
                        {"name": c.name, "value": "[REDACTED]", "secure": c.secure, "httponly": c.has_nonstandard_attr("HttpOnly"), "samesite": c.get("SameSite", "none")}
                        for c in resp.cookies.jar
                    ]
                    result["redirect_chain"] = [str(h) for h in resp.history] if resp.history else []
                except Exception as exc:
                    result["request_error"] = str(exc)

                # Security headers analysis
                result["security_headers"] = self._analyze_security_headers(resp.headers if 'resp' in locals() else {})

                # TLS info
                result["tls"] = await self._get_tls_info(urlparse(url).hostname or url)

                # Robots / Sitemap
                result["robots_sitemap"] = await self._check_public_resources(url)

        except Exception as exc:
            logger.error("web_scan_error", url=url, error=str(exc))
            result["error"] = str(exc)
        return result

    def _analyze_security_headers(self, headers: dict[str, str]) -> dict[str, Any]:
        analysis: dict[str, Any] = {}
        for header in (
            "strict-transport-security",
            "content-security-policy",
            "x-content-type-options",
            "referrer-policy",
            "permissions-policy",
            "x-frame-options",
            "x-xss-protection",
        ):
            present = header in {k.lower(): v for k, v in headers.items()}
            analysis[header.replace("-", "_")] = {"present": present, "value": headers.get(header, headers.get(header.lower(), ""))}
        return analysis

    async def _get_tls_info(self, hostname: str) -> dict[str, Any]:
        info: dict[str, Any] = {"supported": False, "protocol": None, "cipher": None, "cert_expiry": None}
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=5.0) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    info["supported"] = True
                    info["protocol"] = ssock.version()
                    info["cipher"] = ssock.cipher()[0] if ssock.cipher() else None
                    cert = ssock.getpeercert()
                    if cert.get("notAfter"):
                        info["cert_expiry"] = cert["notAfter"]
                    if cert.get("subjectAltName"):
                        info["subject_alt_names"] = cert["subjectAltName"]
        except Exception:
            pass
        return info

    async def _check_public_resources(self, base_url: str) -> dict[str, Any]:
        resources: dict[str, Any] = {}
        for path in ("/robots.txt", "/sitemap.xml"):
            try:
                full = urljoin(base_url, path)
                async with httpx.AsyncClient(timeout=5.0, follow_redirects=False) as client:
                    resp = await client.get(full, headers={"User-Agent": "NIGHTHAWK/1.0"})
                    resources[path] = {
                        "status": resp.status_code,
                        "length": len(resp.text),
                        "exists": resp.status_code == 200,
                    }
            except Exception:
                resources[path] = {"exists": False, "status": None}
        return resources
