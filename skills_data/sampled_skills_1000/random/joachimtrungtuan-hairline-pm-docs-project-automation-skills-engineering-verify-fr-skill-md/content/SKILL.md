---
name: verify-fr
description: Verify functional requirement documents against constitution principles, system PRD consistency, client transcription intent, and dependency integrity. Supports single FR or multiple interconnected FRs from the same product with cross-FR consistency analysis. Use when asked to review FR specifications for gaps, contradictions, quality issues, or cross-FR consistency and return a concise issue report.
---

# Verify FR

## Purpose

Verify FR specifications through incremental section analysis and evidence-based cross-checking. Output the report directly to the user — do not create files.

## Modes

- **Single FR**: Verify one FR specification
- **Multi-FR**: Verify multiple interconnected FRs from the same product — each analyzed individually, then cross-checked against each other for consistency, conflicts, and shared dependency issues

## Required Input

At least one FR identifier, normalized to `FR-###`.

Accepted formats: `FR-001`, `FR001`, `fr-001`, `001`

For multi-FR mode, accept a list (e.g., "FR-001, FR-003, FR-007").

If no FR is provided, ask before proceeding.

## Hard Rules

- Process PRD structure first, then sections one-by-one — never load full PRD at once
- Re-grep evidence before final output to avoid unsupported claims
- Output report only — do not create files
- In multi-FR mode, complete individual analysis of each FR before cross-checking

## Progress Tracking (Mandatory)

**Before starting work**, create a checklist of all workflow steps below. Mark each step in-progress when starting and completed when done. Use the platform's task/todo tracking tools (task lists, todo items, progress trackers). This prevents step-skipping and keeps the workflow auditable.

## Workflow (Single FR)

### 1. Parse FR and initialize tracking

Extract FR number, normalize to `FR-###`. Use the platform's task/todo tracking tool to create a step checklist covering: parse, structure scan, reference loading, **[PLACEHOLDER — PRD sections added in Step 2]**, dependency checks, draft report, post-verification, final output. Do not add per-section items yet — they are added after Step 2 replaces the placeholder.

### 2. Inspect PRD structure

1. Locate `local-docs/project-requirements/functional-requirements/fr###-*/prd.md`
2. Extract H2 headers only (with line numbers)
3. **MANDATORY**: Use the platform's task/todo tracking tool to add one tracking item per H2 section found — replacing the placeholder from Step 1. Every section must appear as its own item (e.g., "Analyze PRD: Overview", "Analyze PRD: Workflows", "Analyze PRD: Screen Specifications"). Do not proceed to Step 3 until all PRD sections are in the todo list.

### 3. Load minimal references

- Full constitution: `.specify/memory/constitution.md`
- FR-specific section from `local-docs/project-requirements/system-prd.md`
- Transcription file paths under `local-docs/project-requirements/transcriptions/` (store paths only; load content via targeted grep per section)

### 4. Analyze sections incrementally

For each PRD section:

1. Mark section tracking item in-progress
2. Load only that section's line range
3. Run fresh searches in constitution, system PRD, and transcriptions
4. Evaluate against these criteria:

**A. Constitution Alignment**

- Multi-tenant, API-first, modularity compliance
- Security requirements (auth, encryption, audit trail)
- Performance and testing standards
- Flag: specification contradicts or omits constitution principles

**B. Cross-Document Consistency**

- Module identifiers match system PRD
- FR references and business rules are consistent
- Dependencies properly documented
- Flag: document contradictions, mismatched IDs, incorrect references

**C. Client Requirement Traceability**

- Each requirement traceable to transcriptions
- No client requirements missing from specification
- Workflows match client's described intent
- Flag: missing requirements or misinterpretations

**D. Specification Completeness**

- Requirements clear and unambiguous
- Edge cases, error scenarios, validations documented
- Acceptance criteria testable
- Data models and interfaces specified
- Flag: incomplete, vague, or contradictory specifications

**E. Screen Field Provenance** (for UI/screen sections only)

**CRITICAL**: Every field in a screen specification must have a documented origin.

Valid provenance types:

| Source | Example |
|--------|---------|
| User input | Form field, text input, selection |
| System calculated | Formula, computation, derived value |
| Database/API retrieved | Backend data fetch |
| Previous screen/step | Data carried from earlier in this FR's workflow |
| Inherited from dependent FR | Field defined in another FR (must document which FR) |
| Default/preset value | Documented default |
| Session/context data | User profile, tenant info |

Validation method:

1. List all fields in the screen specification
2. Grep current FR's PRD for field definition and source
3. Grep current FR's workflows for data flow
4. If no source found, grep dependent FRs for field origin
5. If inherited, verify inheritance is documented (e.g., "field X from FR-###")
6. Mark as **orphaned** only if no provenance found in current FR or dependent FRs

Flag orphaned fields as **critical**.

5. Record issues with severity
6. Clear section context and continue to next

### 5. Cross-check dependencies

For each dependent FR from system PRD:

1. Extract dependency definitions
2. **Business rule conflicts**: contradictory validation, state transitions, calculations, authorization
3. **Data field conflicts**: type mismatches, format conflicts, required vs optional, length/size, enum value differences
4. **Shared component alignment**: API contracts, module boundaries
5. Flag integration-breaking contradictions as critical

