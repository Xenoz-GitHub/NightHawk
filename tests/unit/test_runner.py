"""CampaignRunner tests — stubbed scanners, no network I/O."""

import asyncio

import pytest

from nighthawk.services.campaign_service import CampaignService
from nighthawk.services.runner import CampaignRunner


class StubWebScanner:
    async def run(self, target, scope_manager=None, **ctx):
        return {
            "url": f"https://{target}",
            "status_code": 200,
            "content_type": "text/html",
            "headers": {"server": "nginx/1.24", "x-powered-by": "Next.js"},
            "html_text": "<html>__NEXT_DATA__</html>",
            "cookies": [],
            "security_headers": {
                "strict_transport_security": {"present": False, "value": ""},
                "x_frame_options": {"present": False, "value": ""},
                "content_security_policy": {"present": True, "value": "default-src 'self'"},
            },
            "tls": {"supported": True, "protocol": "TLSv1.3"},
        }


class StubDNS:
    async def run(self, target, scope_manager=None, **ctx):
        return {"target": target, "records": {"A": ["93.184.216.34"], "MX": []}}


class StubNetwork:
    async def run(self, target, scope_manager=None, **ctx):
        return {
            "results": [
                {"port": 443, "state": "open", "service": "https"},
                {"port": 8080, "state": "closed", "service": "unknown"},
            ]
        }


class ExplodingDNS:
    async def run(self, target, scope_manager=None, **ctx):
        raise RuntimeError("dns exploded")


@pytest.fixture()
def service(tmp_path, monkeypatch):
    monkeypatch.setenv("NIGHTHAWK_DATABASE_URL", f"sqlite:///{(tmp_path / 'r.db').as_posix()}")
    import nighthawk.config.config as config_mod
    from nighthawk.database import engine as db_engine_mod

    monkeypatch.setattr(config_mod, "_CONFIG_INSTANCE", None)
    db_engine_mod.reset_engine()
    yield CampaignService()
    db_engine_mod.reset_engine()


def _runner(service, dns=None):
    return CampaignRunner(
        service,
        web_scanner=StubWebScanner(),
        dns_scanner=dns or StubDNS(),
        network_scanner=StubNetwork(),
    )


def test_runner_full_cycle(service):
    campaign = service.create("runner-test", targets=["example.com"])
    cid = campaign.id
    service.start(cid)
    asyncio.run(_runner(service).run_campaign(cid, ["example.com"]))

    final = service.get(cid)
    assert final.status.value == "completed"
    assert final.completed_at is not None

    assets = service.list_assets(cid)
    assert len(assets) == 1  # dns + network + web merged into one hostname asset
    web_asset = assets[0]
    assert "nginx" in web_asset.technologies  # fingerprinted from Server header
    assert "https/443" in web_asset.services
    assert "93.184.216.34" in web_asset.ip_addresses
    assert web_asset.platform == "web"  # richest provenance view wins

    findings = service.list_findings(cid)
    titles = {f.title for f in findings}
    assert "Missing security header: strict-transport-security" in titles
    assert "Missing security header: x-frame-options" in titles
    assert not any("content-security-policy" in t for t in titles)  # present → skipped
    for f in findings:
        assert f.asset_id == web_asset.id
        assert f.evidence

    progress = service.get_progress(cid)
    assert progress["findings"] == len(findings)
    assert progress["assets"] == 1


def test_runner_module_failure_is_contained(service):
    campaign = service.create("resilient", targets=["example.com"])
    cid = campaign.id
    service.start(cid)
    asyncio.run(_runner(service, dns=ExplodingDNS()).run_campaign(cid, ["example.com"]))

    assert service.get(cid).status.value == "completed"  # other modules finished
    # scan.error row + event were recorded
    from nighthawk.database import engine as db_engine_mod
    from nighthawk.database.models import ScanResultDB
    from sqlalchemy import select
    with db_engine_mod.get_session() as session:
        rows = session.scalars(
            select(ScanResultDB).where(ScanResultDB.campaign_id == cid)
        ).all()
    assert any(r.result_json.get("error") == "dns exploded" for r in rows)
