# Code Documenter Agent

A specialized documentation agent that generates comprehensive technical docs, API references, and inline code comments.

## What this agent does
- Produces clear, structured documentation for codebases
- Generates or updates API documentation (OpenAPI 3.0)
- Writes concise, intent-focused code comments and docstrings
- Maintains README, onboarding guides, changelogs, and troubleshooting docs
- Emphasizes accessibility and maintainability

## Folder contents
- `SKILL.md`: Skill definition and workflow
- `references/doc-templates.md`: Templates and checklists
- `make_prompt.py`: Helper to generate a ready-to-paste Codex prompt
- `REQUEST.md`: Generated prompt file

## How to use this agent (no Codex CLI)
Because you do not have a Codex CLI, you run this agent via the Codex UI.
Use the helper script to generate a ready-to-paste prompt.

### Step 1: Generate a prompt
```bash
python code-documenter/make_prompt.py "Document the API endpoints in src/web_app.py"
```

Optional flags:
```bash
python code-documenter/make_prompt.py "Update README" \
  --targets "README.md docs/" \
  --output "Update README.md and docs/README.md" \
  --constraints "Follow existing tone; include curl examples"
```

Defaults if you omit flags:
- Targets: `src/ docs/ README.md config/`
- Output: `Update or create documentation files under docs/ and README.md`
- Constraints: `Preserve existing tone and structure; add examples where helpful; do not modify code unless explicitly asked.`

### Step 2: Paste into Codex
1. Open `code-documenter/REQUEST.md`.
2. Copy the content into the Codex UI.
3. Run the request; Codex will use the `code-documenter` skill.

## Example prompts
- "Create API docs with OpenAPI for the current FastAPI app."
- "Add docstrings to the public functions in src/ and summarize usage."
- "Write a troubleshooting guide for common errors in the webhook handler."

## Extending the agent
- Add more templates under `references/`.
- Update `SKILL.md` defaults or workflow for your team’s standards.

## Troubleshooting
- If the skill doesn’t trigger, explicitly include: "Use code-documenter only."
- If outputs don’t match your style guide, add a short example and ask for reformatting.
