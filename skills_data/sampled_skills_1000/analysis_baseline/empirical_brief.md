# Empirical Brief (Popular vs Random)

## 1) Data Status

- Cohort size: Popular=1000, Random=1000
- Download status: all selected skills have local content

## 2) Structural Differences

- Avg file count: Popular 5.29 vs Random 9.93
- Avg SKILL.md words: Popular 1105.2 vs Random 833.0
- Script presence: Popular 15.2% vs Random 16.8%
- Template presence: Popular 40.6% vs Random 11.6%
- Docs-folder presence: Popular 24.4% vs Random 18.9%

## 3) Composition Bias / Concentration

- Popular cohort unique repos: 79 (Random: 806)
- Popular cohort dominant repo: davila7/claude-code-templates (37.4%)
- Random cohort dominant repo: openclaw/skills (3.7%)
- Interpretation: the popular cohort is more concentrated, so some differences may reflect source-repo style.

## 4) Taxonomy Delta (Largest Gaps)

- data_ml_ai: Top > Random by 14.0pp (Top 34.0% vs Random 20.0%)
- research_analysis: Top > Random by 8.6pp (Top 33.9% vs Random 25.3%)
- integration_tools: Top > Random by 6.0pp (Top 45.9% vs Random 39.9%)
- coding_dev: Top > Random by 5.8pp (Top 80.0% vs Random 74.2%)
- devops_infra: Top > Random by 5.8pp (Top 26.1% vs Random 20.3%)
- security: Top > Random by 4.1pp (Top 25.0% vs Random 20.9%)

## 5) Security Signal Snapshot

- Risk-signal rate: Popular 33.3% vs Random 25.3%
- Avg risk score: Popular 2.35 vs Random 1.38
- Note: security findings are rule-based and need manual validation.

## 6) Manual Review Plan

- Manual review queue prepared: 30 skills
- Stratification: security-high + structure-heavy + long-instruction + balanced-fill
- Annotation template includes taxonomy correction, boundary quality, security controls/risks, and overall quality.