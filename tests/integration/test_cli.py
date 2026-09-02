from typer.testing import CliRunner
from nighthawk.cli.main import app


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(app, ["--version", "scope"])
    assert result.exit_code == 0
    assert "NIGHTHAWK" in result.output or "scope" in result.output
