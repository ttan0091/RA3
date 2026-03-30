---
name: development
description: Local development environment setup and commands
---

# Development Skill

This skill provides instructions for setting up and running the local development environment.

## Prerequisites

- Node.js >= 20.0.0
- Docker & Docker Compose
- npm or yarn

## Quick Start

### Option 1: Full Docker Setup (Recommended)

// turbo

1. Start all services via Docker Compose

```bash
cd server && docker-compose up -d
```

This starts:

- PostgreSQL on port 5432
- Redis on port 6379
- NestJS API on port 3000 (with hot reload)

// turbo 2. Start the frontend separately

```bash
cd client && npm run dev
```

### Option 2: Databases in Docker, Apps Local

// turbo

1. Start only databases

```bash
cd server && docker-compose up -d postgres redis
```

// turbo 2. Install dependencies

```bash
cd server && npm install
cd client && npm install
```

// turbo 3. Run migrations and seed

```bash
cd server && npm run migration:run
cd server && npm run seed:run
```

4. Start backend in dev mode

```bash
cd server && npm run start:dev
```

5. Start frontend in dev mode

```bash
cd client && npm run dev
```

## Environment Configuration

### Server (.env)

Copy `.env.example` to `.env`:

```bash
cd server && cp .env.example .env
```

Key variables:
| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 3000 | API server port |
| `DATABASE_HOST` | localhost | PostgreSQL host |
| `DATABASE_PORT` | 5432 | PostgreSQL port |
| `DATABASE_NAME` | ecommerce | Database name |
| `REDIS_HOST` | localhost | Redis host |
| `JWT_SECRET` | (set your own) | JWT signing key |

### Client

The Vite dev server runs on port 5173 by default.
API requests are proxied via `vite.config.js`.

## Development URLs

| Service      | URL                                 |
| ------------ | ----------------------------------- |
| Frontend     | http://localhost:5173               |
| Backend API  | http://localhost:3000/api/v1        |
| Swagger Docs | http://localhost:3000/api/docs      |
| Health Check | http://localhost:3000/api/v1/health |

## Hot Reload

Both client and server support hot reload:

- **Server**: NestJS `--watch` mode (automatic with `npm run start:dev`)
- **Client**: Vite HMR (automatic with `npm run dev`)

## Debugging

### Backend (VSCode)

1. Run `npm run start:debug` instead of `start:dev`
2. Attach VSCode debugger to port 9229

Add to `.vscode/launch.json`:

```json
{
  "type": "node",
  "request": "attach",
  "name": "Attach to NestJS",
  "port": 9229,
  "restart": true
}
```

### Frontend (Browser DevTools)

React DevTools extension provides component inspection.
Vite source maps enable debugging in browser DevTools.

## Common Development Tasks

### Add New Module (Backend)

```bash
cd server && npx nest g module modules/new-module
cd server && npx nest g controller modules/new-module
cd server && npx nest g service modules/new-module
```

### Add New Component (Frontend)

Create in `client/src/components/`:

```jsx
// client/src/components/NewComponent.jsx
export default function NewComponent() {
  return <div>New Component</div>;
}
```

### Lint & Format

// turbo

```bash
cd server && npm run lint
cd server && npm run format
cd client && npm run lint
```

## Stopping Services

// turbo
Stop all Docker containers:

```bash
cd server && docker-compose down
```

Stop and remove volumes (resets database):

```bash
cd server && docker-compose down -v
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 3000
lsof -i :3000
# Kill the process
kill -9 <PID>
```

### Database Connection Failed

1. Ensure Docker containers are running: `docker ps`
2. Check `.env` configuration matches Docker Compose
3. Wait for health checks: `docker-compose logs postgres`

### Node Modules Issues

```bash
# Clean reinstall
rm -rf node_modules package-lock.json
npm install
```
