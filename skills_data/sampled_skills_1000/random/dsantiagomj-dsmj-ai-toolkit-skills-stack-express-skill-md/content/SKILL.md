---
name: express
description: >
  Express.js patterns for routing, middleware, error handling, and RESTful API development.
  Trigger: When building Express servers, when implementing REST APIs, when setting up middleware,
  when handling authentication in Express, when structuring Node.js backends.
tags: [express, nodejs, rest, api, middleware, routing, backend, server]
author: dsmj-ai-toolkit
metadata:
  version: "1.0"
  last_updated: "2026-01-19"
  category: stack
  auto_invoke: "When working with Express.js applications"
  stack_category: backend
  progressive_disclosure: true
references:
  - name: Middleware Patterns
    url: ./references/middleware.md
    type: local
  - name: Error Handling
    url: ./references/error-handling.md
    type: local
---

# Express.js - Backend API Patterns

**Production patterns for Express.js REST APIs, middleware, and error handling**

---

## When to Use This Skill

**Use this skill when**:
- Building Express.js backend applications
- Implementing RESTful APIs
- Setting up middleware chains
- Handling authentication and authorization
- Structuring Node.js server applications
- Implementing error handling and validation

**Don't use this skill when**:
- Using other frameworks (Fastify, Koa, Hono)
- Building frontend applications
- Working with Next.js API routes (use `nextjs` skill)

---

## Critical Patterns

### Pattern 1: Router Organization

**When**: Structuring API routes in larger applications

```typescript
// ✅ GOOD: Organized router structure
// src/routes/products.ts
import { Router } from 'express';
import { ProductController } from '../controllers/product.controller';
import { validateBody } from '../middleware/validate';
import { productSchema } from '../schemas/product.schema';
import { requireAuth } from '../middleware/auth';

const router = Router();
const controller = new ProductController();

router.get('/', controller.findAll);
router.get('/:id', controller.findById);
router.post('/', requireAuth, validateBody(productSchema), controller.create);
router.put('/:id', requireAuth, validateBody(productSchema), controller.update);
router.delete('/:id', requireAuth, controller.delete);

export default router;

// src/routes/index.ts
import { Router } from 'express';
import productsRouter from './products';
import usersRouter from './users';
import authRouter from './auth';

const router = Router();

router.use('/products', productsRouter);
router.use('/users', usersRouter);
router.use('/auth', authRouter);

export default router;

// src/app.ts
import express from 'express';
import routes from './routes';

const app = express();
app.use('/api/v1', routes);

// ❌ BAD: All routes in one file
app.get('/api/products', ...);
app.post('/api/products', ...);
app.get('/api/users', ...);
// Becomes unmaintainable at scale
```

### Pattern 2: Middleware Chain

**When**: Processing requests through multiple steps

```typescript
// ✅ GOOD: Well-structured middleware chain
import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import rateLimit from 'express-rate-limit';
import { requestLogger } from './middleware/logger';
import { errorHandler } from './middleware/error';

const app = express();

// Security middleware (order matters!)
app.use(helmet()); // Security headers
app.use(cors({ origin: process.env.ALLOWED_ORIGINS?.split(',') }));
app.use(rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per window
}));

// Parsing middleware
app.use(express.json({ limit: '10kb' })); // Body size limit
app.use(express.urlencoded({ extended: true }));

// Logging
app.use(requestLogger);

// Routes
app.use('/api', routes);

// Error handling (must be last!)
app.use(errorHandler);

// ❌ BAD: Error handler before routes
app.use(errorHandler); // Won't catch route errors!
app.use('/api', routes);
```

### Pattern 3: Async Error Handling

**When**: Handling errors in async route handlers

```typescript
// ✅ GOOD: Async wrapper to catch errors
type AsyncHandler = (
  req: Request,
  res: Response,
  next: NextFunction
) => Promise<void>;

const asyncHandler = (fn: AsyncHandler) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

// Usage
router.get('/products/:id', asyncHandler(async (req, res) => {
  const product = await productService.findById(req.params.id);

  if (!product) {
    throw new NotFoundError('Product not found');
  }

  res.json(product);
}));

// ❌ BAD: Unhandled promise rejection
router.get('/products/:id', async (req, res) => {
  const product = await productService.findById(req.params.id); // If this throws, crash!
  res.json(product);
});

// ❌ BAD: Try-catch in every handler
router.get('/products/:id', async (req, res, next) => {
  try {
    const product = await productService.findById(req.params.id);
    res.json(product);
  } catch (error) {
    next(error);
  }
});
```

### Pattern 4: Custom Error Classes

**When**: Creating structured error responses

