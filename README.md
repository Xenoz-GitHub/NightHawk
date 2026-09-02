# NIGHTHAWK

**Ethical Red-Team Reconnaissance, Attack-Surface Discovery, and Exposure-Assessment Platform**

> Strictly intended for systems owned by the user, isolated cybersecurity labs, CTF environments, explicitly authorized penetration tests, and security research environments.

## Quick Start (Global CLI)

```bash
# Install globally (like npm i -g opencode-ai)
pip install .
# or with pipx (recommended)
pipx install .

# Verify
nighthawk --version

# Define scope
nighthawk scope --file scope.yaml

# Assess
nighthawk web https://lab.example
nighthawk secrets ./repo
nighthawk assess --scope scope.yaml
```

## Architecture

- Python 3.11+ (core), FastAPI (API), React + TypeScript (dashboard)
- Async by default (`asyncio`, `httpx`)
- Pydantic v2 models, SQLAlchemy database, Alembic migrations
- NetworkX attack-surface graph, data-driven fingerprint engine
- Plugin protocol for scanner extensibility

## Key Modules

- **Scope Management**: Mandatory authorization enforcement
- **Network Scanner**: Async service fingerprinting
- **Web Scanner**: TLS, headers, cookies, redirects, robots/sitemap
- **Technology Fingerprinting**: YAML-based confidence scoring
- **Secret Scanner**: Regex + entropy + context, with redaction
- **Windows/Linux Collectors**: Read-only platform telemetry
- **Correlation Engine**: Relationship mapping between findings
- **Risk Engine**: Transparent scoring with explanation
- **Reporting**: JSON, HTML (Jinja2), CSV, PDF

## Security Boundaries

- No malware, ransomware, credential theft, persistence malware, covert surveillance, destructive actions, unauthorized exploitation, or evasion mechanisms.
- Every scanner checks scope before execution.
- Default redaction for secrets in logs and reports.
- Least-privilege design with safe defaults.

## Development

```bash
make install
make lint
make test
make format
make build
```

## Documentation

- `docs/architecture.md`
- `docs/cli.md`
- `docs/plugins.md`
- `docs/security.md`
- `docs/detection.md`

## License

MIT — See `LICENSE`.
