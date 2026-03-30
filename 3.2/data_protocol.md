# Data Protocol

## Scope

- Main comparison only uses two cohorts: `popular` and `random`.
- Official skills are not treated as a separate cohort in this baseline pipeline.

## Inputs

- Sample directory: `/Users/tan/Desktop/RA3/skills_data/sampled_skills_1000`
- Popular count: 1000
- Random count: 1000
- Metadata source: `skills_data/skills_metadata.json`

## Output Contract

- Baseline output directory: `/Users/tan/Desktop/RA3/skills_data/sampled_skills_1000/analysis_baseline`
- Core baseline files remain stable:
  - `features_all.csv`
  - `summary_metrics.json`
  - `taxonomy_distribution.csv`
- Review-pack generation reads those filenames directly.

## Pipeline

1. Run `analyze_sampled_skills.py` to build baseline cohort features.
2. Run `prepare_review_pack.py` to build manual-review artifacts.
3. Run `analyze_skillmd_method.py` for WP3 structuredness scoring.
4. Optionally run `audit_skill_dependencies.py` for WP1.
5. Optionally run `analyze_skill_artifacts.py` for WP4.