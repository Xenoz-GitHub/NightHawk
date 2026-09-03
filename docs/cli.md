# Global CLI Installation (like `npm i -g opencode-ai`)

NIGHTHAWK installs as a global CLI command: `nighthawk`.

## Option 1: pipx (recommended for CLI tools)

```bash
pipx install .
# or from repo
pipx install git+https://github.com/Xenoz-GitHub/NightHawk.git
```

After this, `nighthawk` works from any directory, just like `opencode`.

## Option 2: pip (global/user)

```bash
pip install --user .
# Add to PATH if needed:
export PATH="$HOME/.local/bin:$PATH"
```

## Option 3: Docker (global container)

```bash
docker-compose up -d
# CLI runs inside container
```

## Usage after global install

```bash
nighthawk --version
nighthawk scope --file ~/projects/lab/scope.yaml
nighthawk web https://lab.example
nighthawk secrets ~/projects/repo
nighthawk assess --scope ~/projects/lab/scope.yaml
```

The `nighthawk` binary is installed via `pyproject.toml` scripts (`project.scripts`).

## Authorized Red-Team Planning

NIGHTHAWK can create auditable red-team plans without performing network
actions. Simulation is the default mode. Validation and authorized-active
modes require an approval reference, and authorized-active also requires
explicit targets.

```bash
# Show supported objectives
nighthawk redteam objectives

# Preview a deterministic attack path (planning only)
nighthawk redteam plan initial-access

# Create a local simulation mission
nighthawk redteam mission-create "API access review" \
	--objective initial-access \
	--mode simulation \
	--output .nighthawk/missions/api-review.json

# Create an approved active assessment definition
nighthawk redteam mission-create "Approved perimeter test" \
	--objective recon \
	--mode authorized-active \
	--target example.com \
	--authorization-ref ROE-2026-014
```

These commands define and document work; they do not bypass scope controls or
turn the planner into an exploitation tool. Live assessment commands continue
to enforce the configured authorization scope.

## Simulation Rules

The offline simulation uses a three-point action budget for each side on every
turn. Reconnaissance and inspection can be combined; analysis, evidence
collection, containment, and other costly actions consume more of the budget.
Unused points do not carry over. Detection evaluates every attacker action in
the turn, and undo restores the exact action-point state.
