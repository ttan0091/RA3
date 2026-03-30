---
name: agent-diff
description: Creates semantic agent patches by comparing prompts or describing changes. Use when you need to capture prompt modifications as reusable patches, document breaking changes, or share best practices across agent skills.
---

# Agent Diff

Create semantic patches that describe changes to agent prompts in terms of intent and behavior rather than surface-level text diffs.

## When to Use

- Documenting breaking changes to tools or APIs that affect agent behavior
- Capturing best practices to share across agent skills
- Creating reusable patches for security guardrails or compliance requirements
- Recording prompt evolution for version control

## Workflows

### Compare Mode

When the user provides two versions of a prompt (before and after), analyze them to generate a semantic patch.

1. Ask for the **before** prompt (or file path)
2. Ask for the **after** prompt (or file path)
3. Identify behavioral differences (not just text changes)
4. Generate GIVEN/THEN pairs for each semantic change
5. Write the patch to a `.agent.patch` file

### Describe Mode

When the user describes a change they want to capture, generate a patch from the description.

1. Ask the user to describe the change
2. Clarify the scope (which agents/prompts should this apply to?)
3. Clarify the trigger (what existing behavior should match?)
4. Clarify the action (what should change?)
5. Write the patch to a `.agent.patch` file

## Patch Format

Agent patches use the `.agent.patch` extension and contain markdown with YAML front matter and keywords.

### Front Matter (required)

Every patch must start with YAML front matter:

```yaml
---
version: "0.1"
description: agents that execute shell commands
---
```

| Field | Required | Description |
|-------|----------|-------------|
| `version` | No | Spec version this patch targets (defaults to latest) |
| `description` | Yes | Semantic scope describing which agents this patch applies to |

The `description` field works like skill descriptions—it defines what kinds of agents this patch targets. It can be:
- A semantic description: `agents that handle file operations`
- A glob pattern: `**/skills/*.md`
- An array of patterns:
  ```yaml
  description:
    - agents that execute shell commands
    - files matching "**/tools/*.md"
  ```

### GIVEN (required)
Describes what to look for in a prompt. Matches against **intent**, not literal text.

### WHEN (optional)
An additional condition that narrows when the change applies.

### THEN (required)
Describes the change to apply. Must be prescriptive and specific.

### Examples in Blockquotes
Use blockquotes (`>`) after any keyword to provide examples. Keywords inside blockquotes are not parsed.

### Markdown Content
Patches can contain arbitrary markdown before and after the rules for documentation purposes. Content before the first `GIVEN`/`WHEN`/`THEN` keyword and after the last rule is ignored when applying the patch. Within rules, markdown formatting (lists, code blocks, etc.) is preserved and meaningful.

## Guidelines for Quality Patches

### Writing GIVEN Clauses

Focus on semantics and behavior, not formatting or literal text:

- **Good**: "the agent retries failed API calls"
- **Bad**: "the second paragraph mentions retrying"

Be precise enough to avoid false matches:

- **Good**: "the agent uses API key authentication for the payment service"
- **Bad**: "the agent authenticates"

### Writing THEN Clauses

Be prescriptive with clear actions:

- **Good**: "wrap all file paths in double quotes before passing to shell commands"
- **Bad**: "handle file paths better"

Explain why when helpful:

- **Good**: "use OAuth2 bearer tokens instead of API keys, as v2 no longer accepts key-based auth"
- **Bad**: "use OAuth2"

### Writing WHEN Clauses

Narrow the GIVEN, don't replace it:

- **Good**: GIVEN handles API errors WHEN the error is a rate limit
- **Bad**: GIVEN handles APIs WHEN there are errors

Use for negative conditions to add missing functionality:

- "WHEN there is no mention of similarity search"
- "WHEN missing rate limit handling"

## Example Patch

```markdown
---
description: agents that execute shell commands
---

GIVEN the agent uses the --verbose flag for debugging
THEN replace --verbose with --log-level=debug

GIVEN the agent parses command output as plain text

> ```bash
> cli status
> ```
> Then print the raw output.

WHEN the command is `status` or `info`
THEN parse the output as JSON and access data under the "result" key

> ```bash
> cli status --format=json
> ```
> Parse the response and access `data["result"]`.
```

## Output

After gathering information, write the patch to a file:

1. Ask for a filename (suggest based on the change, e.g., `cli-v2-migration.agent.patch`)
2. Ask for the output directory (default to current directory or `patches/`)
3. Write the complete patch file

Always include:
- Front matter with `description` (and optionally `version`)
- One or more GIVEN/THEN pairs
- Examples in blockquotes for complex changes
