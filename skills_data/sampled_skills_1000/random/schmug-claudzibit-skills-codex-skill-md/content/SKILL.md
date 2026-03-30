---
name: codex
description: Quick consultation with OpenAI Codex CLI. Use when you want another AI's perspective on code, architecture, or any technical question.
---

# Codex AI Consultation

Query OpenAI Codex for a second opinion. Pass your question as $ARGUMENTS.

## Usage

```
/codex What's the most efficient way to batch database inserts with Drizzle?
/codex Suggest alternative approaches for this caching strategy
```

## Workflow

### Step 1: Model Selection

Before running the query, check which model is configured. Read `~/.codex/config.toml` to find the current `model` setting. If no model is configured there, ask the user which OpenAI model to use via AskUserQuestion (provide the latest frontier options you're aware of, plus an "Other" escape hatch). Pass the chosen model with `-m MODEL_NAME`.

If the user has used this skill before in the same session and already selected a model, reuse that choice without asking again.

### Step 2: Context Gathering

If $ARGUMENTS references specific files or code, read those files first and include relevant snippets in the prompt.

### Step 3: Run Query

```bash
codex exec -m MODEL_NAME "YOUR PROMPT HERE" -o /tmp/codex-result.txt 2>/dev/null; cat /tmp/codex-result.txt 2>/dev/null; rm -f /tmp/codex-result.txt
```

### Step 4: Present Results

Present Codex's response to the user. Add your own perspective — note where you agree, disagree, or have additional context.

## Rules

- Always suppress stderr to avoid UI noise
- For file context, include relevant snippets directly in the prompt string
- Keep prompts focused — don't dump entire files unless necessary
- If Codex returns an error or empty response, inform the user and suggest they check `codex` CLI auth
- Do NOT use `--dangerously-bypass-approvals-and-sandbox` — this is read-only consultation
- Clean up any temp files after reading
