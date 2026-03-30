#!/bin/bash
# read_response.sh - Read and display user responses from CardFeed
# Usage: ./read_response.sh [--wait] [--clear]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="${SKILL_DIR}/data"
RESPONSES_FILE="${DATA_DIR}/responses.json"

WAIT=false
CLEAR=false

for arg in "$@"; do
  case $arg in
    --wait) WAIT=true ;;
    --clear) CLEAR=true ;;
  esac
done

# Check if responses.json exists
if [ ! -f "$RESPONSES_FILE" ]; then
  echo '{"responses":[]}' > "$RESPONSES_FILE"
fi

# Wait for response if requested
if [ "$WAIT" = true ]; then
  echo "Waiting for user response..."
  while true; do
    RESPONSES=$(cat "$RESPONSES_FILE")
    COUNT=$(echo "$RESPONSES" | grep -o '"cardId"' | wc -l)
    if [ "$COUNT" -gt 0 ]; then
      break
    fi
    sleep 2
  done
fi

# Display responses
cat "$RESPONSES_FILE"

# Clear if requested
if [ "$CLEAR" = true ]; then
  echo '{"responses":[]}' > "$RESPONSES_FILE"
  echo ""
  echo "(Responses cleared)"
fi
