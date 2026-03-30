---
name: validate-starter-scripts
description: validation audit quality check startup initialization integrity
---

# Validate Starter Scripts Skill

Performs comprehensive validation of your 20 starter scripts before the game jam begins.

## What This Does

Checks your complete starter script set for:

- **Code Quality** - Consistent naming, proper encapsulation, clean dependencies
- **Best Practices** - Proper Singleton patterns, error handling, null checks, proper disposal
- **Integration Health** - Scripts work together without conflicts, proper initialization order, no circular dependencies
- **Memory Safety** - Object pooling consistency, proper cleanup, no memory leaks
- **Modern Pattern Readiness** - Input System compatibility, async/await preparedness, resource management

## Activation Triggers

This skill activates when you:
- Ask to "validate my starter scripts"
- Request a "code audit" or "quality check"
- Run `/review-starters` command
- Ask to "check my 20 scripts" or "review my starters"

## Output Format

Returns a structured report:
1. **Critical Issues** (must fix before jam)
2. **Best Practice Suggestions** (improve code quality)
3. **Integration Warnings** (potential team collaboration issues)
4. **Modern Pattern Gaps** (missing Input System, async patterns, etc.)
5. **Ready Status** - "Ready to ship" or list of recommended fixes

## Pre-Jam Usage

Run this before your game jam starts to ensure all starter scripts are solid and won't cause problems during development.
