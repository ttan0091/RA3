# Documentation Templates and Checklists

## Table of Contents
1. README Template
2. API Endpoint Template
3. OpenAPI Minimal Skeleton
4. Architecture Overview Template
5. Troubleshooting Article Template
6. Code Comment Checklist

## 1) README Template
```
# Project Name

## Overview
- What this project does and who it is for

## Quickstart
```bash
# minimal working commands
```

## Installation
- Prerequisites
- Setup steps

## Configuration
- Required environment variables
- Optional settings

## Usage
- Common workflows
- Examples

## API (if applicable)
- Base URL
- Auth
- Example request/response

## Development
- Tests
- Linting
- Local run

## Troubleshooting
- Common errors and fixes

## License
```

## 2) API Endpoint Template
```
### {METHOD} {PATH}

**Description:**

**Auth:**

**Request**
- Headers:
- Query params:
- Path params:
- Body:

**Response**
- Status codes:
- Body schema:

**Example**
```bash
curl ...
```

**Notes**
- Pagination
- Rate limits
- Errors
```

## 3) OpenAPI Minimal Skeleton
```
openapi: 3.0.3
info:
  title: API Name
  version: 1.0.0
servers:
  - url: https://api.example.com
paths:
  /health:
    get:
      summary: Health check
      responses:
        '200':
          description: OK
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
```

## 4) Architecture Overview Template
```
# Architecture Overview

## Goals
- Primary goals
- Non-goals

## High-Level Diagram
- Link or ASCII diagram

## Components
- Service A: responsibility
- Service B: responsibility

## Data Flow
- Step-by-step request flow

## Decisions
- Key trade-offs
- Constraints
```

## 5) Troubleshooting Article Template
```
# Issue Title

## Symptoms
- What users observe

## Cause
- Root cause summary

## Fix
- Step-by-step remediation

## Prevention
- How to avoid in the future

## References
- Related docs or tickets
```

## 6) Code Comment Checklist
- Explain intent/why, not what the code obviously does
- Document edge cases and invariants
- Keep comments close to the code they describe
- Remove stale comments when code changes
