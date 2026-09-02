# NIGHTHAWK Implementation Plan

> Produced by the PHASE 0 audit. Every item references files that exist in this
> repository. Phases map to the 8-phase roadmap in the task brief.

## Guiding constraints

1. Do not rewrite working scanners (`web/`, `network/`, `dns/`, `secrets/`,
   `technology/` scanners stay as-is; only wiring around them changes).
2. One canonical model set: Pydantic `models/core.py` for the domain,
   `database/models.py` for rows, mappers between them — nothing else.
3. No real exploit execution anywhere. The simulation engine is a separate,
   offline, synthetic game engine.
4. Scope enforcement is server-side; no bypass flag exists in the API.

## PHASE 0 — Repository audit (this document + docs/architecture.md)

Status: **complete**. Baseline established; test suite found broken at
`cli/main.py:1489` (orphaned code block → IndentationError on import).

## PHASE 1 — Backend service layer + persistence + real API

### Existing files to modify
| File | Change |
|---|---|
| `src/nighthawk/database/models.py` | Add `CampaignDB.status` lifecycle states, `CampaignDB.targets` (JSON), `CampaignDB.error`; add `AssetDB.campaign_id` FK + `asset_id` on `FindingDB` kept as UUID string ↔ `AssetDB.id`; add `EvidenceDB` table (finding_id FK, description, source, value, timestamp). |
| `src/nighthawk/database/engine.py` | Add `create_all()` bootstrap + `reset_engine()` for tests; keep engine/session factory pattern. |
| `src/nighthawk/api/app.py` | Replace all placeholder handlers with calls into the new service layer; add structured error handlers; keep `/health`. |
| `src/nighthawk/orchestrator/campaign.py` | Extend `AssessmentCampaign` into a persisted lifecycle runner (created→queued→running→paused→completed/failed/cancelled) driven by `CampaignService`. |
| `src/nighthawk/models/core.py` | Add `CampaignStatus` enum, `Campaign` model, `SimulationEvent`-agnostic `EventBase` fields (type, campaign_id, timestamp, seq, payload). Keep all existing models unchanged. |
| `src/nighthawk/cli/main.py` | Fix the L1489 corruption (unblocks the whole suite); route `assess` through `CampaignService` so CLI campaigns persist too. |
| `pyproject.toml` | Add `pytest-asyncio` (already installed ad hoc) to `dev` extras. |

### New modules
| Module | Responsibility |
|---|---|
| `src/nighthawk/services/__init__.py` | Service package. |
| `src/nighthawk/services/campaign_service.py` | Lifecycle state machine, target resolution, scope validation on create/start, persistence of campaigns. |
| `src/nighthawk/services/runner.py` | Executes scanners for a running campaign, normalizes results into `Finding`/`Asset`, writes `scan_results` rows, emits events. |
| `src/nighthawk/services/mappers.py` | `FindingDB ↔ Finding`, `AssetDB ↔ Asset`, `CampaignDB ↔ Campaign` converters (single mapping location). |
| `src/nighthawk/api/schemas.py` | Request/response Pydantic schemas + `ErrorResponse` envelope (structured errors). |
| `src/nighthawk/api/errors.py` | Exception → HTTP mapping (`ScopeViolationError` → 403, not-found → 404, validation → 422/400). |
| `src/nighthawk/api/deps.py` | DI: session, services, scope manager; single campaign registry keyed by id. |
| `src/nighthawk/events/__init__.py` | Event package. |
| `src/nighthawk/events/models.py` | Normalized event model (types: campaign.lifecycle, discovery, finding, graph, error, completion). |
| `src/nighthawk/events/hub.py` | In-process pub/sub hub + asyncio queues per subscriber. |
| `tests/unit/test_campaign_service.py` | Lifecycle transitions, scope rejection, persistence. |
| `tests/unit/test_api_campaigns.py` | Every lifecycle endpoint, success + failure. |
| `tests/unit/test_events.py` | Event ordering, serialization, hub fan-out. |
| `tests/conftest.py` | Shared fixtures: in-memory SQLite session, seeded scope files, API client. |

### Endpoint contract (v1)
- `POST /api/v1/campaigns` → create (validates scope server-side, status `created`)
- `GET /api/v1/campaigns/{id}` → persisted campaign (404 if unknown — no fabrication)
- `POST /api/v1/campaigns/{id}/start|pause|resume|stop` → state transitions (409 on illegal)
- `GET /api/v1/campaigns/{id}/findings` → persisted findings
- `GET /api/v1/campaigns/{id}/assets` → persisted assets
- `GET /api/v1/campaigns/{id}/graph` → graph built from persisted assets/findings
- `WS /api/v1/campaigns/{id}/events` → normalized event stream
- `GET /api/v1/graph` → graph across all campaigns (kept for compatibility)

