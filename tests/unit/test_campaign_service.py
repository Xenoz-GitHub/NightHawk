"""CampaignService lifecycle, persistence, and scope tests (temp database)."""

import uuid

import pytest

from nighthawk.core.exceptions import (
    CampaignNotFoundError,
    InvalidStateTransitionError,
    ScopeViolationError,
    DuplicateCampaignError,
)
from nighthawk.models.core import Asset, Evidence, Finding, Severity
from nighthawk.services import CampaignService


@pytest.fixture()
def service(tmp_path, monkeypatch):
    import nighthawk.config.config as config_mod
    from nighthawk.database import engine as db_engine_mod

    monkeypatch.setenv(
        "NIGHTHAWK_DATABASE_URL", f"sqlite:///{(tmp_path / 'svc.db').as_posix()}"
    )
    monkeypatch.setattr(config_mod, "_CONFIG_INSTANCE", None)
    db_engine_mod.reset_engine()
    yield CampaignService()
    db_engine_mod.reset_engine()


class TestLifecycle:
    def test_create_and_get_roundtrip(self, service):
        created = service.create("op-x", targets=["example.com"])
        fetched = service.get(created.id)
        assert fetched.name == "op-x"
        assert fetched.targets == ["example.com"]
        assert fetched.status.value == "created"
        assert fetched.event_seq == 1

    def test_duplicate_name_rejected(self, service):
        service.create("dupe")
        with pytest.raises(DuplicateCampaignError):
            service.create("dupe")

    def test_out_of_scope_target_rejected(self, service):
        with pytest.raises(ScopeViolationError):
            service.create("bad", targets=["evil.not-in-scope"])

    def test_full_lifecycle_sequence(self, service):
        c = service.create("seq-test")
        service.start(c.id)
        service.pause(c.id)
        service.resume(c.id)
        done = service.stop(c.id)
        assert done.status.value == "cancelled"
        assert done.completed_at is not None
        assert done.event_seq == 6

    def test_invalid_transition_raises(self, service):
        c = service.create("no-start-yet")
        with pytest.raises(InvalidStateTransitionError):
            service.pause(c.id)

    def test_restart_after_cancel_raises(self, service):
        c = service.create("once-only")
        service.start(c.id)
        service.stop(c.id)
        with pytest.raises(InvalidStateTransitionError):
            service.start(c.id)

    def test_get_unknown_raises(self, service):
        with pytest.raises(CampaignNotFoundError):
            service.get(uuid.uuid4())


class TestFindingsAndAssets:
    def test_record_finding_updates_progress(self, service):
        c = service.create("progress")
        service.start(c.id)
        finding = Finding(
            title="Open S3 bucket",
            description="Bucket allows anonymous read.",
            severity=Severity.MEDIUM,
            confidence=0.9,
            category="exposure",
            remediation="Restrict bucket permissions.",
            evidence=[Evidence(description="ListBucket allowed", source="aws-s3")],
        )
        service.add_finding(c.id, finding)
        progress = service.get_progress(c.id)
        assert progress["findings"] == 1
        assert progress["by_severity"]["medium"] == 1
        assert progress["max_severity"] == "medium"

    def test_record_asset_and_persistence(self, service):
        c = service.create("assets")
        service.start(c.id)
        service.add_asset(c.id, Asset(hostname="sub.example.com"))
        assert len(service.list_assets(c.id)) == 1
        # new instance, same database → persistence proof
        assert len(CampaignService().list_assets(c.id)) == 1

    def test_add_finding_requires_active_campaign(self, service):
        c = service.create("not-active")
        with pytest.raises(InvalidStateTransitionError):
            service.add_finding(
                c.id,
                Finding(
                    title="t",
                    description="d",
                    severity=Severity.LOW,
                    confidence=0.5,
                    category="misc",
                    remediation="n/a",
                ),
            )

    def test_list_findings_maps_evidence(self, service):
        c = service.create("evidence")
        service.start(c.id)
        service.add_finding(
            c.id,
            Finding(
                title="XSS",
                description="Reflected XSS in search.",
                severity=Severity.HIGH,
                confidence=0.95,
                category="injection",
                remediation="Encode output.",
                evidence=[
                    Evidence(description="Payload reflected", source="web", value="<script>x</script>")
                ],
            ),
        )
        findings = service.list_findings(c.id)
        assert findings[0].evidence[0].source == "web"
