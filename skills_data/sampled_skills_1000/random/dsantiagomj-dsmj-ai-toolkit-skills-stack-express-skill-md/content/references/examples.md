# Express.js - Detailed Code Examples

## Example 1: Complete Controller Pattern

```typescript
// src/controllers/product.controller.ts
import { Request, Response } from 'express';
import { ProductService } from '../services/product.service';
import { NotFoundError } from '../errors/app-error';

export class ProductController {
  constructor(private productService = new ProductService()) {}

  findAll = async (req: Request, res: Response) => {
    const { page = 1, limit = 20, category } = req.query;

    const result = await this.productService.findAll({
      page: Number(page),
      limit: Math.min(Number(limit), 100),
      category: category as string,
    });

    res.json({
      data: result.items,
      meta: {
        page: result.page,
        limit: result.limit,
        total: result.total,
        pages: Math.ceil(result.total / result.limit),
      },
    });
  };

  findById = async (req: Request, res: Response) => {
    const product = await this.productService.findById(req.params.id);

    if (!product) {
      throw new NotFoundError('Product not found');
    }

    res.json({ data: product });
  };

  create = async (req: Request, res: Response) => {
    const product = await this.productService.create(req.body);
    res.status(201).json({ data: product });
  };

  update = async (req: Request, res: Response) => {
    const product = await this.productService.update(req.params.id, req.body);

    if (!product) {
      throw new NotFoundError('Product not found');
    }

    res.json({ data: product });
  };

  delete = async (req: Request, res: Response) => {
    await this.productService.delete(req.params.id);
    res.status(204).send();
  };
}
```

## Example 2: Authentication Middleware

```typescript
// src/middleware/auth.ts
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { UnauthorizedError } from '../errors/app-error';

interface JwtPayload {
  userId: string;
  email: string;
}

declare global {
  namespace Express {
    interface Request {
      user?: JwtPayload;
    }
  }
}

export function requireAuth(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;

  if (!authHeader?.startsWith('Bearer ')) {
    throw new UnauthorizedError('Missing or invalid authorization header');
  }

  const token = authHeader.split(' ')[1];

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET!) as JwtPayload;
    req.user = payload;
    next();
  } catch {
    throw new UnauthorizedError('Invalid or expired token');
  }
}

export function requireRole(...roles: string[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      throw new UnauthorizedError();
    }

    // Check role
    // if (!roles.includes(req.user.role)) {
    //   throw new ForbiddenError('Insufficient permissions');
    // }

    next();
  };
}
```

## Example 3: Graceful Shutdown

```typescript
// src/server.ts
import express from 'express';
import { createServer } from 'http';

const app = express();
const server = createServer(app);

function gracefulShutdown(signal: string) {
  console.log(`${signal} received, shutting down gracefully...`);

  server.close(() => {
    console.log('HTTP server closed');

    prisma.$disconnect().then(() => {
      console.log('Database connection closed');
      process.exit(0);
    });
  });

  setTimeout(() => {
    console.error('Forced shutdown after timeout');
    process.exit(1);
  }, 30000);
}

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

server.listen(process.env.PORT || 3000, () => {
  console.log(`Server running on port ${process.env.PORT || 3000}`);
});
```

## Example 4: Service Layer Pattern

```typescript
// src/services/product.service.ts
import { prisma } from '../lib/prisma';

interface FindAllParams {
  page: number;
  limit: number;
  category?: string;
}

export class ProductService {
  async findAll({ page, limit, category }: FindAllParams) {
    const where = category ? { category } : {};

    const [items, total] = await Promise.all([
      prisma.product.findMany({
        where,
        skip: (page - 1) * limit,
        take: limit,
        orderBy: { createdAt: 'desc' },
      }),
      prisma.product.count({ where }),
    ]);

    return { items, total, page, limit };
  }

  async findById(id: string) {
    return prisma.product.findUnique({ where: { id } });
  }

  async create(data: CreateProductInput) {
    return prisma.product.create({ data });
  }

  async update(id: string, data: UpdateProductInput) {
    return prisma.product.update({ where: { id }, data });
  }

  async delete(id: string) {
    return prisma.product.delete({ where: { id } });
  }
}
```
