# NIGHTHAWK Architecture (verified against encrypted-crew-v2 @ a177cf0)

> This document reflects the **actual** repository state, not the aspirational
> design. Every claim below was verified by reading the source tree.

## 1. Current architecture map

```
CLI (src/nighthawk/cli/main.py — 1534 lines, Typer + Rich)
 ├── scope command        → ScopeManager (create / show / edit / quick-add)
 ├── discover command     → NetworkScanner.run(target, scope_manager=...)     [real logic]
 ├── web command          → WebScanner.run(target, scope_manager=...)         [real logic]
 ├── secrets command      → SecretScanner.run(target, scope_manager=...)      [real logic]
 ├── assess command       → AssessmentCampaign + WebScanner + NetworkScanner  [real logic]
 ├── report command       → ReportGenerator                                   [hardcoded empty findings]
 ├── repair command       → git+https self-reinstall (subprocess)
 └── game_* commands      → nighthawk.game (RPG system, separate concern)
        │
        ▼
Scope layer (src/nighthawk/scope/manager.py)
 ├── ScopeManager         loads ScopeConfig from YAML, validates targets
 │                        (IP/CIDR/URL/domain matching, wildcard subdomains)
 └── AuthorizationBoundary  scope + module authorization wrapper
        │
        ▼
Orchestrator (src/nighthawk/orchestrator/campaign.py)
 └── AssessmentCampaign   in-memory only: run_scan() → results list, complete()
        │
        ▼
Scanners (all accept optional ScopeManager and self-validate targets)
 ├── web/scanner.py         WebScanner        httpx GET, security headers, TLS, robots
 ├── network/scanner.py     NetworkScanner    async TCP/HTTP probe of common ports
 ├── dns/scanner.py         DNSIntelligence   A/AAAA/CNAME/MX/NS/TXT/SOA via dnspython
 ├── secrets/scanner.py     SecretScanner     regex + entropy secret detection (rules/)
 ├── technology/scanner.py  FingerprintEngine data-driven fingerprints (fingerprints/)
 ├── linux/collector.py     LinuxHostCollector  platform telemetry  (unused)
 └── windows/collector.py   WindowsHostCollector platform telemetry (unused)
        │
        ▼
Models (src/nighthawk/models/core.py — Pydantic v2, the canonical domain models)
 ├── Severity, ConfidenceLevel, Evidence, Finding, Asset,
 │   ServiceInfo, TechnologyMatch, NetworkScanResult, ScopeConfig
        │
        ▼  (NO mapping layer exists between these and the ORM)
Persistence (src/nighthawk/database/)
 ├── engine.py   global SQLAlchemy engine/session factory from NightHawkConfig
 │               ⚠ never invoked by CLI or API; no create_all, no Alembic
 └── models.py   CampaignDB, FindingDB, AssetDB, ScanResultDB (ORM)
        │
        ▼
API (src/nighthawk/api/app.py — 74 lines)  ⚠ 100% PLACEHOLDER
 ├── GET  /health                     real
 ├── POST /api/v1/campaigns           returns random UUID, persists nothing
 ├── GET  /api/v1/campaigns/{id}      returns hardcoded {"status": "running", ...}
 ├── GET  /api/v1/findings            returns []
 ├── GET  /api/v1/assets              returns []
 └── GET  /api/v1/graph               returns {"nodes": [], "edges": []}
        │
        ▼
Analysis (all currently dead code — defined but never called)
 ├── graph/graph.py         AttackSurfaceGraph (NetworkX DiGraph wrapper)
 ├── correlation/engine.py  CorrelationEngine
 └── analysis/scoring.py    RiskEngine
        │
        ▼
Frontend (frontend/ — no package.json, no build toolchain, no tests)
 └── App.tsx  ⚠ hardcoded MOCK findings/assets; Tailwind + Chart.js via CDN;
              Tailwind classes reference a custom palette defined only in index.html;
              "Attack Surface Graph" panel is a decorative placeholder.
```

### Event flow (current)

**None.** There is no event model, no event bus, no WebSocket/SSE transport.
Logging is structlog JSON to stdout only. The frontend has no realtime input.

## 2. Audit findings

### 2.1 Mock data
| Location | Problem |
|---|---|
| `frontend/src/App.tsx` L13-23 | `setFindings([...])` / `setAssets([...])` hardcoded demo data |
| `frontend/src/App.tsx` L107-111 | "Graph Visualization" decorative placeholder card |
| `frontend/src/App.tsx` L149-157 | hardcoded campaign status "Running", scope "lab.example" |

