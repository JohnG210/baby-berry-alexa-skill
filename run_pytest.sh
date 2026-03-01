#!/usr/bin/env bash
# Run the pytest suite with env vars loaded from .env.
# Usage: ./run_pytest.sh [extra pytest args]
#   ./run_pytest.sh -v
#   ./run_pytest.sh -k test_diaper
#   ./run_pytest.sh --tb=short
set -euo pipefail

if [ ! -f ".env" ]; then
    echo "ERROR: .env not found at repo root." >&2
    exit 1
fi

set -o allexport
source .env
set +o allexport

source skill/.venv/bin/activate

cd skill
pytest "$@"
