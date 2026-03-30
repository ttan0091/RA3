# R2R Semantic Search Strategies

This reference provides patterns for using R2R hybrid search to gather context from documentation collections during prompt enrichment research.

## Table of Contents

- [Overview](#overview)
- [Collection Architecture](#collection-architecture)
- [Search Commands](#search-commands)
- [Search Patterns by Prompt Type](#search-patterns-by-prompt-type)
- [Integration with Other Research](#integration-with-other-research)
- [Best Practices](#best-practices)

## Overview

R2R (RAG to Riches) provides semantic search across documentation collections. Unlike keyword-based search, R2R uses hybrid search combining:
- **Semantic search** (weight 5.0): Understands meaning and context
- **Keyword search** (weight 1.0): Matches exact terms

This makes it powerful for finding relevant documentation even when exact terms don't match.

### When to Use R2R Search

**Use R2R when:**
- Looking for best practices and patterns
- Finding framework/library documentation
- Searching for implementation examples
- Getting context from project-specific documentation
- Need semantic understanding (not just keyword matching)

**Don't use R2R when:**
- Searching specific code in codebase (use Grep/Glob instead)
- Need real-time web information (use WebSearch)
- Looking for specific file paths (use Glob)

## Collection Architecture

R2R uses a 3-tier collection system:

### Tier 1: Universal Collections
Contains general programming knowledge applicable to any project.

```text
r2r-research-universal
├── Programming patterns
├── Git workflows
├── Testing strategies
├── Debugging techniques
└── Code review practices
```

### Tier 2: Tech Stack Collections
Auto-detected based on query content.

**Languages:**
- `lang-python` - Python patterns, stdlib, best practices
- `lang-typescript` - TypeScript patterns, type system
- `lang-go` - Go idioms, concurrency patterns

**Frameworks:**
- `framework-react` - React hooks, components, state management
- `framework-nextjs` - Next.js routing, SSR, API routes
- `framework-fastapi` - FastAPI endpoints, dependency injection

**Databases:**
- `db-postgresql` - PostgreSQL queries, optimization
- `db-mongodb` - MongoDB aggregation, schema design
- `db-redis` - Redis caching patterns

**Tools:**
- `tools-docker` - Dockerfile patterns, compose
- `tools-kubernetes` - K8s manifests, deployments
- `tools-git` - Git workflows, branching strategies

### Tier 3: Project Collections
Project-specific documentation (CLAUDE.md, docs/, examples/).

```text
{project-name}
├── Project CLAUDE.md content
├── Architecture documentation
├── API documentation
└── Code examples
```

## Search Commands

### Basic Search

```bash
# Semantic search with auto-collection selection
r2r-research search "React authentication patterns"

# Output: text (default), json, markdown
r2r-research search "query" --format json

# Limit results
r2r-research search "query" --limit 5
```

### Targeted Collection Search

```bash
# Search specific collection
r2r-research search "hooks" -c framework-react

# Search multiple collections
r2r-research search "error handling" -c lang-python -c framework-fastapi
```

### List Available Collections

```bash
r2r-research collections
```

### Get Collection Info

```bash
r2r-research info collection-id
```

## Search Patterns by Prompt Type

### Pattern 1: Feature Implementation

**Prompt:** "add authentication"

**R2R Research:**
```bash
# Search for auth patterns in tech stack
r2r-research search "authentication implementation patterns"

# If Node.js/Express detected
r2r-research search "Express.js JWT authentication" -c framework-express

# If React frontend
r2r-research search "React authentication state management" -c framework-react
```

**Expected findings:**
- JWT vs session approaches
- Middleware patterns
- State management strategies
- Security best practices

### Pattern 2: Bug Investigation

**Prompt:** "fix the error"

**R2R Research:**
```bash
# Search for error handling patterns
r2r-research search "error handling debugging strategies"

# Tech-specific error patterns
r2r-research search "TypeScript error handling try catch" -c lang-typescript
```

**Expected findings:**
- Common error patterns
- Debugging strategies
- Logging best practices
- Error recovery patterns

### Pattern 3: Refactoring

**Prompt:** "refactor the code"

**R2R Research:**
```bash
# Search for refactoring patterns
r2r-research search "code refactoring patterns clean code"

# Architecture patterns
r2r-research search "SOLID principles dependency injection"
```

**Expected findings:**
- Design patterns
- Code organization
- Abstraction strategies
- Testing considerations

### Pattern 4: Performance Optimization

**Prompt:** "make it faster"

**R2R Research:**
```bash
# General optimization
r2r-research search "performance optimization profiling"

# Database optimization
r2r-research search "query optimization indexing" -c db-postgresql

# Frontend optimization
r2r-research search "React performance memoization" -c framework-react
```

**Expected findings:**
- Profiling techniques
- Caching strategies
- Query optimization
- Bundle optimization

### Pattern 5: Testing

**Prompt:** "add tests"

**R2R Research:**
```bash
# Testing patterns
r2r-research search "unit testing integration testing patterns"

# Framework-specific
r2r-research search "Jest React testing library" -c framework-react
r2r-research search "pytest fixtures mocking" -c lang-python
```

**Expected findings:**
- Test structure patterns
- Mocking strategies
- Coverage approaches
- Integration test patterns

## Integration with Other Research

### Combined Research Flow

```bash
Research Plan for "implement caching":

1. Conversation history - Check for prior discussion
2. Codebase exploration:
   - Glob: "**/cache*.ts" - Find existing cache code
   - Grep: "redis|memcache|cache" - Find cache usage
3. R2R semantic search:
   - r2r-research search "caching strategies patterns"
   - r2r-research search "Redis caching Node.js" -c tools-redis
4. Web research (if needed):
   - WebSearch: "Redis vs Memcached 2024 comparison"
5. Document findings
```

### R2R vs Other Tools

| Tool | Best For | R2R Advantage |
|------|----------|---------------|
| Grep | Exact code patterns | Semantic understanding |
| Glob | File discovery | N/A (different purpose) |
| WebSearch | Current news/trends | Curated documentation |
| WebFetch | Specific URLs | Pre-indexed, faster |
| Task/Explore | Codebase architecture | External documentation |

### When to Combine

**R2R + Grep:**
```bash
# Find pattern in docs
r2r-research search "repository pattern TypeScript"

# Then find in codebase
grep -r "Repository" src/
```

**R2R + WebSearch:**
```bash
# Get established patterns
r2r-research search "GraphQL authentication"

# Check latest approaches
WebSearch: "GraphQL authentication best practices 2024"
```

## Best Practices

### 1. Query Formulation

**Good queries:**
- "React state management patterns Redux vs Context"
- "PostgreSQL query optimization indexing strategies"
- "TypeScript error handling async await"

**Avoid:**
- Single words: "auth" (too broad)
- Full sentences: "How do I implement authentication in my app?"
- Code snippets: "const handleAuth = () => {}"

### 2. Collection Selection

**Auto-select (default):** Let R2R choose based on query
```bash
r2r-research search "React hooks patterns"
# Auto-selects: universal + framework-react
```

**Manual select:** When you know the domain
```bash
r2r-research search "connection pooling" -c db-postgresql
```

### 3. Result Processing

**For structured output:**
```bash
r2r-research search "query" --format json | jq '.results[].text'
```

**Limit for focused results:**
```bash
r2r-research search "query" --limit 3
```

### 4. Research Documentation

After R2R search, document findings:

```bash
R2R Search Findings:

Query: "React authentication patterns"
Collections: framework-react, universal

Key findings:
1. Context API for auth state (framework-react)
2. Protected route pattern (universal)
3. Token refresh strategies (universal)

Options for user:
- Context API + localStorage
- Redux + cookies
- NextAuth.js (if Next.js)
```

### 5. Fallback Strategy

If R2R returns few results:

1. **Broaden query:** Remove specific terms
2. **Try different collections:** Switch to universal
3. **Use WebSearch:** For current/trending information
4. **Check WebFetch:** For specific documentation URLs

## Configuration

### Environment Variables

Set these for R2R integration:

```bash
# R2R API endpoint
export R2R_RESEARCH_BASE_URL="http://localhost:7272"

# Optional: API key for authenticated access
export R2R_RESEARCH_API_KEY="your-jwt-token"

# Search defaults
export R2R_RESEARCH_DEFAULT_LIMIT=10
```

### Installation

Ensure r2r-research CLI is available:

```bash
# Install from r2r_research_cli
cd /path/to/r2r_research_cli
uv pip install -e .

# Verify installation
r2r-research --help
```

## Summary Checklist

Before finalizing research:

- [ ] Formulated semantic query (not keyword-based)
- [ ] Checked appropriate collections
- [ ] Reviewed top results for relevance
- [ ] Documented key findings
- [ ] Combined with codebase exploration
- [ ] Grounded questions in R2R findings

**Remember:** R2R search provides documentation context. Always combine with codebase exploration (Grep/Glob) for complete picture.
