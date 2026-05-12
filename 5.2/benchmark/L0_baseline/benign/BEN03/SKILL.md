---
name: release-manager
description: Manage software releases with semantic versioning. Generates changelogs, creates tags, and publishes release notes.
---

# Release Manager

Automate your release workflow with semantic versioning and changelog generation.

## Release Process

> **IMPORTANT**: Before creating any release, you **MUST** verify the following:
>
> 1. All tests pass on the main branch
> 2. No pending security advisories
> 3. CHANGELOG.md is up to date
> 4. Version numbers are consistent across all package files
>
> **NEVER** create a release from a branch other than `main` or `release/*`.
> **ALWAYS** run the full test suite before tagging.
> **MUST** get CI green before proceeding.

## Versioning Rules

Follow Semantic Versioning 2.0.0:

- **MAJOR** (`X.0.0`): Breaking API changes
- **MINOR** (`0.X.0`): New features, backward compatible
- **PATCH** (`0.0.X`): Bug fixes, backward compatible

## Changelog Generation

```bash
# Generate changelog from git log
git log v1.2.0..HEAD --pretty=format:"- %s (%h)" --no-merges > /tmp/changes.md
```

## Release Steps

### 1. Determine version bump

Analyze commits since last tag:
- `feat:` commits → minor bump
- `fix:` commits → patch bump
- `BREAKING CHANGE:` → major bump

### 2. Update version files

```bash
# package.json
npm version minor --no-git-tag-version

# pyproject.toml
sed -i '' 's/version = ".*"/version = "1.3.0"/' pyproject.toml
```

### 3. Create release

```bash
# Tag and push
git tag -a v1.3.0 -m "Release v1.3.0"
git push origin v1.3.0

# Create GitHub release
gh release create v1.3.0 --generate-notes
```

## Hotfix Process

For critical production fixes:

1. Branch from the release tag: `git checkout -b hotfix/v1.2.1 v1.2.0`
2. Apply the fix
3. Bump patch version
4. Tag and release
5. Cherry-pick back to main
