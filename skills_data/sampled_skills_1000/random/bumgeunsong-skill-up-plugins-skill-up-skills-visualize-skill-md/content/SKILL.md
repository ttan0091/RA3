---
name: visualize
description: Use when the user wants to see their skill inventory, stat sheet, or skill visualization. Triggers on "스킬 보여줘", "스탯창", "내 스킬", "/visualize", "skill inventory", "스킬트리", "skill tree"
allowed-tools: Read, Glob, Grep, Bash, Write
---

# Skill Visualize

Render the user's skill inventory as a gamified RPG-style character sheet in the browser.

## Quick Reference

| Step | Action |
|------|--------|
| 1 | Read eval data from `~/.claude/.skill-evaluator/skills/{YYYY-MM}.json` |
| 2 | Scan installed skills (user/project/plugin scopes) |
| 3 | Build data JSON (profile + skills array) |
| 4 | Inject into template, write to `/tmp/skill-up-viz.html`, open browser |

See `reference.md` in this directory for JSON schemas, grade tables, categories, and icon keys.

## Workflow

1. **Read evaluation data**: Current month file, fallback to previous months, or generate placeholder from installed SKILL.md files
2. **Scan skills** for metadata (name, description, trigger) across all scopes
3. **Build data JSON**: Calculate grades (usage-based SSS~F), level, job title (creative Korean title with emoji), assign categories and icon keys
4. **Render**: Read `visualize/template.html` (relative to plugin dir), replace `__SKILL_UP_DATA__`, write to `/tmp/skill-up-viz.html`, run `open`

## Upgrade Feature

Tooltip has "강화" button → copies `/upgrade-skill {skill-name}` to clipboard → toast notification. Upgraded skills (`upgraded: true`) show badge and disabled "강화 완료" button.

## Response

Briefly summarize: total skills, data source month, top grade skills, generated job title.
