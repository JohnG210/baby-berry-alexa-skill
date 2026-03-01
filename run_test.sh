#!/usr/bin/env bash
# Run a Lambda test event against the skill locally.
# Usage: ./run_test.sh skill/test_events/launch.json
set -euo pipefail

EVENT="${1:-skill/test_events/launch.json}"

if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found at repo root." >&2
    exit 1
fi

set -o allexport
# shellcheck source=.env
source .env
set +o allexport

source skill/.venv/bin/activate

cd skill
lambda-local -l lambda_function.py -h lambda_handler -e "../$EVENT"
