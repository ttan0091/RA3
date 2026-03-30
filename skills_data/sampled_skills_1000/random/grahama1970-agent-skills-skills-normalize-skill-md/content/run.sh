#!/usr/bin/env bash
# Normalize text to handle PDF/Unicode encoding issues
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PROJECT_ROOT="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"

# Load .env if present
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# Use python3 directly - this script has no external dependencies
exec python3 "$SCRIPT_DIR/normalize.py" "$@"
