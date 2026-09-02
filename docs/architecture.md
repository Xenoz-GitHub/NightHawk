# NIGHTHAWK Architecture

## Design Principles

- Security-first: Every operation respects explicit scope.
- Evidence-first: Findings include evidence, confidence, and reasoning.
- Async by default: Network scanners use `asyncio`.
- Modular: Plugins can be added without rewriting core.
- Cross-platform: Windows and Linux use native mechanisms normalized to common models.
- Redaction: Secrets are never exposed in full in logs or reports by default.

## Module Dependencies

```
CLI / API
    ↓
Scope Manager (enforces authorization boundary)
    ↓
Orchestrator (campaign management)
    ↓
Plugin Registry → Scanner Plugins (network, web, technology, secrets, windows, linux)
    ↓
Event Normalization → Finding Model → Evidence
    ↓
Correlation Engine → Graph Engine → Risk Engine
    ↓
Reporting (JSON, HTML, CSV, PDF) / Dashboard
```

## Database Schema (SQLAlchemy)

- `campaigns`: Assessment campaigns
- `findings`: Security observations
- `assets`: Discovered hosts
- `scan_results`: Raw scanner outputs

Migrations are managed with Alembic.

## Safety Mechanisms

- `ScopeViolationError` is raised for out-of-scope targets.
- Rate limiting is enforced via configuration.
- Sensitive values are redacted by default.
- No destructive actions are implemented.
