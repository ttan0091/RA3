---
name: seed-data
description: Seed database with test assessment data for development. Use when setting up a fresh environment or resetting test data.
disable-model-invocation: true
allowed-tools: Bash
argument-hint: "[clean]"
---

# Seed Test Data

Seed the database with test data for development.

## Available Commands

### Standard Seed
```bash
npm run seed:test
```
Adds test data without removing existing data.

### Clean and Reseed
```bash
npm run seed:test:clean
```
Removes existing test data and reseeds. Use when data is corrupted or needs reset.

## What Gets Seeded

1. **Assessment Types** - All 12 resilience domains
2. **Assessment Sections** - Sections for each domain
3. **Assessment Questions** - Full question set with weights
4. **Benchmarks** - Industry benchmark data
5. **Test Sessions** - Sample completed assessments
6. **Test Scores** - Pre-calculated scores for testing

## Usage

If `$ARGUMENTS` is "clean":
```bash
npm run seed:test:clean
```

Otherwise:
```bash
npm run seed:test
```

## Manual Seeding

For specific data:
```bash
# Seed only questions
npx ts-node scripts/seed-questions.ts

# Seed only benchmarks
npx ts-node scripts/seed-benchmarks.ts
```

## Verification

After seeding, verify:
```bash
# Check question count
curl http://localhost:3000/api/assessment-types | jq '.[].question_count'

# Check sections loaded
curl http://localhost:3000/api/assessment-sections/operational-resilience | jq 'length'
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Duplicate key error | Run with `clean` flag |
| Foreign key violation | Seed in correct order (types → sections → questions) |
| RLS blocking inserts | Use service role or disable RLS temporarily |
| Missing env vars | Check `.env.local` has Supabase keys |

## Output

Report:
- Tables seeded
- Record counts
- Any errors
- Verification results
