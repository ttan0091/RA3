---
id: SKL-enterprise-ENTERPRISERBACMODELS
name: Enterprise Rbac Models
description: Enterprise RBAC (Role-Based Access Control) provides a scalable, auditable,
  and secure approach to managing user permissions through role-based assignments.
  This skill covers implementing hierarchical
version: 1.0.0
status: active
owner: '@cerebra-team'
last_updated: '2026-02-22'
category: Backend
tags:
- api
- backend
- server
- database
stack:
- Python
- Node.js
- REST API
- GraphQL
difficulty: Intermediate
---

# Enterprise Rbac Models

## Skill Profile
*(Select at least one profile to enable specific modules)*
- [ ] **DevOps**
- [x] **Backend**
- [ ] **Frontend**
- [ ] **AI-RAG**
- [ ] **Security Critical**

## Overview
Enterprise RBAC (Role-Based Access Control) provides a scalable, auditable, and secure approach to managing user permissions through role-based assignments. This skill covers implementing hierarchical roles, custom permissions, multi-level access control (organization, project, resource), and integration with SSO for enterprise applications.

## Why This Matters
- **Scalability**: Manage thousands of users with role-based assignments instead of individual permissions
- **Security Compliance**: Meet enterprise security requirements (SOC2, ISO 27001) with audit trails and least privilege
- **Operational Efficiency**: Automate onboarding/offboarding through role assignments and SSO integration
- **Flexibility**: Support custom roles, hierarchical inheritance, and multi-level access control

---

## Core Concepts & Rules

### 1. Core Principles
- Follow established patterns and conventions
- Maintain consistency across codebase
- Document decisions and trade-offs

### 2. Implementation Guidelines
- Start with the simplest viable solution
- Iterate based on feedback and requirements
- Test thoroughly before deployment


## Inputs / Outputs / Contracts
* **Inputs**:
  - User identity (email, user ID)
  - SSO assertion (groups, attributes)
  - Role assignment requests
  - Permission check requests (userId, permission, resourceId)
* **Entry Conditions**:
  - Database initialized with users, roles, permissions tables
  - Authentication system implemented (SSO or local)
  - Role hierarchy defined
* **Outputs**:
  - Permission check result (true/false)
  - User roles and permissions
  - Audit logs for role changes and access attempts
  - Access review reports
* **Artifacts Required (Deliverables)**:
  - Database schema (users, roles, permissions, user_roles, role_permissions)
  - Permission checking middleware
  - Role management API endpoints
  - UI components for conditional rendering
  - Audit logging implementation
* **Acceptance Evidence**:
  - Test suite covering all roles and permissions
  - API endpoint permission enforcement tests
  - UI component visibility tests
  - Audit log verification
* **Success Criteria**:
  - All API endpoints properly enforce permissions
  - UI correctly shows/hides elements based on permissions
  - Role inheritance works correctly
  - SSO group-to-role mapping functions
  - Audit logs capture all permission changes