### 6. Compile issue report

Group by severity, deduplicate, prioritize by impact.

Generate 3+ solution options per issue with pros, cons, and effort estimate.

### 7. Post-verify every claim

Re-run targeted searches for each issue:

- Keep only evidence-backed findings
- Remove unsupported findings
- Downgrade severity when evidence is weaker than claimed

### 8. Output final report

Return verified report text to user. Do not write files.

## Workflow Extension: Multi-FR Mode

When verifying multiple interconnected FRs:

### Phase 1: Individual verification

Run Steps 1–7 for each FR separately. Maintain per-FR issue lists.

### Phase 2: Cross-FR consistency analysis

After all individual verifications:

1. **Shared data model consistency**: verify data entities referenced across FRs use consistent field names, types, formats, and validation rules
2. **Workflow integration points**: verify handoff points between FRs are complete (FR-A output matches FR-B expected input)
3. **Business rule coherence**: check that rules across FRs don't contradict (e.g., different approval thresholds for the same entity)
4. **Module boundary alignment**: verify FRs don't make conflicting assumptions about which module owns a capability
5. **Dependency graph integrity**: check for circular dependencies, missing dependencies, or version conflicts

### Phase 3: Combined report

Output one report covering:

- Per-FR issues (from Phase 1)
- Cross-FR issues (from Phase 2)
- Overall product consistency assessment

## Report Template

```markdown
# FR Verification Report

**FR(s)**: FR-### [, FR-###, ...]
**Priority**: P#
**Modules**: P-##, PR-##, A-##
**Status**: Verified with Issues / Clean

---

## CRITICAL ISSUES

### Issue #1: [Title]
**FR**: FR-### (or Cross-FR)
**Description**: [1-2 sentences]
**Impact**: [What breaks or risks]

**Solutions**:
1. **[Option A]**: [Desc] | Pros: [X] | Cons: [Y] | Effort: Low/Med/High
2. **[Option B]**: [Desc] | Pros: [X] | Cons: [Y] | Effort: Low/Med/High
3. **[Option C]**: [Desc] | Pros: [X] | Cons: [Y] | Effort: Low/Med/High

---

## MEDIUM ISSUES
[Same format]

---

## MINOR ISSUES
[Same format]

---

## SUMMARY

**Total Issues**: X Critical, Y Medium, Z Minor
**Constitution Compliance**: Pass/Fail
**Client Alignment**: assessment
**Dependencies**: Status
**Cross-FR Consistency**: assessment (multi-FR mode only)

**Recommendation**: [Next action]
```

Report length: under 300 words for single-FR, under 500 words for multi-FR.

## Severity Guidance

- **Critical**: constitution violations, missing client must-haves, orphaned UI fields without provenance, dependency rule/data conflicts that break integration, cross-FR business rule contradictions
- **Medium**: incomplete specs, inconsistent field formats/names, missing edge cases, minor cross-FR inconsistencies
- **Minor**: clarity and documentation quality gaps

## Search Commands Reference

**Constitution**:

```bash
rg -i "architecture|security|performance|testing" .specify/memory/constitution.md
rg -A 10 "NON-NEGOTIABLE" .specify/memory/constitution.md
```

**System PRD**:

```bash
rg -A 50 "## FR-###" local-docs/project-requirements/system-prd.md
rg -i "module|priority|dependency" local-docs/project-requirements/system-prd.md
```

**Transcriptions**:

```bash
rg -i "keyword" local-docs/project-requirements/transcriptions/*.txt
rg -C 5 "keyword" local-docs/project-requirements/transcriptions/*.txt
```

**PRD section loading**:

```bash
rg -n "^## " local-docs/project-requirements/functional-requirements/fr###-*/prd.md
```

**Screen field provenance**:

```bash
rg -i "field|input|textbox|dropdown|checkbox|button" fr###-*/prd.md
rg -i "calculated|derived|user input|database|api|retrieved" fr###-*/prd.md
rg -i "pass|carry|transfer|populate|data flow" fr###-*/prd.md
```

**Dependency conflict check**:

```bash
rg -A 20 "Business Rules|Validation|Constraints|Rules" fr###-*/prd.md
rg -i "field|column|attribute|parameter|data type" fr###-*/prd.md
rg -A 10 "Data Model|API Schema|Database|Table" fr###-*/prd.md
```

## Error Handling

If verification cannot be completed:

- Document missing files/sections in report
- Note incomplete dependencies
- Mark uncertain areas with [UNVERIFIED] tag
- Provide partial analysis with caveats
- List additional info needed

## Quality Checklist

Before final output, confirm:

- [ ] All PRD sections analyzed individually
- [ ] Fresh searches performed per section
- [ ] Screen field provenance checked for all UI sections
- [ ] Dependency business rule conflicts checked
- [ ] Dependency data field conflicts checked
- [ ] All findings verified in post-check
- [ ] Each issue has 3+ solution options
- [ ] Report within word limit
- [ ] No unsupported claims
- [ ] Cross-FR consistency checked (multi-FR mode)
