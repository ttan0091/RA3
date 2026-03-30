# Prisma Query Patterns Reference

Common query patterns for efficient database operations.

## Basic CRUD

### Create

```typescript
// Single create
const user = await prisma.user.create({
  data: {
    email: 'user@example.com',
    name: 'John Doe',
    profile: {
      create: { bio: 'Developer' }, // Nested create
    },
  },
  include: { profile: true },
});

// Create many
const { count } = await prisma.user.createMany({
  data: [
    { email: 'user1@example.com', name: 'User 1' },
    { email: 'user2@example.com', name: 'User 2' },
  ],
  skipDuplicates: true,
});

// Create with connect (existing relation)
const post = await prisma.post.create({
  data: {
    title: 'My Post',
    author: { connect: { id: userId } },
    tags: { connect: [{ id: tag1Id }, { id: tag2Id }] },
  },
});
```

### Read

```typescript
// Find unique
const user = await prisma.user.findUnique({
  where: { email: 'user@example.com' },
});

// Find first (with ordering)
const latestPost = await prisma.post.findFirst({
  where: { published: true },
  orderBy: { publishedAt: 'desc' },
});

// Find many with pagination
const posts = await prisma.post.findMany({
  where: { published: true },
  orderBy: { createdAt: 'desc' },
  skip: 0,
  take: 10,
  include: {
    author: { select: { name: true, image: true } },
    _count: { select: { comments: true } },
  },
});

// Count
const postCount = await prisma.post.count({
  where: { authorId: userId },
});
```

### Update

```typescript
// Update single
const user = await prisma.user.update({
  where: { id: userId },
  data: { name: 'New Name' },
});

// Update many
const { count } = await prisma.post.updateMany({
  where: { authorId: userId, published: false },
  data: { published: true, publishedAt: new Date() },
});

// Upsert
const user = await prisma.user.upsert({
  where: { email: 'user@example.com' },
  update: { name: 'Updated Name' },
  create: { email: 'user@example.com', name: 'New User' },
});

// Atomic operations
await prisma.post.update({
  where: { id: postId },
  data: { viewCount: { increment: 1 } },
});
```

### Delete

```typescript
// Delete single
await prisma.user.delete({
  where: { id: userId },
});

// Delete many
const { count } = await prisma.session.deleteMany({
  where: { expires: { lt: new Date() } },
});
```

## Advanced Filtering

```typescript
// Complex where conditions
const posts = await prisma.post.findMany({
  where: {
    AND: [
      { published: true },
      {
        OR: [
          { title: { contains: 'prisma', mode: 'insensitive' } },
          { content: { contains: 'prisma', mode: 'insensitive' } },
        ],
      },
    ],
    author: {
      role: { in: ['ADMIN', 'MODERATOR'] },
    },
    tags: {
      some: { name: 'typescript' },
    },
    createdAt: {
      gte: new Date('2024-01-01'),
    },
  },
});

// Full-text search (PostgreSQL)
const results = await prisma.post.findMany({
  where: {
    content: { search: 'prisma & typescript' },
  },
});

// JSON filtering
const users = await prisma.user.findMany({
  where: {
    settings: {
      path: ['notifications', 'email'],
      equals: true,
    },
  },
});
```

## Relation Queries

```typescript
// Include nested relations
const post = await prisma.post.findUnique({
  where: { id: postId },
  include: {
    author: true,
    comments: {
      include: { author: true },
      orderBy: { createdAt: 'desc' },
      take: 5,
    },
    tags: true,
  },
});

// Select specific fields
const users = await prisma.user.findMany({
  select: {
    id: true,
    name: true,
    _count: {
      select: { posts: true, comments: true },
    },
  },
});

// Relation filters
const usersWithPosts = await prisma.user.findMany({
  where: {
    posts: {
      some: { published: true },
    },
  },
});

const usersWithoutPosts = await prisma.user.findMany({
  where: {
    posts: {
      none: {},
    },
  },
});
```

## Transactions

```typescript
// Sequential transaction
const [user, post] = await prisma.$transaction([
  prisma.user.create({ data: { email: 'new@example.com' } }),
  prisma.post.create({ data: { title: 'Draft', authorId: 'xxx' } }),
]);

// Interactive transaction
const result = await prisma.$transaction(
  async (tx) => {
    const user = await tx.user.findUnique({ where: { id: userId } });
    if (!user) throw new Error('User not found');

    const balance = await tx.account.update({
      where: { userId: user.id },
      data: { balance: { decrement: amount } },
    });

    if (balance.balance < 0) {
      throw new Error('Insufficient balance');
    }

    return balance;
  },
  {
    maxWait: 5000, // 5s max wait to start
    timeout: 10000, // 10s timeout
    isolationLevel: 'Serializable',
  }
);
```

## Aggregations

```typescript
// Group by
const postsByAuthor = await prisma.post.groupBy({
  by: ['authorId'],
  _count: { id: true },
  _avg: { viewCount: true },
  having: {
    id: { _count: { gt: 5 } },
  },
  orderBy: {
    _count: { id: 'desc' },
  },
});

// Aggregate
const stats = await prisma.post.aggregate({
  _count: true,
  _avg: { viewCount: true },
  _sum: { viewCount: true },
  _min: { createdAt: true },
  _max: { createdAt: true },
  where: { published: true },
});
```

## Raw Queries

```typescript
// Raw query
const users = await prisma.$queryRaw<User[]>`
  SELECT * FROM users
  WHERE email LIKE ${`%${domain}`}
  ORDER BY created_at DESC
`;

// Raw execute
await prisma.$executeRaw`
  UPDATE posts
  SET view_count = view_count + 1
  WHERE id = ${postId}
`;

// TypedSQL (Prisma 5.19+)
// Create SQL file: prisma/sql/getUserPosts.sql
// import { getUserPosts } from '@prisma/client/sql';
// const posts = await prisma.$queryRawTyped(getUserPosts(userId));
```
