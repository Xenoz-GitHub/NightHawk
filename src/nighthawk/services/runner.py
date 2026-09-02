"""Campaign runner: executes authorized scanners and normalizes results.

Bridges the existing scanners (`web`, `dns`, `network`, technology
fingerprinting) into the service layer: every result becomes persisted
domain objects (assets, findings, raw scan rows) and normalized events.
Scanners are injectable so tests can stub them without any network I/O.
"""

from __future__ import annotations

import asyncio
from urllib.parse import urlparse
from uuid import UUID

from nighthawk.config.config import get_config
from nighthawk.dns.scanner import DNSIntelligence
from nighthawk.logging.setup import get_logger
from nighthawk.models.core import Asset, Evidence, Finding, Severity
from nighthawk.network.scanner import NetworkScanner
from nighthawk.scope.manager import ScopeManager
from nighthawk.services.campaign_service import CampaignService
from nighthawk.technology.scanner import FingerprintEngine
from nighthawk.web.scanner import WebScanner

logger = get_logger("runner")

# Module registry. `tech` reuses the collected web evidence (fingerprinting)
# rather than making new requests.
MODULES = ("web", "dns", "network", "tech")

_REMEDIATION_HEADERS = (
    "Configure the missing security header following current best practice "
    "(e.g. CSP via `Content-Security-Policy`, HSTS via `Strict-Transport-Security`)."
)

# Headers worth a MEDIUM when absent; the rest are LOW.
_MEDIUM_HEADERS = {"strict_transport_security", "content_security_policy"}


class CampaignRunner:
    """Executes the modules of a running campaign and persists results."""

    def __init__(
        self,
        service: CampaignService,
        scope_manager: ScopeManager | None = None,
        web_scanner: WebScanner | None = None,
        dns_scanner: DNSIntelligence | None = None,
        network_scanner: NetworkScanner | None = None,
        fingerprints: FingerprintEngine | None = None,
    ) -> None:
        self._service = service
        self._scope = scope_manager or ScopeManager(get_config().default_scope_path)
        self._web = web_scanner or WebScanner()
        self._dns = dns_scanner or DNSIntelligence()
        self._network = network_scanner or NetworkScanner()
        self._fingerprints = fingerprints or FingerprintEngine()
        self._web_cache: dict[str, dict] = {}

    async def run_campaign(
        self, campaign_id: UUID, targets: list[str], modules: list[str] | None = None,
    ) -> None:
        """Run all modules against all targets, then complete the campaign."""
        modules = [m for m in (modules or list(MODULES)) if m in MODULES]
        self._web_cache.clear()
        for target in targets:
            for module in modules:
                if not await self._wait_while_paused(campaign_id):
                    return  # cancelled or failed while paused
                await self._run_module(campaign_id, module, target)
                self._service.emit_graph_updated(campaign_id)
        final = self._service.get(campaign_id)
        if final.status.value == "running":
            self._service.complete(campaign_id)

    # ------------------------------------------------------------------ #
    # Module dispatch
    # ------------------------------------------------------------------ #

    async def _run_module(self, campaign_id: UUID, module: str, target: str) -> None:
        try:
            if module == "dns":
                self._normalize_dns(campaign_id, target, await self._dns.run(target, scope_manager=self._scope))
            elif module == "network":
                self._normalize_network(campaign_id, target, await self._network.run(target, scope_manager=self._scope))
            elif module == "web":
                self._normalize_web(campaign_id, target, await self._fetch_web(target), with_findings=True)
            elif module == "tech":
                self._normalize_web(campaign_id, target, await self._fetch_web(target), with_findings=False)
        except Exception as exc:  # one failing module never kills the campaign
            logger.warning("runner_module_error", module=module, target=target, error=str(exc))
            self._service.record_scan_error(campaign_id, module, target, str(exc))

    async def _fetch_web(self, target: str) -> dict:
        """Web scan with per-target caching so `web` and `tech` share one request."""
        if target not in self._web_cache:
            self._web_cache[target] = await self._web.run(target, scope_manager=self._scope)
        return self._web_cache[target]

    # ------------------------------------------------------------------ #
    # Normalizers → assets + findings
    # ------------------------------------------------------------------ #

    def _normalize_dns(self, campaign_id: UUID, target: str, result: dict) -> None:
        records = result.get("records", {}) or {}
        ips = [
            r for qtype in ("A", "AAAA")
            for r in records.get(qtype, []) if not r.startswith("error:")
        ]
        self._service.add_asset(campaign_id, Asset(
            hostname=target,
            ip_addresses=ips,
            platform="dns",
            metadata={"record_types": sorted(records.keys())},
        ))

    def _normalize_network(self, campaign_id: UUID, target: str, result: dict) -> None:
        services = [s for s in result.get("results", []) if s.get("state") == "open"]
        names = [f"{s.get('service', 'unknown')}/{s['port']}" for s in services]
        self._service.add_asset(campaign_id, Asset(
            hostname=target,
            platform="network",
            services=names,
            metadata={"open_ports": [s["port"] for s in services]},
        ))

    def _normalize_web(self, campaign_id: UUID, target: str, result: dict, *, with_findings: bool) -> None:
        url = result.get("url") or (target if target.startswith("http") else f"https://{target}")
        hostname = urlparse(url).hostname or target

        technologies = [m.name for m in self._fingerprints.match_technology(result)]

        scheme = "https" if result.get("tls", {}).get("supported") else "http"
        asset = self._service.add_asset(campaign_id, Asset(
            hostname=hostname,
            platform="web",
            services=[scheme],
            technologies=technologies,
            metadata={
                "url": url,
                "status_code": result.get("status_code"),
                "content_type": result.get("content_type"),
            },
        ))

        if not with_findings:
            return

        for header, info in (result.get("security_headers") or {}).items():
            if info.get("present"):
                continue
            severity = Severity.MEDIUM if header in _MEDIUM_HEADERS else Severity.LOW
            self._service.add_finding(campaign_id, Finding(
                title=f"Missing security header: {header.replace('_', '-')}",
                description=(
                    f"The response from {url} does not include the "
                    f"`{header.replace('_', '-')}` security header."
                ),
                severity=severity,
                confidence=1.0,
                category="web/headers",
                asset_id=asset.id,
                evidence=[Evidence(
                    description=f"Security header '{header.replace('_', '-')}' absent from response",
                    source="web",
                )],
                remediation=_REMEDIATION_HEADERS,
            ))

    # ------------------------------------------------------------------ #
    # Pause / cancel cooperation
    # ------------------------------------------------------------------ #

    async def _wait_while_paused(self, campaign_id: UUID) -> bool:
        """Block while paused. Returns False if the campaign must abort."""
        while True:
            status = self._service.get(campaign_id).status
            if status.value == "paused":
                await asyncio.sleep(0.2)
                continue
            return status.value == "running"
