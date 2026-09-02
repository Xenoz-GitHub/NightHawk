#!/bin/bash
# NIGHTHAWK Global Install Script
# Works on Linux/macOS/Windows (Git Bash / WSL)
# Usage: curl -sSL https://raw.githubusercontent.com/Xenoz-GitHub/NightHawk/main/install.sh | bash
# Or: bash install.sh

set -euo pipefail

REPO_URL="https://github.com/Xenoz-GitHub/NightHawk.git"

echo "[NIGHTHAWK] Installing globally..."

# Try pipx first (best practice for CLI tools)
if command -v pipx &>/dev/null; then
    echo "[NIGHTHAWK] Installing with pipx from GitHub..."
    pipx install "git+${REPO_URL}"
else
    echo "[NIGHTHAWK] Installing with pip from GitHub..."
    pip install --user "git+${REPO_URL}"
fi

echo "[NIGHTHAWK] Installation complete."
echo "[NIGHTHAWK] Run: nighthawk --version"
echo "[NIGHTHAWK] Verify: nighthawk scope --file scope.yaml"
