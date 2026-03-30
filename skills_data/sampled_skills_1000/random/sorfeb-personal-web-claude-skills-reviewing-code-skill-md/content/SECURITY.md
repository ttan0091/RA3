# Security Review Checklist

## Input Validation

```
- [ ] All tRPC inputs use Zod schemas
- [ ] String lengths constrained (min/max)
- [ ] Arrays have size limits
- [ ] UUIDs validated with z.string().uuid()
- [ ] Enums use z.enum() not z.string()
- [ ] No user input in SQL/queries (use Prisma)
```

## Authentication

```
- [ ] Protected routes use protectedProcedure
- [ ] Session checked before sensitive operations
- [ ] No auth bypass in conditional logic
- [ ] Token/session expiry handled
```

## Authorization

```
- [ ] Resource ownership verified before update/delete
- [ ] userId from session, not from input
- [ ] Admin operations have role checks
- [ ] No horizontal privilege escalation
```

## Data Exposure

```
- [ ] Passwords never returned in queries
- [ ] Sensitive fields excluded from select()
- [ ] Error messages don't expose internals
- [ ] Stack traces not sent to client
- [ ] No PII in console.log statements
```

## Environment Variables

```
- [ ] DATABASE_URL not hardcoded
- [ ] API keys not in source code
- [ ] Secrets only from process.env
- [ ] .env files in .gitignore
```

## Dependency Security

```
- [ ] New deps approved by user
- [ ] No known vulnerabilities (npm audit)
- [ ] Minimal dependency footprint
- [ ] No abandoned packages
```

## Client-Side Security

```
- [ ] No sensitive data in localStorage
- [ ] No dynamic code execution functions
- [ ] User-generated content escaped
- [ ] No raw HTML injection with user input
```

## Common Vulnerabilities

| Risk | Check | Prevention |
|------|-------|------------|
| SQL Injection | Raw queries | Always use Prisma ORM |
| XSS | HTML rendering | Escape user content |
| CSRF | Form submissions | Use tRPC (handles this) |
| Auth bypass | Session checks | protectedProcedure |
| Data leak | Error messages | Generic client errors |