```typescript
// ✅ GOOD: Custom error classes
// src/errors/app-error.ts
export class AppError extends Error {
  constructor(
    public message: string,
    public statusCode: number,
    public code: string
  ) {
    super(message);
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }
}

export class NotFoundError extends AppError {
  constructor(message = 'Resource not found') {
    super(message, 404, 'NOT_FOUND');
  }
}

export class ValidationError extends AppError {
  constructor(message: string, public details?: Record<string, string[]>) {
    super(message, 400, 'VALIDATION_ERROR');
  }
}

export class UnauthorizedError extends AppError {
  constructor(message = 'Unauthorized') {
    super(message, 401, 'UNAUTHORIZED');
  }
}

// Error handler middleware
export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: {
        code: err.code,
        message: err.message,
        ...(err instanceof ValidationError && { details: err.details }),
      },
    });
  }

  // Unknown error - log and return generic message
  console.error('Unexpected error:', err);
  res.status(500).json({
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred',
    },
  });
}

// ❌ BAD: String errors or status codes everywhere
throw new Error('Not found'); // No status code!
res.status(404).json({ error: 'Not found' }); // Inconsistent format
```

### Pattern 5: Request Validation

**When**: Validating incoming request data

```typescript
// ✅ GOOD: Validation middleware with Zod
import { z } from 'zod';
import { Request, Response, NextFunction } from 'express';
import { ValidationError } from '../errors/app-error';

export function validateBody<T extends z.ZodSchema>(schema: T) {
  return (req: Request, res: Response, next: NextFunction) => {
    const result = schema.safeParse(req.body);

    if (!result.success) {
      const details = result.error.flatten().fieldErrors;
      throw new ValidationError('Validation failed', details);
    }

    req.body = result.data; // Replace with validated data
    next();
  };
}

export function validateQuery<T extends z.ZodSchema>(schema: T) {
  return (req: Request, res: Response, next: NextFunction) => {
    const result = schema.safeParse(req.query);

    if (!result.success) {
      throw new ValidationError('Invalid query parameters');
    }

    req.query = result.data as any;
    next();
  };
}

// Schema definition
const createProductSchema = z.object({
  name: z.string().min(1).max(100),
  price: z.number().positive(),
  category: z.enum(['electronics', 'clothing', 'food']),
});

// Usage
router.post('/products',
  requireAuth,
  validateBody(createProductSchema),
  asyncHandler(async (req, res) => {
    // req.body is typed and validated!
    const product = await productService.create(req.body);
    res.status(201).json(product);
  })
);

// ❌ BAD: Manual validation in handler
router.post('/products', async (req, res) => {
  if (!req.body.name) {
    return res.status(400).json({ error: 'Name required' });
  }
  if (typeof req.body.price !== 'number') {
    return res.status(400).json({ error: 'Price must be number' });
  }
  // ... more validation scattered in handler
});
```

---

## Code Examples

For complete, production-ready examples, see [references/examples.md](./references/examples.md):
- Controller pattern with pagination
- Authentication middleware with JWT
- Graceful shutdown handling
- Service layer pattern

---

## Anti-Patterns

### Don't: Business Logic in Controllers

```typescript
// ❌ BAD: All logic in controller
router.post('/orders', async (req, res) => {
  const items = await db.cartItem.findMany({ where: { userId: req.user.id } });
  const total = items.reduce((sum, i) => sum + i.price * i.quantity, 0);
  const order = await db.order.create({ data: { items, total } });
  await sendEmail(req.user.email, 'Order confirmed');
  res.json(order);
});

// ✅ GOOD: Controller calls service
router.post('/orders', asyncHandler(async (req, res) => {
  const order = await orderService.createFromCart(req.user.id);
  res.status(201).json({ data: order });
}));
```

### Don't: Expose Stack Traces

```typescript
// ❌ BAD: Sending error stack to client
app.use((err, req, res, next) => {
  res.status(500).json({ error: err.message, stack: err.stack });
});

// ✅ GOOD: Log internally, send safe message
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});
```

### Don't: Skip Input Validation

```typescript
// ❌ BAD: Trust user input
router.post('/users', async (req, res) => {
  const user = await db.user.create({ data: req.body }); // Dangerous!
});

// ✅ GOOD: Validate and sanitize
router.post('/users', validateBody(userSchema), async (req, res) => {
  const user = await db.user.create({ data: req.body });
});
```

---

## Quick Reference

| Task | Pattern | Example |
|------|---------|---------|
| Organize routes | Router modules | `router.use('/products', productsRouter)` |
| Catch async errors | asyncHandler | `asyncHandler(async (req, res) => {})` |
| Validate input | Zod middleware | `validateBody(schema)` |
| Custom errors | Error classes | `throw new NotFoundError()` |
| Auth middleware | requireAuth | `router.use(requireAuth)` |
| Parse JSON | Built-in | `app.use(express.json())` |
| Security headers | Helmet | `app.use(helmet())` |

---

## Resources

**Official Documentation**:
- [Express.js](https://expressjs.com/)
- [Express Error Handling](https://expressjs.com/en/guide/error-handling.html)

**Related Skills**:
- **nodejs**: Node.js patterns
- **security**: API security best practices
- **api-design**: RESTful API design

---

## Keywords

`express`, `expressjs`, `nodejs`, `rest`, `api`, `middleware`, `routing`, `backend`, `server`, `error-handling`, `validation`
