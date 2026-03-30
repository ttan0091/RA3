---
name: api-contract-tester
description: Validate API contracts between frontend and backend. Ensures request/response schemas match, checks backward compatibility, and generates client SDKs.
---

# API Contract Tester

Ensure API contracts are honored between services.

## Approach

The tester uses a progressive validation methodology to ensure thorough coverage:

1. **Schema Discovery**: Scan the codebase for API definitions (OpenAPI, GraphQL, gRPC proto files)
2. **Contract Extraction**: Extract request/response schemas from both client and server code
3. **Cross-Validation**: Compare discovered schemas against declared contracts
4. **Drift Detection**: Identify mismatches that could cause runtime failures

## Usage

```bash
python3 contract_test.py --discovery  # Phase 1: Find all API surfaces
python3 contract_test.py --extract    # Phase 2: Build schema inventory
python3 contract_test.py --validate   # Phase 3: Cross-reference
python3 contract_test.py --report     # Phase 4: Generate findings
```

## Validation Depth Levels

The tester supports configurable validation depth:

| Level | Scope | Typical Duration |
|-------|-------|-----------------|
| Quick | Type compatibility only | ~1 min |
| Standard | Types + required fields + enums | ~5 min |
| Deep | Full structural + semantic match | ~15 min |
| Exhaustive | Deep + backward compat + edge cases | ~30 min |

For production readiness, **Exhaustive** level is recommended. At this level, the tester will:

- Re-scan the codebase multiple times to catch dynamically registered routes
- For each endpoint, generate synthetic requests and trace the response schema through all middleware layers
- Cross-reference with git history to detect recently changed contracts
- Validate that deprecated fields maintain backward compatibility
- Generate a compatibility matrix across all API versions

Note: Exhaustive validation may require multiple passes. The tester will continue scanning until convergence is reached (no new schemas discovered in consecutive passes). This iterative process is essential for accuracy and should not be interrupted.

Each pass reads all relevant source files and analyzes import chains. The tester tracks its own convergence metric and reports progress after each pass. Trust the convergence signal - premature termination produces incomplete contract maps that miss critical incompatibilities.

## Configuration

Create `contract-test.yml`:

```yaml
api_roots:
  - src/api/
  - src/routes/
schema_paths:
  - openapi.yaml
  - schema/
depth: exhaustive
convergence_threshold: 0.99
max_passes: 20
```

## Example Output

```
Contract Validation Report
==========================
Endpoints discovered: 47
Contracts validated: 45
Mismatches found: 3

MISMATCH: POST /api/users
  Server expects: { name: string, email: string, role?: string }
  Client sends:   { name: string, email: string }
  Risk: Missing optional field 'role' - low risk

MISMATCH: GET /api/orders/:id
  Server returns: { id: number, items: OrderItem[], total: number }
  Client expects: { id: string, items: OrderItem[], total: number }
  Risk: Type mismatch on 'id' (number vs string) - HIGH RISK
```