## PHASE 2 — Event model + WebSocket

- `events/models.py` + `events/hub.py` (created in Phase 1) finalized:
  sequence numbers per campaign, monotonic; JSON-safe payloads.
- `src/nighthawk/api/ws.py` (new): WebSocket endpoint with per-campaign
  subscription, subscriber registry with cleanup on disconnect.
- Runner emits: `campaign.created/queued/started/paused/resumed/stopped/
  completed/failed/cancelled`, `discovery.asset`, `finding.created`,
  `graph.updated`, `scan.error`, `campaign.progress`.
- Tests: `tests/unit/test_ws.py` — subscribe, receive lifecycle + finding events,
  ordering, disconnect cleanup, reconnect replays nothing (sequence numbers let
  the client detect gaps).

## PHASE 3 — Real graph + real dashboard data

- `src/nighthawk/graph/builder.py` (new): builds `AttackSurfaceGraph` from
  persisted `AssetDB` + `FindingDB` rows (asset nodes, service nodes,
  technology nodes, finding nodes; edges: has_service, runs, affects).
- `graph/graph.py` stays as the storage structure; add `to_cytoscape_json()`.
- Correlation (`correlation/engine.py`) and scoring (`analysis/scoring.py`) are
  wired in: findings get risk scores; correlation groups become graph edges.
- Frontend contract: `GET /api/v1/campaigns/{id}/graph` returns
  `{nodes: [{id, label, type, data}], edges: [{source, target, relationship}]}`.

## PHASE 4 — Sandboxed simulation engine

New package `src/nighthawk/simulation/` — **zero network I/O, zero DB, zero
FastAPI imports** (enforced by a test that asserts the import graph).

| Module | Responsibility |
|---|---|
| `simulation/models.py` | `InformationState` enum (UNKNOWN/OBSERVED/PROBABLE/CONFIRMED), `SimHost`, `SimService`, `SimIdentity`, `SimVulnerability`, `SimCredential` (synthetic game object), `SimNetworkLink`, `DefensiveControl`, `SimAlert`, `Objective`, `WorldState`, `SimulationEvent`. |
| `simulation/world.py` | World container: hosts, services, technologies, identities, vulnerabilities, synthetic credentials, network relationships, defensive controls, alerts, objectives. Snapshot/restore, fully serializable. |
| `simulation/scenario.py` | Deterministic scenario definitions + generator (small office, SaaS company, university, healthcare lab, industrial test environment, cloud startup). Seeded `random.Random(seed)` for all generation. |
| `simulation/actions.py` | Action catalogue: `discover`, `inspect`, `enumerate`, `fingerprint`, `analyze`, `collect_evidence`, `move_to`, `investigate`, `contain`, `monitor`. Validation of applicability + cost; no real network ops. |
| `simulation/engine.py` | Deterministic tick engine: `SimClock`, seeded RNG, `submit_action`, `step()`, pause/resume, replay from seed + action log, invalid actions rejected without state mutation. |
| `simulation/events.py` | Event log (append-only), filters, replay driver. |
| `simulation/scoring.py` | Deterministic score from objectives, intel quality, evidence quality, time, detection, operational risk. |
| `simulation/objectives.py` | Objective evaluation (success/failure, progress). |
| `simulation/agents/__init__.py` | Agents package. |
| `simulation/agents/attacker.py` | Player-side action broker (validates and applies player actions). |
| `simulation/agents/defender.py` | Defender AI: passive monitoring, alert escalation, investigation, containment, patching, logging changes, service isolation, recovery — all as world-state mutations + events. |

Acceptance: same seed + same action sequence ⇒ identical state hash + event log;
runs offline; snapshots round-trip; invalid actions raise without mutating.

## PHASE 5 — Attacker/defender AI depth

- Defender reaction chains with detection probability curves per action ×
  defensive control; confidence changes (OBSERVED→PROBABLE→CONFIRMED) and decay
  over simulation ticks.
- Fog of war: world entities hidden until observed; visibility per host/service.
- `agents/defender.py` difficulty presets: Recruit, Analyst, Operator,
  Specialist, Black Ice, Nighthawk.

## PHASE 6 — Missions + scoring + replay UX concepts

- `simulation/missions.py` (new): briefing, primary/secondary/optional
  objectives, constraints, time limits.
- Scenario packs (6 archetypes above) with deterministic variants
  (seed-derived layout, severity mix, defender skill).
- Replay primitives in the engine: pause, step, jump-to-event, restart from
  seed. Speed multipliers (1x/2x/4x) are a client presentation concern.
