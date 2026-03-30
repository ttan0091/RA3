---
name: zellij
description: Control Zellij terminal multiplexer from Claude Code. Use when the user asks to create panes, tabs, run commands in new panes, manage terminal layout, or interact with the Zellij workspace.
---

# Zellij Control Skill

Zellij is a terminal workspace/multiplexer. This skill enables Claude Code to control Zellij sessions, panes, and tabs.

## Environment Detection

When running inside a Zellij session, these environment variables are available:
- `ZELLIJ` - Set to `0` when inside a session
- `ZELLIJ_SESSION_NAME` - Name of the current session
- `ZELLIJ_PANE_ID` - ID of the current pane

Check if inside Zellij:
```bash
if [ -n "$ZELLIJ" ]; then echo "Inside Zellij"; fi
```

## Git Worktree Convention

**IMPORTANT**: When creating git worktrees (e.g., for a new zellij tab), always create them inside the repository's `.worktrees/` directory:

```
<git-root>/.worktrees/<branch-name>
```

**Correct example:**
```bash
# From /Users/pepe/projects/github.com/pepegar/femto
git worktree add .worktrees/github-actions -b github-actions
# Result: /Users/pepe/projects/github.com/pepegar/femto/.worktrees/github-actions
```

**WRONG - Do NOT create worktrees as sibling directories:**
```bash
# WRONG: git worktree add ../femto-github-actions github-actions
```

This convention keeps worktrees organized within the repository and is consistent with the `git-wt` tool.

## Common Operations

### Run Command in New Pane

```bash
# Open new pane to the right (default direction)
zellij run -- <command>

# Open floating pane
zellij run -f -- <command>

# Open pane in specific direction
zellij run -d right -- <command>
zellij run -d down -- <command>

# Open pane with custom name
zellij run -n "my-pane" -- <command>

# Open pane with specific working directory
zellij run --cwd /path/to/dir -- <command>

# Close pane automatically when command exits
zellij run -c -- <command>

# Open in-place (suspends current pane)
zellij run -i -- <command>

# Start suspended (waits for ENTER to run)
zellij run -s -- <command>
```

### Pane Actions

```bash
# Close focused pane
zellij action close-pane

# Move focus
zellij action focus-next-pane
zellij action focus-previous-pane
zellij action move-focus right
zellij action move-focus left
zellij action move-focus up
zellij action move-focus down

# Move pane
zellij action move-pane right
zellij action move-pane left
zellij action move-pane up
zellij action move-pane down

# Toggle floating panes
zellij action toggle-floating-panes

# Toggle fullscreen
zellij action toggle-fullscreen

# Rename pane
zellij action rename-pane "new-name"

# Clear pane buffer
zellij action clear
```

### Tab Actions

```bash
# Create new tab
zellij action new-tab

# Create new tab with name
zellij action new-tab -n "my-tab"

# Create new tab with working directory
zellij action new-tab --cwd /path/to/dir

# Create new tab with layout
zellij action new-tab -l /path/to/layout.kdl

# Navigate tabs
zellij action go-to-next-tab
zellij action go-to-previous-tab
zellij action go-to-tab 1
zellij action go-to-tab-name "my-tab"

# Rename tab
zellij action rename-tab "new-name"

# Close tab
zellij action close-tab

# Move tab
zellij action move-tab left
zellij action move-tab right

# Query tab names
zellij action query-tab-names
```

### Create Tab with Command (Using Layout)

**IMPORTANT**: Unlike `zellij run` which creates panes, to create a **tab** with a command you MUST use a layout file. The `new-tab` action does NOT accept a command argument directly.

**Step 1: Create a temporary KDL layout file**

Layout files use KDL syntax. Example layout that creates a tab with a command:

```kdl
layout {
    tab name="my-tab" cwd="/path/to/workdir" {
        pane command="bash" {
            args "-c" "echo 'hello' | my-command --flag"
        }
    }
}
```

**Step 2: Create the tab using the layout**

```bash
zellij action new-tab -l /tmp/my-layout.kdl
```

**Complete example - Create tab running a command (with compact-bar UI):**

```bash
# Create layout file with compact-bar UI
cat > /tmp/tab-layout.kdl << 'EOF'
layout {
    default_tab_template {
        children
        pane size=1 borderless=true {
            plugin location="zellij:compact-bar"
        }
    }
    tab name="dev-server" cwd="/home/user/project" {
        pane command="npm" {
            args "run" "dev"
        }
    }
}
EOF

# Create tab from layout
zellij action new-tab -l /tmp/tab-layout.kdl
```

**Layout syntax reference:**

| Property | Example | Notes |
|----------|---------|-------|
| `tab name="x"` | `tab name="server"` | Tab display name |
| `cwd` | `cwd="/path"` | Working directory (can be on tab or pane) |
| `command` | `command="node"` | Executable to run |
| `args` | `args "arg1" "arg2"` | Arguments (must be in child braces) |
| `focus true` | `pane focus=true` | Set initial focus |

**Pane with command and args:**

```kdl
pane command="bash" {
    args "-c" "echo 'Create something' | claude --dangerously-skip-permissions"
}
```

### Scrolling

```bash
zellij action scroll-up
zellij action scroll-down
zellij action page-scroll-up
zellij action page-scroll-down
zellij action half-page-scroll-up
zellij action half-page-scroll-down
zellij action scroll-to-top
zellij action scroll-to-bottom
```

### Layout Operations

```bash
# Dump current layout to stdout
zellij action dump-layout

# Dump focused pane content to file
zellij action dump-screen /path/to/file

# Switch to next/previous swap layout
zellij action next-swap-layout
zellij action previous-swap-layout
```

