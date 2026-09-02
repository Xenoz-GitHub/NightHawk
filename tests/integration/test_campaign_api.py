"""Campaign API lifecycle, scope enforcement, and error contract tests."""

import uuid

import pytest


@pytest.fixture()
def campaign_id(api_client):
    resp = api_client.post("/api/v1/campaigns", json={"name": "t1", "targets": ["example.com"]})
    assert resp.status_code == 201
    return resp.json()["id"]


class TestCampaignLifecycle:
    def test_health(self, api_client):
        resp = api_client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_create_returns_201(self, api_client):
        resp = api_client.post(
            "/api/v1/campaigns", json={"name": "op-alpha", "targets": ["example.com"]}
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "created"
        assert body["targets"] == ["example.com"]
        assert body["event_seq"] == 1

    def test_create_empty_name_422(self, api_client):
        resp = api_client.post("/api/v1/campaigns", json={"name": "", "targets": []})
        assert resp.status_code == 422
        assert resp.json()["error"] == "request_validation_error"

    def test_full_lifecycle(self, api_client, campaign_id):
        assert api_client.post(f"/api/v1/campaigns/{campaign_id}/start").json()["status"] == "running"
        assert api_client.post(f"/api/v1/campaigns/{campaign_id}/pause").json()["status"] == "paused"
        assert api_client.post(f"/api/v1/campaigns/{campaign_id}/resume").json()["status"] == "running"
        assert api_client.post(f"/api/v1/campaigns/{campaign_id}/stop").json()["status"] == "cancelled"
        final = api_client.get(f"/api/v1/campaigns/{campaign_id}").json()
        assert final["completed_at"] is not None
        assert final["event_seq"] == 6  # created,queued,started,paused,resumed,cancelled

    def test_get_unknown_404(self, api_client):
        resp = api_client.get(f"/api/v1/campaigns/{uuid.uuid4()}")
        assert resp.status_code == 404
        assert resp.json()["error"] == "campaign_not_found"

    def test_restart_after_cancel_409(self, api_client, campaign_id):
        api_client.post(f"/api/v1/campaigns/{campaign_id}/start")
        api_client.post(f"/api/v1/campaigns/{campaign_id}/stop")
        resp = api_client.post(f"/api/v1/campaigns/{campaign_id}/start")
        assert resp.status_code == 409
        body = resp.json()
        assert body["error"] == "invalid_state_transition"
        assert body["current_state"] == "cancelled"
        assert body["requested_state"] == "running"

    def test_pause_before_start_409(self, api_client, campaign_id):
        resp = api_client.post(f"/api/v1/campaigns/{campaign_id}/pause")
        assert resp.status_code == 409

    def test_list_includes_created(self, api_client, campaign_id):
        campaigns = api_client.get("/api/v1/campaigns").json()
        assert any(c["id"] == campaign_id for c in campaigns)


class TestScopeEnforcement:
    def test_out_of_scope_target_403(self, api_client):
        resp = api_client.post(
            "/api/v1/campaigns", json={"name": "bad", "targets": ["not-authorized.tld"]}
        )
        assert resp.status_code == 403
        body = resp.json()
        assert body["error"] == "scope_violation"
        assert body["target"] == "not-authorized.tld"

    def test_nothing_persisted_on_rejection(self, api_client):
        api_client.post(
            "/api/v1/campaigns", json={"name": "bad", "targets": ["not-authorized.tld"]}
        )
        assert api_client.get("/api/v1/campaigns").json() == []


class TestEventStreaming:
    def test_ws_receives_lifecycle_event(self, api_client, campaign_id):
        with api_client.websocket_connect(f"/ws/campaigns/{campaign_id}") as ws:
            # a lifecycle change while subscribed must arrive on the socket
            api_client.post(f"/api/v1/campaigns/{campaign_id}/start")
            queued = ws.receive_json()
            started = ws.receive_json()
            assert [queued["type"], started["type"]] == [
                "campaign.queued",
                "campaign.started",
            ]
            assert started["seq"] == queued["seq"] + 1
            assert queued["campaign_id"] == campaign_id

    def test_ws_unaffected_by_other_campaigns(self, api_client, campaign_id):
        other = api_client.post("/api/v1/campaigns", json={"name": "other"}).json()["id"]
        with api_client.websocket_connect(f"/ws/campaigns/{campaign_id}") as ws:
            api_client.post(f"/api/v1/campaigns/{other}/start")
            # nothing delivered for the unrelated campaign; only heartbeat
            first = ws.receive_text()
            assert first == "#hb"  # heartbeat arrives after 2s of silence


class TestFindingsAndAssets:
    def test_findings_assets_progress(self, api_client, campaign_id):
        from nighthawk.api.deps import get_campaign_service
        from nighthawk.models.core import Evidence, Finding, Severity

        api_client.post(f"/api/v1/campaigns/{campaign_id}/start")
        service = get_campaign_service()

        service.add_finding(
            uuid.UUID(campaign_id),
            Finding(
                title="Exposed admin panel",
                description="Admin panel reachable without authentication.",
                severity=Severity.HIGH,
                confidence=0.9,
                category="exposure",
                remediation="Require authentication.",
                evidence=[Evidence(description="HTTP 200 on /admin", source="web")],
            ),
        )

        findings = api_client.get(f"/api/v1/campaigns/{campaign_id}/findings").json()
        assert len(findings) == 1
        assert findings[0]["severity"] == "high"
        assert findings[0]["title"] == "Exposed admin panel"

        progress = api_client.get(f"/api/v1/campaigns/{campaign_id}/progress").json()
        assert progress["findings"] == 1
        assert progress["by_severity"]["high"] == 1
        assert progress["max_severity"] == "high"

        assets = api_client.get(f"/api/v1/campaigns/{campaign_id}/assets").json()
        assert assets == []

    def test_recorded_asset_survives_reconnect(self, api_client, campaign_id):
        """Second service instance (fresh session) sees persisted data."""
        from nighthawk.api.deps import get_campaign_service
        from nighthawk.models.core import Asset

        api_client.post(f"/api/v1/campaigns/{campaign_id}/start")
        service = get_campaign_service()
        service.add_asset(uuid.UUID(campaign_id), Asset(hostname="sub.example.com"))

        from nighthawk.api import deps

        deps.reset_services()  # forces a brand-new service/session
        assets = api_client.get(f"/api/v1/campaigns/{campaign_id}/assets").json()
        assert len(assets) == 1
        assert assets[0]["hostname"] == "sub.example.com"
