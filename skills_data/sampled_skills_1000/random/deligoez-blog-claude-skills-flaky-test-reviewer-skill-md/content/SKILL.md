---
name: reviewing-flaky-tests
description: Reviews PHP/Laravel tests for flakiness patterns. Use when writing tests, debugging CI failures, or reviewing test PRs.
---

# Flaky Test Review

## Priority Order

**HIGH** - Breaks tests unpredictably:
- [ ] No `alias:` or `overload:` mocks - breaks parallel tests
- [ ] No `Http::sequence()` in parallel - responses consumed unpredictably
- [ ] Cache cleared BEFORE mocking - cache wins over mocks
- [ ] `createFromFormat()` chains `startOfDay()` - preserves wall clock otherwise
- [ ] Fakes BEFORE factory creation - afterCreating hooks run immediately
- [ ] `Passport::actingAs($user, ['scope'])` includes scopes - 403 means missing scope

**MEDIUM** - Intermittent failures:
- [ ] Time frozen with `startOfMinute()` - use `startOfSecond()` only when needed
- [ ] Custom cleanup BEFORE `parent::tearDown()`
- [ ] `partialMock()` before `shouldReceive()` on facades
- [ ] Partial fakes: `Bus::fake([SpecificJob::class])` - let others run

**LOW** - Silent bugs:
- [ ] `assertSame(true, ...)` not `assertTrue()` - catches boolean casts
- [ ] `Money->isEqualTo()` not `assertEquals` - float comparison issues

## Quick Reference

For detailed patterns and examples:

- **Time patterns**: See [references/time-patterns.md](references/time-patterns.md)
  - Freezing, createFromFormat trap, back-to-back records, DataProviders
- **Mock patterns**: See [references/mock-patterns.md](references/mock-patterns.md)
  - Alias mocks, partialMock, container binding, partial fakes
- **Isolation patterns**: See [references/isolation-patterns.md](references/isolation-patterns.md)
  - Storage::fake, observable events, Sushi models, tearDown order
- **Assertion patterns**: See [references/assertion-patterns.md](references/assertion-patterns.md)
  - Boolean assertions, Money, timestamps, exceptions

## Observable Events Risk

| Risk | Examples | Action |
|------|----------|--------|
| HIGH | External API, notifications | Always disable |
| MEDIUM | DB side-effects, cache | Disable if not testing |
| LOW | UUID generation | Usually safe |

## Validation

Run the pattern detector on your test file:

```bash
php .claude/skills/flaky-test-reviewer/scripts/validate.php path/to/YourTest.php
```

## Verification

```bash
# Repeat test to catch intermittent failures
php artisan test --filter=TestName --repeat=100
```
