"""Authorized network discovery and service fingerprinting."""

import asyncio
import ipaddress
from datetime import datetime, timezone
from typing import Any

import httpx

from nighthawk.logging.setup import get_logger
from nighthawk.scope.manager import ScopeManager
from nighthawk.core.exceptions import ScopeViolationError, ScannerTimeoutError
from nighthawk.models.core import NetworkScanResult, ServiceInfo

logger = get_logger("network")


class NetworkScanner:
    """Async network reconnaissance scanner."""

    def __init__(self, timeout: float = 5.0, max_ports: int = 50) -> None:
        self.timeout = timeout
        self.max_ports = max_ports
        self.name = "network"
        self.version = "1.0.0"

    async def can_run(self, target: str, scope_config: Any = None) -> bool:
        return True

    async def run(
        self,
        target: str,
        scope_manager: ScopeManager | None = None,
        **context: Any,
    ) -> dict[str, Any]:
        if scope_manager is not None:
            scope_manager.validate_target(target)

        result = NetworkScanResult(target=target)
        try:
            # Basic reachability / fingerprinting
            services = await self._scan_target(target)
            result.results = services
        except asyncio.TimeoutError:
            raise ScannerTimeoutError(f"Network scan timed out for {target}")
        except Exception as exc:
            result.errors.append(str(exc))
            logger.error("network_scan_error", target=target, error=str(exc))
        return result.model_dump(mode="json")

    async def _scan_target(self, target: str) -> list[dict[str, Any]]:
        services: list[dict[str, Any]] = []
        try:
            # Try common ports
            ports = [80, 443, 22, 25, 53, 3306, 5432, 8080, 8443]
            for port in ports[: self.max_ports]:
                service = await self._probe_port(target, port)
                if service:
                    services.append(service)
        except Exception as exc:
            logger.error("network_probe_error", target=target, error=str(exc))
        return services

    async def _probe_port(self, target: str, port: int) -> dict[str, Any] | None:
        try:
            url = f"http://{target}:{port}" if port not in (443, 8443) else f"https://{target}:{port}"
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=False) as client:
                try:
                    resp = await client.get(url, headers={"User-Agent": "NIGHTHAWK/1.0"})
                    return {
                        "port": port,
                        "protocol": "tcp",
                        "state": "open",
                        "service": "http" if port == 80 else "https" if port in (443, 8443) else "unknown",
                        "status_code": resp.status_code,
                        "headers": dict(resp.headers),
                        "banner": None,
                    }
                except httpx.ConnectError:
                    return None
                except httpx.TimeoutException:
                    return None
        except Exception:
            return None