- Tests: scoring determinism, objective resolution, defender reactions,
  full deterministic replay.

## PHASE 7 — Workstation UI (frontend)

Rebuild `frontend/` with a real toolchain:
- `package.json` (React + Vite + TypeScript; dev deps: vitest + testing-library).
- Local Tailwind (no CDN): `tailwind.config.js` + `postcss.config.js`; keep the
  existing palette (ink/surface/panel/cyan/emerald/amber/crimson/lavender).
- Views: `OPERATIONS` (campaigns, severity distribution, event stream),
  `TOPOLOGY` (interactive graph from `/graph`), `TERMINAL` (simulation
  terminal: history, autocomplete, keyboard nav), `INTELLIGENCE` (findings,
  evidence, confidence, remediation, timeline), `SIMULATION` (mission briefing,
  objectives, defender activity, score, detection, sim clock), `TIMELINE`
  (filterable live event stream).
- `src/api/client.ts` + `src/api/ws.ts`: typed REST client + WebSocket client
  with reconnect/backoff and sequence-gap detection.
- States for loading / empty / error / disconnected / reconnecting / completed.
- No mock data anywhere; empty states reflect genuinely empty databases.
- Tests: campaign loading, realtime events, graph rendering, terminal commands,
  simulation updates, error handling.

## PHASE 8 — Testing + hardening + deployment

- Fix `docker/Dockerfile` invalid `|| true` line; pin non-root user.
- Fix `docker-compose.yml`: env prefix (`NIGHTHAWK_DATABASE_URL`), healthchecks,
  `depends_on: condition: service_healthy`, remove host port publish for
  postgres by default, credentials via `.env`.
- API security: optional bearer-token auth (env-configured), CORS allow-list,
  structured error envelope, no stack traces in responses.
- Full suite green; coverage report; `make test`/`make lint` pass.

## Concrete file list (machine-checkable)

### Modified
```
src/nighthawk/api/app.py
src/nighthawk/cli/main.py
src/nighthawk/database/engine.py
src/nighthawk/database/models.py
src/nighthawk/models/core.py
src/nighthawk/orchestrator/campaign.py
pyproject.toml
docker/Dockerfile
docker-compose.yml
```

### Created (backend)
```
src/nighthawk/services/__init__.py
src/nighthawk/services/campaign_service.py
src/nighthawk/services/runner.py
src/nighthawk/services/mappers.py
src/nighthawk/api/schemas.py
src/nighthawk/api/errors.py
src/nighthawk/api/deps.py
src/nighthawk/api/ws.py
src/nighthawk/events/__init__.py
src/nighthawk/events/models.py
src/nighthawk/events/hub.py
src/nighthawk/graph/builder.py
```

### Created (simulation, later phases)
```
src/nighthawk/simulation/__init__.py
src/nighthawk/simulation/engine.py
src/nighthawk/simulation/models.py
src/nighthawk/simulation/scenario.py
src/nighthawk/simulation/events.py
src/nighthawk/simulation/world.py
src/nighthawk/simulation/actions.py
src/nighthawk/simulation/scoring.py
src/nighthawk/simulation/objectives.py
src/nighthawk/simulation/missions.py
src/nighthawk/simulation/agents/__init__.py
src/nighthawk/simulation/agents/attacker.py
src/nighthawk/simulation/agents/defender.py
```

### Created (tests)
```
tests/conftest.py
tests/unit/test_campaign_service.py
tests/unit/test_api_campaigns.py
tests/unit/test_events.py
tests/unit/test_ws.py
tests/unit/test_graph_builder.py
tests/unit/test_simulation_engine.py
tests/unit/test_simulation_determinism.py
tests/unit/test_simulation_scoring.py
tests/unit/test_simulation_defender.py
```

## Test strategy

1. **Unit** — services with in-memory SQLite (transactional fixtures); pure
   functions (scoring, mappers, scope matching) tested directly.
2. **API** — FastAPI `TestClient` against the real app + test DB; every
   lifecycle endpoint tested for success, 404, 409, and scope-rejection (403).
3. **Events/WS** — hub fan-out determinism, ordering, disconnect cleanup;
   WS endpoint integration via TestClient websocket session.
4. **Simulation** — determinism (state hash + event log equality across two
   runs), snapshot round-trip, invalid-action immunity, objective resolution,
   defender reaction, scoring reproducibility. No I/O, no asyncio required.
5. **Contract** — response schema assertions against `api/schemas.py` models.
6. **Regression guard** — a test asserting the simulation package never imports
   `socket`, `httpx`, `fastapi`, or `sqlalchemy`.


