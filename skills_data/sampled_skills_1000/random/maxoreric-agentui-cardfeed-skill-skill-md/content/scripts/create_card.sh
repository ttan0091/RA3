#!/bin/bash
# create_card.sh - Generate a new Card component for CardFeed
# Usage: ./create_card.sh <CardName> <description>
# Example: ./create_card.sh ProgressCard "Shows progress with percentage bar"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CARDS_DIR="${SKILL_DIR}/app/src/components/cards"
REGISTRY_FILE="${CARDS_DIR}/index.ts"

CARD_NAME="$1"
DESCRIPTION="$2"

if [ -z "$CARD_NAME" ]; then
  echo "Usage: ./create_card.sh <CardName> <description>"
  echo "Example: ./create_card.sh ProgressCard 'Shows progress with percentage bar'"
  exit 1
fi

# Convert CardName to lowercase type name
# ProgressCard -> progress, DashboardCard -> dashboard
BASE_NAME=$(echo "$CARD_NAME" | sed 's/Card$//')
TYPE_NAME=$(echo "$BASE_NAME" | tr '[:upper:]' '[:lower:]')

CARD_FILE="${CARDS_DIR}/${CARD_NAME}.tsx"

# Check if card already exists
if [ -f "$CARD_FILE" ]; then
  echo "Card already exists: $CARD_FILE"
  exit 1
fi

# Generate the card component
cat > "$CARD_FILE" << EOF
import type { CardResponse } from '../../types/card';

interface ${CARD_NAME}Data {
  type: '${TYPE_NAME}';
  content: {
    title: string;
    // TODO: Add more fields as needed
    [key: string]: any;
  };
}

interface ${CARD_NAME}Props {
  card: ${CARD_NAME}Data & { id: string; timestamp: string; status: string; author?: string };
  onRespond: (response: CardResponse) => void;
}

/**
 * ${CARD_NAME}
 * ${DESCRIPTION:-"Custom card component"}
 */
export function ${CARD_NAME}({ card, onRespond }: ${CARD_NAME}Props) {
  const handleAcknowledge = () => {
    onRespond({
      cardId: card.id,
      timestamp: new Date().toISOString(),
      action: 'acknowledge',
    });
  };

  return (
    <div className="card-content">
      <h1>{card.content.title}</h1>
      <div className="card-body">
        {/* TODO: Customize this card's content */}
        <p>This is a custom ${CARD_NAME}.</p>
      </div>
      <div className="card-interactions">
        <button className="btn btn-primary" onClick={handleAcknowledge}>
          ✅ Acknowledge
        </button>
      </div>
    </div>
  );
}
EOF

echo "Created: $CARD_FILE"

# Update the registry (index.ts)
# Add import
sed -i '' "s|^import { BriefingCard }|import { ${CARD_NAME} } from './${CARD_NAME}';\nimport { BriefingCard }|" "$REGISTRY_FILE"

# Add to CardRegistry
sed -i '' "s|code_review: CodeReviewCard,|code_review: CodeReviewCard,\n  ${TYPE_NAME}: ${CARD_NAME},|" "$REGISTRY_FILE"

# Add to exports
sed -i '' "s|export { BriefingCard|export { ${CARD_NAME}, BriefingCard|" "$REGISTRY_FILE"

echo "Updated registry: $REGISTRY_FILE"
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  Card '${CARD_NAME}' created!                          ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  Type: '${TYPE_NAME}'                                  ║"
echo "║  File: ${CARD_FILE}                                    ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  Vite HMR will auto-reload the app                     ║"
echo "║  Push a card with type '${TYPE_NAME}' to test          ║"
echo "╚════════════════════════════════════════════════════════╝"
