"""Authorized Windows host assessment."""

import platform
from typing import Any

from nighthawk.logging.setup import get_logger
from nighthawk.scope.manager import ScopeManager
from nighthawk.models.core import Asset

logger = get_logger("windows")


class WindowsHostCollector:
    """Collect observable Windows host properties."""

    def __init__(self) -> None:
        self.name = "windows_host"
        self.version = "1.0.0"

    async def can_run(self, target: str, scope_config: Any = None) -> bool:
        return platform.system().lower() == "windows"

    async def run(
        self,
        target: str,
        scope_manager: ScopeManager | None = None,
        **context: Any,
    ) -> dict[str, Any]:
        logger.info("windows_assessment_start", target=target)
        # Safe, non-destructive observation only
        asset = Asset(
            hostname=platform.node(),
            platform="windows",
            os_name=platform.system(),
            os_version=platform.release(),
            services=["windows_host_collector"],
        )
        results = {
            "asset": asset.model_dump(),
            "observations": {
                "platform": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
            },
            "note": "Windows module performs safe, read-only telemetry. No destructive actions performed.",
        }
        logger.info("windows_assessment_complete", observations=list(results["observations"].keys()))
        return results
