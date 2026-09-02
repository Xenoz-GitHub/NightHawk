"""Regression guard: the simulation package must stay fully sandboxed.

The engine is an offline, deterministic tactical simulator. It must never
grow network I/O, database access, or web-framework imports — those belong
to the platform layers, not to a game module.
"""

import subprocess
import sys
from pathlib import Path

SIMULATION_DIR = (
    Path(__file__).resolve().parents[2] / "src" / "nighthawk" / "simulation"
)

FORBIDDEN = ("socket", "httpx", "requests", "urllib", "fastapi", "sqlalchemy")

# Modules that may appear in sys.modules transitively through standard-library
# imports but must never be imported *directly* by simulation code (guaranteed
# by the static source scan below). `urllib` is pure URL parsing pulled in by a
# stdlib chain; it performs no I/O by itself.
ALLOWED_TRANSITIVE = {"urllib"}

PROBE = """
import sys
for name in ("nighthawk", "nighthawk.simulation"):
    sys.modules.pop(name, None)
import nighthawk.simulation
leaked = sorted({
    name.split(".")[0] for name in sys.modules
    if name.split(".")[0] in {"socket", "httpx", "requests", "urllib", "fastapi", "sqlalchemy"}
})
print(leaked)
"""


class TestSandboxGuard:
    def test_no_forbidden_source_imports(self):
        assert SIMULATION_DIR.is_dir()
        offenders = []
        for path in SIMULATION_DIR.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in FORBIDDEN:
                if token in text:
                    offenders.append(f"{path.name}: {token}")
        assert offenders == []

    def test_no_forbidden_runtime_imports(self):
        result = subprocess.run(
            [sys.executable, "-c", PROBE],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, result.stderr
        leaked = set(eval(result.stdout.strip()))  # noqa: S307 - fixed probe output
        assert leaked <= ALLOWED_TRANSITIVE
