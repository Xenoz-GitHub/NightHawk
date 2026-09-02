"""Authorized DNS reconnaissance."""

import dns.resolver
import dns.reversename
from datetime import datetime, timezone
from typing import Any

from nighthawk.logging.setup import get_logger
from nighthawk.scope.manager import ScopeManager
from nighthawk.core.exceptions import ScopeViolationError

logger = get_logger("dns")


class DNSIntelligence:
    """Low-impact DNS intelligence scanner."""

    def __init__(self) -> None:
        self.name = "dns"
        self.version = "1.0.0"
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 5.0
        self.resolver.lifetime = 10.0

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

        results: dict[str, Any] = {
            "target": target,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "records": {},
        }
        try:
            for qtype in ("A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA"):
                try:
                    answers = self.resolver.resolve(target, qtype)
                    results["records"][qtype] = [str(r) for r in answers]
                except dns.resolver.NoAnswer:
                    results["records"][qtype] = []
                except Exception as exc:
                    results["records"][qtype] = [f"error: {exc}"]
        except Exception as exc:
            logger.error("dns_scan_error", target=target, error=str(exc))
            results["error"] = str(exc)
        return results
