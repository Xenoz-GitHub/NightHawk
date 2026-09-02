"""CORS allow-list: middleware attached only when origins are configured."""


def _handle_tests_cors(monkeypatch, origins: str):
    monkeypatch.setenv("NIGHTHAWK_CORS_ORIGINS", origins)

    import nighthawk.config.config as config_mod

    monkeypatch.setattr(config_mod, "_CONFIG_INSTANCE", None)

    from nighthawk.api.app import create_app

    return create_app()


class TestCors:
    def test_middleware_attached_when_configured(self, monkeypatch):
        app = _handle_tests_cors(
            monkeypatch, "https://app.example.com,http://localhost:3000"
        )
        names = {m.cls.__name__ for m in app.user_middleware if m.cls}
        assert "CORSMiddleware" in names

    def test_no_middleware_when_empty(self, monkeypatch):
        app = _handle_tests_cors(monkeypatch, "")
        names = {m.cls.__name__ for m in app.user_middleware if m.cls}
        assert "CORSMiddleware" not in names