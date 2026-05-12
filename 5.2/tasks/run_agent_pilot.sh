#!/bin/bash
# Agent-based pilot experiment using Codex CLI
#
# Usage:
#   ./run_agent_pilot.sh           # run all sequentially
#   ./run_agent_pilot.sh --parallel # run all in parallel

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/run_agent_experiment.py" "$@"
