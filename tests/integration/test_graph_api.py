"""Graph endpoint integration: runner-populated data → cytoscape JSON."""

import asyncio
import uuid


class StubWeb:
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
                "content_security_policy": {"present": True, "value": "default-src 'self'"},
            },
            "tls": {"supported": True, "protocol": "TLSv1.3"},
        }


class StubDNS:
    async def run(self, target, scope_manager=None, **ctx):
        return {"target": target, "records": {"A": ["93.184.216.34"]}}


class StubNetwork:
    async def run(self, target, scope_manager=None, **ctx):
        return {"results": [{"port": 443, "state": "open", "service": "https"}]}


def test_graph_endpoint_shape(api_client):
    from nighthawk.services import CampaignService
    from nighthawk.services.runner import CampaignRunner

    service = CampaignService()
    campaign = service.create("graph-test", targets=["example.com"])
    service.start(campaign.id)
    runner = CampaignRunner(
        service,
        web_scanner=StubWeb(),
        dns_scanner=StubDNS(),
        network_scanner=StubNetwork(),
    )
    asyncio.run(runner.run_campaign(campaign.id, ["example.com"]))

    resp = api_client.get(f"/api/v1/campaigns/{campaign.id}/graph")
    assert resp.status_code == 200
    body = resp.json()
    assert body["nodes"] and body["edges"]

    types = {n["type"] for n in body["nodes"]}
    assert {"asset", "finding"} <= types  # HSTS absence must surface as a finding node

    node_ids = {n["id"] for n in body["nodes"]}
    assert all(e["source"] in node_ids and e["target"] in node_ids for e in body["edges"])
    assert all(e["relationship"] for e in body["edges"])

    asset_nodes = [n for n in body["nodes"] if n["type"] == "asset"]
    assert len(asset_nodes) == 1  # dns/network/web merged into one hostname asset
    assert asset_nodes[0]["label"] == "example.com"

    assert api_client.get(f"/api/v1/campaigns/{uuid.uuid4()}/graph").status_code == 404
