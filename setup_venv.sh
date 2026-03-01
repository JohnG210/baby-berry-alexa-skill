#!/usr/bin/env bash
# Sets up a local Python 3.12 venv for development and testing.
# Run from the repo root: ./setup_venv.sh
set -euo pipefail

PYTHON_VERSION="3.12.11"
VENV_DIR="skill/.venv"

# ── 1. Ensure pyenv is available ────────────────────────────────────────────
if ! command -v pyenv &>/dev/null; then
    echo "ERROR: pyenv not found. Install it from https://github.com/pyenv/pyenv" >&2
    exit 1
fi

# ── 2. Install Python version if missing ────────────────────────────────────
if ! pyenv versions --bare | grep -qx "$PYTHON_VERSION"; then
    echo "==> Installing Python $PYTHON_VERSION via pyenv..."
    pyenv install "$PYTHON_VERSION"
else
    echo "==> Python $PYTHON_VERSION already installed."
fi

# ── 3. Pin version for this repo ────────────────────────────────────────────
pyenv local "$PYTHON_VERSION"
echo "==> Set .python-version to $PYTHON_VERSION"

# ── 4. Create venv ──────────────────────────────────────────────────────────
PYTHON="$(pyenv root)/versions/$PYTHON_VERSION/bin/python"

if [ -d "$VENV_DIR" ]; then
    echo "==> $VENV_DIR already exists — skipping creation."
else
    echo "==> Creating venv at $VENV_DIR ..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

# ── 5. Install dependencies ─────────────────────────────────────────────────
echo "==> Installing requirements-dev.txt ..."
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install -r skill/requirements-dev.txt

echo ""
echo "Done. Activate with:"
echo "  source skill/.venv/bin/activate"
