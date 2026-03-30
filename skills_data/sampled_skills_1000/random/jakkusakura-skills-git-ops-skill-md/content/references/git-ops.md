# Git Ops Reference

Source: `.codex/AGENTS.md`

## Key Rules

- Do not revert or remove changes you did not make.
- Ignore unexpected changes you did not make and do not include them in your commits.
- Assume other users or agents may be working concurrently; never interrupt, include, or alter their in-progress work unless explicitly instructed.
- Do not amend commits unless explicitly requested.
- Do not recommend or execute history-rewriting commands (rebase, reset --hard, push --force) unless explicitly requested.
- For destructive operations (deleting files/directories, rebuilding databases, git reset --hard, git push --force):
  - Warn about risks beforehand.
  - Provide safer alternatives when possible.
  - Usually confirm before running the command.

## Git/GitHub Guidance

- Check git history for commit message patterns; if not specified, use Conventional Commits.
- When doing git operations like rebase, use non-interactive mode with `EDITOR=true`.
- Prefer GitHub interactions via the `gh` CLI when possible.
- When local branch is out of date, prefer fast-forward, then rebase, then merge.

## Additional Constraints

- Do not use `git reset --hard` or `git checkout --` unless specifically requested or approved by the user.

## Staging Guidance
- below guidance should be used if you are told to commit a hunk or multiple users concurrently changed same file
- otherwise git add can still be used
- For non-interactive partial staging, prefer `git apply --cached` with a targeted patch file instead of `git add`.
- Recommended workflow:
  - Generate a diff of the specific files you touched
