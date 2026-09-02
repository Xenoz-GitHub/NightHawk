# Global CLI Installation

NIGHTHAWK installs globally — users never need to clone the repo or stay in the source folder.

## From GitHub (any computer, any folder — no clone needed)

```bash
# Using the tag (recommended for stable installs)
pip install git+https://github.com/Xenoz-GitHub/NightHawk.git@v1.0.0

# Or using the branch directly
pip install git+https://github.com/Xenoz-GitHub/NightHawk.git@arena/01a05f4e-nighthawk

# Or with pipx (isolated CLI, best practice)
pipx install git+https://github.com/Xenoz-GitHub/NightHawk.git@v1.0.0
```

**Note for Windows users:** If `pip install .` says "Neither 'setup.py' nor 'pyproject.toml' found", you are in the wrong folder. Use the GitHub URL above, or clone first:

```cmd
git clone https://github.com/Xenoz-GitHub/NightHawk.git
pip install .\NightHawk

After install, `nighthawk` works from any directory:
```bash
nighthawk --version
nighthawk scope --file ~/scope.yaml
```

## From local repo (developing / testing)

```bash
cd NightHawk
pip install .
```

## Windows users

If `pip install .` fails with "Neither 'setup.py' nor 'pyproject.toml' found", you are NOT in the repo folder. Either:

```cmd
# Option 1: Clone first, then install
cd C:\Users\John Lloyd
mkdir nighthawk_install
cd nighthawk_install
git clone https://github.com/Xenoz-GitHub/NightHawk.git
pip install .\NightHawk

# Option 2: Install directly from GitHub
pip install git+https://github.com/Xenoz-GitHub/NightHawk.git
```

## After install

```bash
nighthawk --version
nighthawk scope --file scope.yaml
nighthawk web https://lab.example
```

The `nighthawk` binary is installed to your Python environment's `Scripts/` or `bin/` folder and is available globally, just like `npm i -g opencode-ai` creates `opencode`.
