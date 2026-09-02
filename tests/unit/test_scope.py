import pytest
from nighthawk.scope.manager import ScopeManager
from nighthawk.core.exceptions import ScopeViolationError, ConfigurationError


def test_scope_load_missing(tmp_path):
    with pytest.raises(ConfigurationError):
        ScopeManager(tmp_path / "nonexistent.yaml")


def test_scope_authorized_domain(tmp_path):
    scope_file = tmp_path / "scope.yaml"
    scope_file.write_text("name: test\ndomains:\n  - example.com\n")
    manager = ScopeManager(str(scope_file))
    assert manager.is_authorized("example.com")
    assert not manager.is_authorized("other.com")


def test_scope_violation_raises(tmp_path):
    scope_file = tmp_path / "scope.yaml"
    scope_file.write_text("name: test\n")
    manager = ScopeManager(str(scope_file))
    with pytest.raises(ScopeViolationError):
        manager.validate_target("unauthorized.host")