## Skill Composition
* **Depends on**: Authentication (SSO, SAML, OIDC), Database Design
* **Compatible with**: SCIM Provisioning, Security Questionnaires, Vendor Onboarding
* **Conflicts with**: None
* **Related Skills**: [SSO (SAML & OIDC)](file://50-enterprise-integrations/sso-saml-oidc/SKILL.md), [SCIM Provisioning](file://50-enterprise-integrations/scim-provisioning/SKILL.md)

---

## Quick Start / Implementation Example

1. Review requirements and constraints
2. Set up development environment
3. Implement core functionality following patterns
4. Write tests for critical paths
5. Run tests and fix issues
6. Document any deviations or decisions

```python
# Example implementation following best practices
def example_function():
    # Your implementation here
    pass
```


## Assumptions / Constraints / Non-goals

* **Assumptions**:
  - Development environment is properly configured
  - Required dependencies are available
  - Team has basic understanding of domain
* **Constraints**:
  - Must follow existing codebase conventions
  - Time and resource limitations
  - Compatibility requirements
* **Non-goals**:
  - This skill does not cover edge cases outside scope
  - Not a replacement for formal training


## Compatibility & Prerequisites

* **Supported Versions**:
  - Python 3.8+
  - Node.js 16+
  - Modern browsers (Chrome, Firefox, Safari, Edge)
* **Required AI Tools**:
  - Code editor (VS Code recommended)
  - Testing framework appropriate for language
  - Version control (Git)
* **Dependencies**:
  - Language-specific package manager
  - Build tools
  - Testing libraries
* **Environment Setup**:
  - `.env.example` keys: `API_KEY`, `DATABASE_URL` (no values)


## Test Scenario Matrix (QA Strategy)

| Type | Focus Area | Required Scenarios / Mocks |
| :--- | :--- | :--- |
| **Unit** | Core Logic | Must cover primary logic and at least 3 edge/error cases. Target minimum 80% coverage |
| **Integration** | DB / API | All external API calls or database connections must be mocked during unit tests |
| **E2E** | User Journey | Critical user flows to test |
| **Performance** | Latency / Load | Benchmark requirements |
| **Security** | Vuln / Auth | SAST/DAST or dependency audit |
| **Frontend** | UX / A11y | Accessibility checklist (WCAG), Performance Budget (Lighthouse score) |


## Technical Guardrails & Security Threat Model

### 1. Security & Privacy (Threat Model)
* **Top Threats**: Injection attacks, authentication bypass, data exposure
- [ ] **Data Handling**: Sanitize all user inputs to prevent Injection attacks. Never log raw PII
- [ ] **Secrets Management**: No hardcoded API keys. Use Env Vars/Secrets Manager
- [ ] **Authorization**: Validate user permissions before state changes

### 2. Performance & Resources
- [ ] **Execution Efficiency**: Consider time complexity for algorithms
- [ ] **Memory Management**: Use streams/pagination for large data
- [ ] **Resource Cleanup**: Close DB connections/file handlers in finally blocks

### 3. Architecture & Scalability
- [ ] **Design Pattern**: Follow SOLID principles, use Dependency Injection
- [ ] **Modularity**: Decouple logic from UI/Frameworks

### 4. Observability & Reliability
- [ ] **Logging Standards**: Structured JSON, include trace IDs `request_id`
- [ ] **Metrics**: Track `error_rate`, `latency`, `queue_depth`
- [ ] **Error Handling**: Standardized error codes, no bare except
- [ ] **Observability Artifacts**:
    - **Log Fields**: timestamp, level, message, request_id
    - **Metrics**: request_count, error_count, response_time
    - **Dashboards/Alerts**: High Error Rate > 5%


## Agent Directives & Error Recovery
*(ข้อกำหนดสำหรับ AI Agent ในการคิดและแก้ปัญหาเมื่อเกิดข้อผิดพลาด)*

- **Thinking Process**: Analyze root cause before fixing. Do not brute-force.
- **Fallback Strategy**: Stop after 3 failed test attempts. Output root cause and ask for human intervention/clarification.
- **Self-Review**: Check against Guardrails & Anti-patterns before finalizing.
- **Output Constraints**: Output ONLY the modified code block. Do not explain unless asked.


## Definition of Done (DoD) Checklist

- [ ] Tests passed + coverage met
- [ ] Lint/Typecheck passed
- [ ] Logging/Metrics/Trace implemented
- [ ] Security checks passed
- [ ] Documentation/Changelog updated
- [ ] Accessibility/Performance requirements met (if frontend)


## Anti-patterns / Pitfalls

* ⛔ **Don't**: Log PII, catch-all exception, N+1 queries
* ⚠️ **Watch out for**: Common symptoms and quick fixes
* 💡 **Instead**: Use proper error handling, pagination, and logging


## Reference Links & Examples

* Internal documentation and examples
* Official documentation and best practices
* Community resources and discussions


## Versioning & Changelog

* **Version**: 1.0.0
* **Changelog**:
  - 2026-02-22: Initial version with complete template structure

