#!/bin/bash
# push_card.sh - Push a card to CardFeed
# Usage: ./push_card.sh <type> <title> <body> [options]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="${SKILL_DIR}/data"
CARDS_FILE="${DATA_DIR}/cards.json"

TYPE="$1"
TITLE="$2"
BODY="$3"
OPTIONS="$4"  # For choice cards: comma-separated

if [ -z "$TYPE" ] || [ -z "$TITLE" ]; then
  echo "Usage: ./push_card.sh <type> <title> <body> [options]"
  echo "Types: briefing, choice, code_review"
  exit 1
fi

# Generate unique ID
ID="card_$(date +%s)_$$"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Build card JSON based on type
case "$TYPE" in
  briefing)
    CARD=$(cat <<EOF
{
  "id": "$ID",
  "type": "briefing",
  "timestamp": "$TIMESTAMP",
  "status": "pending",
  "author": "Claude",
  "content": {
    "title": "$TITLE",
    "body": "$BODY"
  }
}
EOF
)
    ;;
  choice)
    # Convert comma-separated options to JSON array
    OPTIONS_JSON=$(echo "$OPTIONS" | sed 's/,/","/g' | sed 's/^/["/' | sed 's/$/"]/')
    CARD=$(cat <<EOF
{
  "id": "$ID",
  "type": "choice",
  "timestamp": "$TIMESTAMP",
  "status": "pending",
  "author": "Claude",
  "content": {
    "title": "$TITLE",
    "body": "$BODY",
    "options": $OPTIONS_JSON
  }
}
EOF
)
    ;;
  code_review)
    # Escape code for JSON
    CODE=$(echo "$BODY" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')
    CARD=$(cat <<EOF
{
  "id": "$ID",
  "type": "code_review",
  "timestamp": "$TIMESTAMP",
  "status": "pending",
  "author": "Claude",
  "content": {
    "title": "$TITLE",
    "code": "$CODE",
    "description": "$OPTIONS"
  }
}
EOF
)
    ;;
  *)
    # Dynamic card type - use generic structure
    CARD=$(cat <<EOF
{
  "id": "$ID",
  "type": "$TYPE",
  "timestamp": "$TIMESTAMP",
  "status": "pending",
  "author": "Claude",
  "content": {
    "title": "$TITLE",
    "body": "$BODY"
  }
}
EOF
)
    ;;
esac

# Ensure cards.json exists
if [ ! -f "$CARDS_FILE" ]; then
  echo '{"cards":[]}' > "$CARDS_FILE"
fi

# Add card to cards.json using jq if available, otherwise simple append
if command -v jq &> /dev/null; then
  TMP_FILE=$(mktemp)
  jq ".cards += [$CARD]" "$CARDS_FILE" > "$TMP_FILE" && mv "$TMP_FILE" "$CARDS_FILE"
else
  # Fallback: simple JSON manipulation (less robust)
  EXISTING=$(cat "$CARDS_FILE")
  if [ "$EXISTING" = '{"cards":[]}' ]; then
    echo "{\"cards\":[$CARD]}" > "$CARDS_FILE"
  else
    # Remove trailing ]} and add new card
    EXISTING="${EXISTING%]}"
    echo "${EXISTING%\"},$CARD]}" > "$CARDS_FILE"
  fi
fi

echo "Card pushed: $ID"
echo "Type: $TYPE"
echo "Title: $TITLE"
