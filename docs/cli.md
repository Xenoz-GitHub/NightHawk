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