### 2.2 Placeholder APIs
| Endpoint | Evidence |
|---|---|
| `POST /api/v1/campaigns` | `app.py` L41-49: returns `str(uuid4())`, no persistence |
| `GET /api/v1/campaigns/{id}` | `app.py` L52-59: hardcoded `"status": "running"` |
| `GET /api/v1/findings` | `app.py` L62-64: `return []` |
| `GET /api/v1/assets` | `app.py` L67-69: `return []` |
| `GET /api/v1/graph` | `app.py` L72-74: `{"nodes": [], "edges": []}` |

### 2.3 Dead code (defined, never referenced anywhere)
- `analysis/scoring.py::RiskEngine`
- `correlation/engine.py::CorrelationEngine`
- `graph/graph.py::AttackSurfaceGraph`
- `plugins/protocol.py::PluginRegistry` / `REGISTRY` (no scanner registers itself)
- `database/models.py::ScanResultDB` (no writer, no reader)
- `scope/manager.py::AuthorizationBoundary` (nothing calls `enforce`)
- `linux/collector.py`, `windows/collector.py` (not wired into CLI or API)

### 2.4 Duplicated models / competing representations
- Pydantic `Finding`/`Asset` (models/core.py) vs SQLAlchemy `FindingDB`/`AssetDB`
  (database/models.py) with **no mapping layer** — fields drift already
  (`FindingDB` has no evidence column; `AssetDB` has no campaign FK).
- Two config singletons with the same accessor name `get_config()`:
  `config/config.py` (env-based `NightHawkConfig`) and `config/user_config.py`
  (JSON-file `ConfigManager`) — different types, same accessor name.
- Duplicate imports inside single files:
  `secrets/scanner.py` L13+L33 and `technology/scanner.py` L15 import
  `nighthawk.utils.paths` twice.

### 2.5 Advertised but incompletely integrated modules
- **Plugin registry** — `docs/plugins.md` documents `REGISTRY.register(...)`;
  no scanner registers itself and nothing iterates the registry.
- **Alembic migrations** — `docs/architecture.md` claimed "Migrations are managed
  with Alembic"; there is no `alembic.ini`, no `migrations/` directory, and no
  `Base.metadata.create_all` anywhere.
- **Report from campaign** — CLI `report` command contains
  `findings = []  # In production, load from DB for campaign`.
- **`ScanResultDB`** — table exists in schema docs; nothing writes or reads it.
- **Campaign status machine** — orchestrator only knows `running`/`completed`;
  created/queued/paused/failed/cancelled do not exist.


### 2.6 Missing persistence
- The database session factory is never called by any runtime path (CLI or API).
  Scan results, findings, assets, and campaigns all evaporate when a process ends.
- No schema creation mechanism (no create_all, no migrations).
- `AssetDB` rows cannot be associated with a campaign (no FK).

### 2.7 Missing realtime event transport
- No WebSocket endpoint, no SSE, no pub/sub. The frontend polls nothing; it
  renders static mocks. Campaign progress inside `AssessmentCampaign.run_scan`
  is invisible to any other consumer.

### 2.8 Missing frontend/backend contracts
- No `package.json` → no build, no dev server deps, no test runner, no lint.
  `vite.config.ts` and `App.tsx` exist but the project cannot build.
- Frontend expects types like `Finding {title, severity, category, confidence}`
  that are never generated or validated against the API.
- `docker-compose.yml` mounts `./frontend/build` into nginx; Vite outputs
  `frontend/dist` — the dashboard container currently serves nothing.

### 2.9 Authorization weaknesses
1. **Repo-root `scope.yaml` authorizes entire TLDs** — `domains: [com, net, org,
   io, app, ...]` combined with `ScopeManager._domain_is_authorized`
   (`host.endswith("." + allowed)`) means **every .com/.net/.org/.io/... domain
   on the internet is in scope by default**. This is the most dangerous defect
   in the repository.
2. **`--skip-scope` flag** on `discover`, `web`, and `secrets` CLI commands
   bypasses validation entirely. The CLI may keep an interactive UX, but the
   API must never offer an equivalent.
3. **API has no scope enforcement** because it has no execution at all; when it
   gains one, target validation must be server-side and mandatory.
4. **No authentication on the API** (acceptable for localhost dev, but must be a
   deliberate, documented decision with a token option for remote use).
5. `_check_ip_scope` treats any overlapping CIDR as authorized — a broad scope
   entry plus a broad target could pass.
6. Unstructured errors; `GET /api/v1/campaigns/{id}` returns 200 with fabricated
   data for unknown IDs.

