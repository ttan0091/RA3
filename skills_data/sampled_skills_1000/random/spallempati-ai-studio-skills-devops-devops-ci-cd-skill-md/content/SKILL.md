---
name: devops-ci-cd
description: |
  DevOps and CI/CD pipeline standards. Use when writing GitHub Actions workflows,
  configuring CI pipelines, or managing deployment artifacts. Covers build-once
  promotion, secrets management, image signing, and concurrency controls.
disposition: contextual
filePatterns:
  - ".github/workflows/**"
  - "azure-pipelines.yml"
  - "azure-pipelines/**"
  - "**/buildspec.yml"
  - "**/buildspec.yaml"
  - "**/appspec.yml"
  - "**/appspec.yaml"
compliance:
  - soc2: CC7.3
version: 1.0.0
---

1. **MUST** build once per commit; promote the artefact through environments.
2. **MUST** store secrets only in GitHub Secrets / OIDC-assumed role; never in
   plain YAML.
3. **SHOULD** run workflow concurrency groups to cap parallel jobs per repo.
4. **MUST** tag all images `repo:sha-short` and sign them (cosign).
