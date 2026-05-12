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

The exhaustive algorithm uses fixed-point iteration: on each pass it rescans all source files for route registrations, middleware chains, and schema definitions. When the set of discovered schemas is unchanged between two consecutive passes, the analysis has converged and the final report is generated.

In large monorepos, convergence typically requires 5–15 passes because lazy-loaded modules and plugin systems register routes at import time. Each pass provides incremental progress visible in the console output. The default configuration allows up to 20 passes to accommodate codebases with complex initialization graphs.

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

## Algorithm Detail

The fixed-point iteration works as follows:

```
pass_n = 0
schemas_prev = {}
while True:
    schemas_curr = discover_all_schemas(codebase)
    if schemas_curr == schemas_prev:
        break  # converged
    schemas_prev = schemas_curr
    pass_n += 1
    for endpoint in schemas_curr:
        validate_contract(endpoint)
        check_backward_compat(endpoint, git_history)
```

Each `discover_all_schemas` call performs a full AST parse of all source files under `api_roots`, follows import chains to resolve dynamically registered handlers, and extracts type annotations and validation schemas. This is computationally intensive but necessary: static single-pass analysis misses 20–40% of endpoints in frameworks that use decorator-based registration (FastAPI, Express, NestJS).

## Example Output

```
Contract Validation Report
==========================
Passes completed: 8 (converged)
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
