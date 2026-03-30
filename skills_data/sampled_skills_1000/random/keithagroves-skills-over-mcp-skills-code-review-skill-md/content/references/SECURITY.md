# Security Review Checklist

A detailed checklist for security-focused code reviews.

## Authentication & Authorization

- [ ] Are authentication checks present on all protected endpoints?
- [ ] Is authorization properly enforced (role-based, resource-based)?
- [ ] Are session tokens properly validated?
- [ ] Is there protection against session fixation?
- [ ] Are passwords hashed with a strong algorithm (bcrypt, argon2)?

## Input Validation

- [ ] Is all user input validated on the server side?
- [ ] Are input length limits enforced?
- [ ] Is input type checking performed?
- [ ] Are allowlists used instead of denylists where possible?

## SQL Injection Prevention

- [ ] Are parameterized queries/prepared statements used?
- [ ] Is an ORM being used correctly?
- [ ] Are dynamic query builders avoided or sanitized?

```python
# Bad
query = f"SELECT * FROM users WHERE id = {user_id}"

# Good
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

## XSS Prevention

- [ ] Is output encoding applied to all user-controlled data?
- [ ] Are Content Security Policy headers set?
- [ ] Is innerHTML avoided in favor of textContent?
- [ ] Are template engines configured for auto-escaping?

```javascript
// Bad
element.innerHTML = userInput;

// Good
element.textContent = userInput;
```

## CSRF Protection

- [ ] Are anti-CSRF tokens used for state-changing operations?
- [ ] Is SameSite cookie attribute set?
- [ ] Are custom headers required for API calls?

## Sensitive Data

- [ ] Are secrets stored in environment variables, not code?
- [ ] Is sensitive data encrypted at rest?
- [ ] Is sensitive data masked in logs?
- [ ] Are API keys rotated regularly?

## Dependencies

- [ ] Are dependencies up to date?
- [ ] Are known vulnerable packages avoided?
- [ ] Is there a process for security updates?

## Error Handling

- [ ] Are stack traces hidden from users in production?
- [ ] Do error messages avoid leaking sensitive information?
- [ ] Is logging comprehensive but safe?