### Resize Panes

```bash
zellij action resize increase left
zellij action resize increase right
zellij action resize increase up
zellij action resize increase down
zellij action resize decrease left
zellij action resize decrease right
zellij action resize decrease up
zellij action resize decrease down
```

### Session Management

```bash
# List active sessions
zellij list-sessions

# Attach to session
zellij attach <session-name>
zellij attach -c  # Create if doesn't exist

# Kill session
zellij kill-session <session-name>
zellij kill-all-sessions

# Delete session (removes from resurrection)
zellij delete-session <session-name>
zellij delete-all-sessions

# Rename current session
zellij action rename-session "new-name"
```

### Input Mode Switching

```bash
# Switch input mode for all connected clients
zellij action switch-mode locked
zellij action switch-mode pane
zellij action switch-mode tab
zellij action switch-mode resize
zellij action switch-mode move
zellij action switch-mode search
zellij action switch-mode session
```

### Write to Terminal

```bash
# Write characters to the focused pane
zellij action write-chars "text to write"

# Write raw bytes
zellij action write 27 91 65  # ESC [ A (arrow up)
```

### Edit Files

```bash
# Open file in new pane with default editor
zellij edit /path/to/file

# Open floating editor
zellij edit -f /path/to/file

# Edit scrollback of current pane
zellij action edit-scrollback
```

## Floating Pane Options

When using `zellij run -f` (floating pane), you can specify:

```bash
# Size and position as percentages
zellij run -f --width 50% --height 50% --x 25% --y 25% -- <command>

# Size and position as absolute values
zellij run -f --width 80 --height 24 --x 10 --y 5 -- <command>

# Pinned floating pane (always on top)
zellij run -f --pinned true -- <command>
```

## Usage Patterns for Claude Code

### Run Tests in New Pane
```bash
zellij run -f -n "tests" -- npm test
```

### Open Log Viewer
```bash
zellij run -d down -n "logs" -- tail -f /var/log/app.log
```

### Start Development Server
```bash
zellij run -f --width 40% --height 30% --x 60% --y 0% -n "server" -- npm run dev
```

### Create Side-by-Side Layout
```bash
# Run in new pane to the right
zellij run -d right -- htop
```

### Quick Terminal for Commands
```bash
# Open floating terminal, close when done
zellij run -f -c -- bash -c "echo 'Done!'; sleep 2"
```

### Create Tab with Claude Code Running

To spawn a new tab running Claude Code with a prompt, you MUST include the default UI otherwise the tab will be missing the standard Zellij interface.

**Using compact-bar (minimal UI):**

```bash
cat > /tmp/claude-tab.kdl << 'EOF'
layout {
    default_tab_template {
        children
        pane size=1 borderless=true {
            plugin location="zellij:compact-bar"
        }
    }
    tab name="github-actions" cwd="/path/to/repo/.worktrees/branch-name" {
        pane command="bash" {
            args "-c" "echo 'Create a GitHub Action for testing' | claude --dangerously-skip-permissions"
        }
    }
}
EOF

zellij action new-tab -l /tmp/claude-tab.kdl
```

**Using tab-bar + status-bar (full UI):**

```bash
cat > /tmp/claude-tab.kdl << 'EOF'
layout {
    default_tab_template {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children
        pane size=2 borderless=true {
            plugin location="zellij:status-bar"
        }
    }
    tab name="github-actions" cwd="/path/to/repo/.worktrees/branch-name" {
        pane command="bash" {
            args "-c" "echo 'Create a GitHub Action for testing' | claude --dangerously-skip-permissions"
        }
    }
}
EOF

zellij action new-tab -l /tmp/claude-tab.kdl
```

**Important**: Without `default_tab_template` containing UI plugins, the new tab will be missing the standard Zellij interface.

## Important Notes

1. **Action commands require active session**: `zellij action *` commands only work when running inside a Zellij session (when `$ZELLIJ` env var is set).

2. **Session commands work anywhere**: `zellij list-sessions`, `zellij attach`, etc. work outside of sessions.

3. **Panes vs Tabs with commands**:
   - `zellij run -- <cmd>` creates a **pane** with a command (simple, direct)
   - `zellij action new-tab -l layout.kdl` creates a **tab** with a command (requires layout file)
   - There is NO `zellij action new-tab -- <cmd>` syntax

4. **Check session context**: Always verify you're in a Zellij session before using action commands:
   ```bash
   [ -n "$ZELLIJ" ] && zellij action <command>
   ```

5. **Floating panes**: Great for temporary outputs, logs, or monitoring without disrupting layout.

## Quick Reference

| Task | Command |
|------|---------|
| New pane with command | `zellij run -- <cmd>` |
| Floating pane | `zellij run -f -- <cmd>` |
| New tab (empty) | `zellij action new-tab` |
| New tab with command | `zellij action new-tab -l layout.kdl` (requires layout file) |
| Close pane | `zellij action close-pane` |
| Focus right | `zellij action move-focus right` |
| List sessions | `zellij list-sessions` |
| Rename pane | `zellij action rename-pane "name"` |
| Toggle floating | `zellij action toggle-floating-panes` |
| Fullscreen | `zellij action toggle-fullscreen` |

## Key Distinction: Panes vs Tabs

- **Pane with command**: Use `zellij run -- <command>` - simple and direct
- **Tab with command**: Use `zellij action new-tab -l <layout.kdl>` - requires a KDL layout file

There is NO way to create a tab with a command without using a layout file.