### 2.10 Test coverage gaps
- The suite currently **cannot be collected**: `cli/main.py` L1489 contains an
  orphaned `engine.save_game(slot=1)` block after `game_clients` returns
  (IndentationError breaks `nighthawk.cli.main` import and every dependent test).
- No tests for: API endpoints, persistence, orchestrator, graph, scoring,
  reporting, event model. Existing tests cover scope matching (5), entropy and
  fingerprint loading (4), CLI version smoke (1), and the game engine (44).
- No in-memory SQLite fixtures; no contract tests for API schemas.

### 2.11 Additional defects found (deployment / hygiene)
- `docker/Dockerfile` L25: `COPY scope.yaml /app/scope.yaml || true` — invalid
  Dockerfile syntax (`|| true` is shell, not Dockerfile).
- `docker-compose.yml`: hardcoded dev credentials (`nighthawk:nighthawk`),
  port 5432 published to host, no healthchecks, `depends_on` without
  `condition: service_healthy`, deprecated `version:` key.
- `docker-compose.yml` sets `DATABASE_URL=` but `NightHawkConfig` expects the
  `NIGHTHAWK_` prefix (`NIGHTHAWK_DATABASE_URL`) — the compose DB URL is
  silently ignored.

## 3. Target architecture (phased)

```
                         ┌──────────────────────────────────────────┐
                         │              Frontend (React)            │
                         │  Operations / Topology / Terminal /      │
                         │  Intelligence / Simulation / Timeline    │
                         └───────▲──────────────────────▲───────────┘
                        REST /ws │                      │ REST
                         ┌───────┴──────────────────────┴───────────┐
                         │              FastAPI API                 │
                         │  routes → services (service layer)       │
                         │  structured errors · CORS · WS hub       │
                         └───────▲──────────────────────▲───────────┘
                                 │                      │
                    ┌────────────┴─────────┐  ┌─────────┴──────────────┐
                    │   CampaignService    │  │  SimulationService     │
                    │  lifecycle state     │  │  (sandboxed engine)    │
                    │  machine + runner    │  │  only consumes events  │
                    └───▲──────────▲───────┘  └─────────▲──────────────┘
                        │          │                    │
              normalize │          │ persist            │ pure in-memory
              findings  │          │ campaigns/         │ world+events+seed
              /assets   │          │ findings/assets/   │
                        │          │ scan_results/events│
        ┌───────────────┴──┐   ┌───┴────────────┐   ┌───┴────────────────┐
        │ Scanner modules  │   │ Persistence    │   │ src/nighthawk/     │
        │ (unchanged logic)│   │ SQLAlchemy +   │   │ simulation/        │
        │ + PluginRegistry │   │ Alembic        │   │ engine/world/...   │
        └────────▲─────────┘   └────────────────┘   └────────────────────┘
                 │ always validated against
        ┌────────┴─────────┐
        │ ScopeManager     │  (server-side; no bypass flag in API)
        └──────────────────┘
```

Key decisions:
1. **Single set of domain models.** Pydantic `models/core.py` stays canonical.
   SQLAlchemy rows in `database/models.py`; mapping helpers convert ORM↔domain.
   No third representation is introduced.
2. **Service layer owns lifecycle.** `CampaignService` is the only writer of
   campaign state; API routes and CLI both call it.
3. **Event model is normalized and shared.** `events/models.py` defines typed
   events with sequence numbers; an in-process hub fans out to WebSocket.
4. **Scope validation is server-side and mandatory** for any API-initiated
   target. The CLI keeps its interactive UX but uses the same `ScopeManager`.
5. **Simulation is a separate package** (`src/nighthawk/simulation/`) with zero
   network I/O, zero DB dependency, zero FastAPI import — importable and testable
   standalone, deterministic under a fixed seed.

## 4. Safety posture

- No exploit execution exists or will be added. Scanners are observational only
  (HTTP GET, DNS queries, TCP connect probes, local file regex scans, local
  platform telemetry).
- Simulation actions are game moves on synthetic objects; they never produce
  network traffic (the engine has no sockets, no httpx, no DNS imports).
- Scope rejection is fail-closed: unknown/empty scope ⇒ nothing is authorized.

- `frontend/index.html` loads Tailwind/Chart.js from CDNs at runtime (fails
  offline and in production; no vendored build).
- `Makefile` targets `python3.12`; `pyproject.toml` declares `>=3.11`.
- `pyproject.toml` sets `asyncio_mode = "auto"` but `pytest-asyncio` was not
  installed in the dev environment (installed during this audit).



