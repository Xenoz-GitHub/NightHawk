"""Authorized Linux host assessment."""

import platform
import os
from typing import Any

from nighthawk.logging.setup import get_logger
from nighthawk.scope.manager import ScopeManager
from nighthawk.models.core import Asset

logger = get_logger("linux")


class LinuxHostCollector:
    """Collect observable Linux host properties."""

    def __init__(self) -> None:
        self.name = "linux_host"
        self.version = "1.0.0"

    async def can_run(self, target: str, scope_config: Any = None) -> bool:
        return platform.system().lower() == "linux"

    async def run(
        self,
        target: str,
        scope_manager: ScopeManager | None = None,
        **context: Any,
    ) -> dict[str, Any]:
        logger.info("linux_assessment_start", target=target)
        observations: dict[str, Any] = {
            "platform": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
        }
        # Safe read-only observations
        try:
            observations["uname"] = os.uname().sysname
        except Exception:
            pass
        asset = Asset(
            hostname=platform.node(),
            platform="linux",
            os_name=platform.system(),
            os_version=platform.release(),
            services=["linux_host_collector"],
        )
        results = {
            "asset": asset.model_dump(),
            "observations": observations,
            "note": "Linux module performs safe, read-only telemetry. No destructive actions performed.",
        }
        logger.info("linux_assessment_complete", observations=list(observations.keys()))
        return results
