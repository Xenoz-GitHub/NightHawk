"""Campaign orchestration and scanner coordination."""

import asyncio
from datetime import datetime, timezone
from typing import Any

from nighthawk.logging.setup import get_logger
from nighthawk.scope.manager import ScopeManager
from nighthawk.core.exceptions import NightHawkError

logger = get_logger("orchestrator")


class AssessmentCampaign:
    """A single authorized assessment campaign."""

    def __init__(self, campaign_id: str, scope_manager: ScopeManager) -> None:
        self.campaign_id = campaign_id
        self.scope_manager = scope_manager
        self.started_at = datetime.now(timezone.utc)
        self.completed_at: datetime | None = None
        self.status = "running"
        self.results: list[dict[str, Any]] = []

    async def run_scan(self, scanner: Any, target: str, **kwargs: Any) -> None:
        """Run a scanner under scope enforcement."""
        logger.info("campaign_scan_start", campaign=self.campaign_id, scanner=scanner.__class__.__name__, target=target)
        try:
            result = await scanner.run(target, scope_manager=self.scope_manager, **kwargs)
            self.results.append({
                "scanner": scanner.__class__.__name__,
                "target": target,
                "result": result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        except NightHawkError as exc:
            logger.error("campaign_scan_error", campaign=self.campaign_id, error=str(exc))
            self.results.append({
                "scanner": scanner.__class__.__name__,
                "target": target,
                "error": str(exc),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

    def complete(self) -> None:
        self.completed_at = datetime.now(timezone.utc)
        self.status = "completed"
        logger.info("campaign_completed", campaign=self.campaign_id, duration_seconds=(self.completed_at - self.started_at).total_seconds())
