# SKILL.md Annotation Schema

## Scope

- Target document: the primary `SKILL.md` inside each sampled skill directory.
- Pilot purpose: validate a compact codebook before expanding to full-sample automatic scoring.
- Blind review rule: raters should label from `SKILL.md` content only and ignore cohort, stars, and repo popularity.

## Pilot Sample Design

- Total pilot items: 12
- Cohort split: `popular=6`, `random=6`
- Bucket split within each cohort:
  - `security_high=2`
  - `structure_heavy=2`
  - `instruction_long=2`

## Label Fields

### `has_trigger_condition`

- `1`: the document explicitly states when to use the skill, what problem/context activates it, or prerequisites/preconditions.
- `0`: no explicit usage trigger or precondition statement.

### `has_constraints`

- `1`: the document includes explicit limitations, prohibitions, guardrails, or boundary conditions such as `do not`, `must not`, `avoid`, `only if`, `unless`.
- `0`: no clear constraint or guardrail language.

### `has_error_fallback`

- `1`: the document includes troubleshooting, fallback paths, rollback/retry instructions, or explicit failure handling.
- `0`: no meaningful failure-handling or fallback guidance.

### `has_io_spec`

- `1`: the document clearly specifies expected inputs, required variables/files, output artifacts, or output format/schema.
- `0`: inputs/outputs are absent or too implicit to count.

### `spec_form`

- Allowed labels:
  - `natural_language`
  - `structured_template`
  - `dsl`
  - `code_pseudocode`
  - `logic_math`
  - `mixed`

Decision rule:

- `natural_language`: prose dominates; sections may exist but instructions are mostly paragraph-style.
- `structured_template`: headings, lists, placeholders, and explicit slots/checklists dominate.
- `dsl`: the main instruction style is a domain-specific declarative format or grammar.
- `code_pseudocode`: code blocks, command sequences, or pseudocode are the primary specification vehicle.
- `logic_math`: formulas, symbolic logic, or mathematical notation dominate.
- `mixed`: at least two forms are both substantial and no single form clearly dominates.

### `has_stepwise_procedure`

- `1`: there is a clearly ordered or sequential procedure, either numbered or strongly signaled by sequence words.
- `0`: the file is descriptive/reference-like without a clear procedural flow.

### `example_quality`

- `0`: no meaningful example.
- `1`: minimal example coverage, such as a short snippet or a single shallow example.
- `2`: substantive examples, multiple examples, or worked examples aligned with the procedure.

## Resolved Structuredness Score

Resolved manual score uses this fixed mapping:

- trigger condition: `0/20`
- constraints: `0/20`
- stepwise procedure: `0/15`
- error/fallback: `0/15`
- I/O spec: `0/15`
- example quality: `0/8/15` for `0/1/2`

Total score range: `0-100`

## Adjudication Rule

- Keep both blind ratings.
- If raters disagree, add one adjudicated value per field.
- Kappa is computed on blind ratings only.
- Final `manual_labels.csv` should store `rater_a_*`, `rater_b_*`, and `resolved_*` columns.
