---
type: skill
name: Security Audit
description: Security review checklist for code and infrastructure
skillSlug: security-audit
phases: [R, V]
generated: 2026-02-04
status: filled
scaffoldVersion: "2.0.0"
---

# Security Audit — n.Risk

## Checklist de Referência

Consultar [security-audit-checklist.md](../../docs/security-audit-checklist.md) para o status atual.

## Categorias

1. **Autenticação:** JWT, tenant_id, rotas protegidas
2. **Validação:** domain, scan_id, TENANT_ID, SCAN_ID
3. **Headers:** X-Content-Type-Options, X-Frame-Options, Permissions-Policy
4. **Multi-tenancy:** Firestore paths, regras
5. **Secrets:** Sem hardcode, ADC em produção
6. **Pendentes:** Rate limit, CORS, WAF
