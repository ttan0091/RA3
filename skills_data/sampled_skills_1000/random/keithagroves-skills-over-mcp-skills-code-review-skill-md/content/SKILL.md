---
name: code-review
description: Performs thorough code reviews focusing on correctness, security, performance, and maintainability. Use when reviewing pull requests, examining code changes, or auditing existing code.
metadata:
  author: mcp-tests
  version: "1.0"
---

# Code Review Skill

This skill guides you through performing comprehensive code reviews.

## When to Use

- Reviewing pull requests or merge requests
- Auditing existing code for issues
- Evaluating code quality before deployment
- Mentoring developers through code feedback

## Review Process

### 1. Understand the Context

Before reviewing code:
- Read the PR description or commit message
- Understand the purpose of the change
- Check related issues or tickets

### 2. Check for Correctness

- Does the code do what it's supposed to do?
- Are edge cases handled?
- Are there any logic errors?
- Do the tests cover the new functionality?

### 3. Security Review

Look for common vulnerabilities:
- SQL injection (parameterized queries?)
- XSS (input sanitization, output encoding?)
- Authentication/authorization issues
- Sensitive data exposure
- Insecure dependencies

### 4. Performance Considerations

- N+1 queries or inefficient database access
- Unnecessary loops or computations
- Memory leaks or excessive allocations
- Missing indexes for database queries

### 5. Code Quality

- Is the code readable and well-organized?
- Are variable/function names descriptive?
- Is there appropriate error handling?
- Is the code DRY (Don't Repeat Yourself)?
- Are there any code smells?

### 6. Maintainability

- Is the code easy to modify?
- Are there sufficient comments for complex logic?
- Does it follow project conventions?
- Is the test coverage adequate?

## Feedback Guidelines

When providing feedback:
- Be specific and constructive
- Explain the "why" behind suggestions
- Differentiate between blocking issues and suggestions
- Acknowledge good practices you see

## Example Review Comment

```
**Issue: Potential SQL Injection**

The query on line 42 concatenates user input directly:
`query = "SELECT * FROM users WHERE id = " + userId`

This is vulnerable to SQL injection. Please use parameterized queries:
`query = "SELECT * FROM users WHERE id = ?", [userId]`
```

## Additional Resources

For detailed guidance, see:
- [Security Checklist](references/SECURITY.md) - Comprehensive security review checklist
- [check-complexity.py](scripts/check-complexity.py) - Script to analyze code complexity
