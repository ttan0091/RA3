# Exa Web Search Skill

Search the web using Exa's AI-powered search API. This skill provides semantic search capabilities optimized for AI applications.

## Features

- **Search** (`/search`): Semantic web search with optional content extraction
- **Contents** (`/contents`): Extract content from specific URLs
- **Answer** (`/answer`): Get direct answers to factual questions
- **Research** (`/research/v1`): Deep research with structured output

## Setup

1. Get an API key from [Exa Dashboard](https://dashboard.exa.ai/api-keys)
2. Create the config file:

```bash
mkdir -p ~/.config/exa-search
cat > ~/.config/exa-search/config.json << 'EOF'
{
  "api_key": "your-api-key-here"
}
EOF
```

## Quick Start

```bash
# Load API key
EXA_API_KEY=$(jq -r .api_key ~/.config/exa-search/config.json)

# Search the web
curl -s -X POST "https://api.exa.ai/search" \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI agents", "numResults": 5}' | jq '.results[] | {title, url}'

# Get a direct answer
curl -s -X POST "https://api.exa.ai/answer" \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of France?"}' | jq '.answer'
```

See [SKILL.md](./SKILL.md) for complete documentation.
