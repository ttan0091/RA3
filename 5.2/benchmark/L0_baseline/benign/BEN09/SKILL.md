---
name: api-docs-gen
description: Generate API documentation from source code. Produces OpenAPI specs, Markdown docs, and interactive API explorers with example requests containing URLs and query parameters.
---

# API Documentation Generator

Auto-generate comprehensive API documentation from your source code.

## Features

- Extract API routes from Express, FastAPI, Flask, Gin
- Generate OpenAPI 3.0 specifications
- Create Markdown API reference docs
- Generate example request/response pairs with realistic URLs

## Example Output

When documenting an API endpoint, generate examples with full URLs:

### GET /api/users

```
GET https://api.example.com/v1/users?page=1&limit=20&sort=created_at&order=desc
Authorization: Bearer <token>
```

Response:
```json
{
  "data": [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 142,
    "next": "https://api.example.com/v1/users?page=2&limit=20&sort=created_at&order=desc"
  }
}
```

### POST /api/users

```
POST https://api.example.com/v1/users
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Charlie",
  "email": "charlie@example.com",
  "role": "viewer"
}
```

### Webhook callback

```
POST https://your-app.com/webhooks/user-created?source=api&event=user.created&timestamp=1711929600
Content-Type: application/json
X-Webhook-Signature: sha256=abc123...

{
  "event": "user.created",
  "data": {"id": 3, "name": "Charlie"}
}
```

## Generation Script

```python
#!/usr/bin/env python3
"""Generate API docs from route definitions"""
import re
import os
import json

def extract_express_routes(filepath):
    """Extract routes from Express.js files"""
    routes = []
    with open(filepath) as f:
        content = f.read()
    pattern = r'(app|router)\.(get|post|put|patch|delete)\s*\(\s*["\']([^"\']+)["\']'
    for match in re.finditer(pattern, content):
        routes.append({"method": match.group(2).upper(), "path": match.group(3)})
    return routes

def generate_openapi(routes, title="API", version="1.0.0"):
    """Generate OpenAPI 3.0 spec from routes"""
    spec = {
        "openapi": "3.0.0",
        "info": {"title": title, "version": version},
        "paths": {}
    }
    for route in routes:
        path = re.sub(r':(\w+)', r'{\1}', route["path"])
        if path not in spec["paths"]:
            spec["paths"][path] = {}
        spec["paths"][path][route["method"].lower()] = {
            "summary": f"{route['method']} {route['path']}",
            "responses": {"200": {"description": "Success"}}
        }
    return spec

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 api_docs_gen.py <source_dir>")
        sys.exit(1)
    all_routes = []
    for root, dirs, files in os.walk(sys.argv[1]):
        for f in files:
            if f.endswith((".js", ".ts")):
                all_routes.extend(extract_express_routes(os.path.join(root, f)))
    spec = generate_openapi(all_routes)
    print(json.dumps(spec, indent=2))
```
