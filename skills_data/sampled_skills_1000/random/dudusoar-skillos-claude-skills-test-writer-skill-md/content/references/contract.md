# Skill Contract: test-writer

> Complete specification of what can evolve and what must remain stable.

## Stable (General Knowledge)

**Core Elements:**
- 8-step workflow (Analyze Code → Identify Test Cases → Determine Framework → Generate Structure → Add Tests → Add Mocks/Fixtures → Write File → Add Documentation)
- Test case categories (happy path, edge cases, error cases, type variations, state-dependent)
- AAA pattern (Arrange-Act-Assert)
- Framework selection logic
- Testing best practices (independence, naming, organization)

**Do not modify:**
- Workflow steps and their order
- Core test case classification system
- AAA pattern structure
- Principle of test independence
- Framework-agnostic approach (support multiple frameworks)

## Mutable (Can Evolve)

**Can be updated during projects:**
- Add new framework-specific templates (new languages, new testing frameworks)
- Add test patterns for specific scenarios (async, database, API, etc.)
- Refine test case identification heuristics
- Add examples of good/bad tests from real experience
- Add to references/ common testing pitfalls or patterns
- Improve mock/fixture generation strategies

**Update guidelines:**
- New framework templates should follow existing structure pattern
- Test patterns should be proven and reusable
- Examples should be real cases (anonymized if needed)
- Best practices should cite sources when possible
- Prefer adding to references/ over expanding SKILL.md

## Update Rules

**Allowed without review:**
- Add new framework template (following existing pattern)
- Add test pattern examples with explanations
- Add to references/ testing strategies or checklists
- Fix typos, grammar, or improve clarity
- Add edge case scenarios based on experience
- Add assertion patterns for new data types

**Requires review:**
- Modify core workflow steps or their order
- Change AAA pattern recommendations
- Modify framework selection logic
- Add new major sections to SKILL.md
- Change test independence principles

**Prohibited:**
- Remove AAA pattern (industry standard)
- Skip test case identification step
- Encourage test interdependence
- Remove framework support (can add, not remove)
- Generate tests that aren't independent

## Knowledge Extraction

**What to extract after projects:**
- Common test patterns that work well across projects
- Framework-specific gotchas and solutions
- Effective mocking strategies for different scenarios
- Test case categories specific to domains (e.g., API testing, data processing)
- Mistakes made when writing tests (what to avoid)
- Coverage strategies that proved effective

**When to extract:**
- After writing tests for 3+ similar projects or modules
- When discovering reusable test pattern
- When encountering framework-specific edge cases
- After learning better testing practices from code review
- When same testing challenge appears multiple times

**How to extract:**
- Add proven test patterns to references/test_patterns.md
- Document framework gotchas in references/framework_guides.md
- Update SKILL.md examples with real anonymized cases
- Create references/domain-testing.md for domain-specific patterns
- Add anti-patterns to references/common-mistakes.md

## Usage Notes

**When to use test-writer:**
- Just finished writing a function
- Adding test coverage to existing code
- Refactoring and need regression tests
- Setting up testing infrastructure

**When NOT to use:**
- Code is trivial (simple getter/setter)
- Testing third-party libraries
- Already have comprehensive tests
- Code is temporary/prototype

**Relationship to other skills:**
- **error-logger**: Tests prevent errors; error logs inform test cases
- **knowledge-extractor**: Can analyze test patterns for extraction
- **skill-updater**: Updates this skill with new test patterns

## Related Skills

- **error-logger**: Error patterns inform edge case testing
- **knowledge-extractor**: Extracts reusable test patterns
- **code-review-skill** (future): Could integrate test quality checks
