---
name: mycelium-continue
description: Resumes interrupted workflow from last checkpoint with context-aware scope detection. Use when user says "continue", "resume work", "keep going", "finish this", or after interruption. Supports --full to run all remaining phases (plan→work→review→capture) and --track to switch between multiple plans. Auto-detects whether to finish current phase or run full workflow.
license: MIT
version: 0.9.0
argument-hint: "[--full] [--track <track_id>]"
allowed-tools: ["Skill", "Read", "Write", "Edit", "Bash", "Glob", "Grep", "Task", "AskUserQuestion"]
metadata:
  author: Jason Hsieh
  category: workflow
  tags: [resume, checkpoint, context-management]
  documentation: https://github.com/jason-hchsieh/mycelium
---

# Workflow Continue

Resume interrupted work with context-aware scope detection.

## Your Task

1. **Parse arguments**:
   - `--full`: Override to full mode — run all remaining phases to completion regardless of original invocation
   - `--track <track_id>`: Switch to and resume a specific plan (pauses the current active plan)

2. **Load session state**:
   - Read `.mycelium/state.json`
   - Identify `current_phase`, checkpoints, and `invocation_mode`
   - If no state found → error: "No workflow state found. Start with `/mycelium-go` or `/mycelium-plan`."

3. **Handle `--track` if provided**:
   - Find `<track_id>` in `session_state.plans[]`. If not found, check `.mycelium/plans/` for a matching file. If still not found, error: "Plan `<track_id>` not found."
   - Set the current active plan to `"paused"` in both `plans[]` and its plan file frontmatter
   - Set the target plan to `"in_progress"` in both `plans[]` and its plan file frontmatter
   - Update `current_track` to point to the target plan
   - Re-read the target plan to determine its `current_phase` and checkpoints

4. **Restore mid-phase context**:
   - Read `.mycelium/progress.md` for completed work summary
   - Check for uncommitted work (`git status`) or stashes (`git stash list`)
   - Show what was completed, what's in progress, and known blockers

5. **Determine continuation scope**:

   | Condition | Behavior |
   |-----------|----------|
   | `--full` flag provided | Follow `mycelium-go` workflow, resume current phase, chain through ALL remaining phases to end |
   | `invocation_mode == "full"` (started via `/mycelium-go`) | Follow `mycelium-go` workflow, resume current phase, chain through ALL remaining phases to end |
   | `invocation_mode == "single"` (started via `/workflow-[phase]`) | Load appropriate phase skill, finish current phase ONLY |
   | No `invocation_mode` in state | Treat as `"single"` — finish current phase only |

6. **Load appropriate skill and execute**:

   **Full mode** (mycelium-go):
   - Load `mycelium-go` skill (contains full workflow logic)
   - Resume from current phase checkpoint
   - Chain through remaining phases: context_loading → clarify_request → planning → implementation → verification → context_sync → review → finalization → pattern_detection → store_knowledge

   **Single mode** (phase-specific):
   - Map `current_phase` to skill:
     - `context_loading` → Invoke `mycelium-context-load`
     - `clarify_request` → Invoke `mycelium-clarify`
     - `planning` → Invoke `mycelium-plan`
     - `implementation` → Invoke `mycelium-work`
     - `verification` → Invoke `mycelium-work` (verification is internal, part of work phase)
     - `context_sync` → Invoke `mycelium-work` (context sync is internal, part of work phase)
     - `review` → Invoke `mycelium-review`
     - `finalization` → Invoke `mycelium-finalize`
     - `pattern_detection` → Invoke `mycelium-patterns`
     - `store_knowledge` → Invoke `mycelium-capture`
     - `completed` → Output "✅ Workflow already complete!"
   - Resume from checkpoint within that phase
   - Stop after phase completion

6. **Final report**: Summarize what was resumed and completed

## Skills Used

Varies based on continuation scope:

**Full mode**:
- **mycelium-go**: Phase management, chaining through remaining phases (all 8 phases)

**Single mode** (one of):
- **mycelium-context-load**: If interrupted during Phase 0 (context loading)
- **mycelium-clarify**: If interrupted during Phase 1 (clarify request)
- **mycelium-plan**: If interrupted during Phase 2 (planning)
- **mycelium-work**: If interrupted during Phase 3/4.5/4.5B (implementation/verification/context)
- **mycelium-review**: If interrupted during Phase 5 (review)
- **mycelium-finalize**: If interrupted during Phase 6 (finalization)
- **mycelium-patterns**: If interrupted during Phase 6E (pattern detection)
- **mycelium-capture**: If interrupted during Phase 6F (store knowledge)

## Quick Examples

```bash
# Resume with context-aware scope (finishes what was originally started)
/mycelium-continue

# Override to full mode — run all remaining phases regardless
/mycelium-continue --full

# Switch to and resume a specific plan
/mycelium-continue --track auth_20260210

# Switch to a plan and run all remaining phases
/mycelium-continue --track auth_20260210 --full
```

## Behavior Summary

| Original skill | `/mycelium-continue` | `/mycelium-continue --full` |
|---------------|---------------------|---------------------------|
| `/mycelium-go` | Resume → finish all remaining phases | Same |
| `/mycelium-context-load` | Resume → finish Phase 0 only | Resume → finish all remaining phases |
| `/mycelium-clarify` | Resume → finish Phase 1 only | Resume → finish all remaining phases |
| `/mycelium-plan` | Resume → finish Phase 2 only | Resume → finish all remaining phases |
| `/mycelium-work` | Resume → finish Phase 3 only | Resume → finish all remaining phases |
| `/mycelium-review` | Resume → finish Phase 5 only | Resume → finish all remaining phases |
| `/mycelium-finalize` | Resume → finish Phase 6 only | Resume → finish all remaining phases |
| `/mycelium-patterns` | Resume → finish Phase 6E only | Resume → finish all remaining phases |
| `/mycelium-capture` | Resume → finish Phase 6F only | Resume → finish all remaining phases |

**With `--track`**: Pauses current active plan, switches to specified plan, then follows the same scope rules above.

## Important

- **Context-aware** - Automatically detects whether to resume single phase or full workflow
- **`--full` override** - Forces full workflow mode regardless of original invocation
- **`--track` switch** - Switch to and resume a different plan (auto-pauses current plan)
- **Verifies test baseline** - Runs tests before continuing (must pass)
- **Handles uncommitted work** - Shows uncommitted changes, offers to stash or keep
- **Context efficient** - Loads summary from progress.md, not full history
- **Safe defaults** - When uncertain, asks user before proceeding

## References

- [`.mycelium/` directory structure][mycelium-dir]
- [Session state docs][session-state-docs]
- [Session state schema][session-state-schema]
- [Progress template][progress-template]

[mycelium-dir]: ../../docs/mycelium-directory.md
[session-state-docs]: ../../docs/session-state.md
[session-state-schema]: ../../schemas/session-state.schema.json
[progress-template]: ../../templates/state/progress.md.template
