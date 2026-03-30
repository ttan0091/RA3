# Prisma Schema Patterns

## Model Conventions

### Base Model Pattern

```prisma
model User {
  // Primary key - prefer cuid/uuid over autoincrement
  id        String   @id @default(cuid())

  // Unique fields
  email     String   @unique
  username  String   @unique

  // Optional fields
  name      String?
  bio       String?
  avatar    String?

  // Enums
  role      Role     @default(USER)
  status    Status   @default(ACTIVE)

  // Relations
  posts     Post[]
  profile   Profile?
  comments  Comment[]

  // Timestamps
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  deletedAt DateTime? // Soft delete

  // Indexes
  @@index([email])
  @@index([createdAt(sort: Desc)])
  @@map("users") // Table name
}

enum Role {
  USER
  ADMIN
  MODERATOR
}

enum Status {
  ACTIVE
  INACTIVE
  SUSPENDED
}
```

### Relation Patterns

```prisma
// One-to-One
model User {
  id      String   @id @default(cuid())
  profile Profile?
}

model Profile {
  id     String @id @default(cuid())
  user   User   @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId String @unique
}

// One-to-Many
model User {
  id    String @id @default(cuid())
  posts Post[]
}

model Post {
  id       String @id @default(cuid())
  author   User   @relation(fields: [authorId], references: [id])
  authorId String

  @@index([authorId])
}

// Many-to-Many (implicit)
model Post {
  id   String @id @default(cuid())
  tags Tag[]
}

model Tag {
  id    String @id @default(cuid())
  name  String @unique
  posts Post[]
}

// Many-to-Many (explicit - with extra fields)
model Post {
  id       String     @id @default(cuid())
  postTags PostTag[]
}

model Tag {
  id       String     @id @default(cuid())
  postTags PostTag[]
}

model PostTag {
  post      Post     @relation(fields: [postId], references: [id])
  postId    String
  tag       Tag      @relation(fields: [tagId], references: [id])
  tagId     String
  addedAt   DateTime @default(now())
  addedBy   String?

  @@id([postId, tagId])
}
```

### Self-Relations

```prisma
// Tree structure (comments with replies)
model Comment {
  id        String    @id @default(cuid())
  content   String
  parent    Comment?  @relation("CommentReplies", fields: [parentId], references: [id])
  parentId  String?
  replies   Comment[] @relation("CommentReplies")
}

// Followers/Following
model User {
  id        String @id @default(cuid())
  followers User[] @relation("UserFollows")
  following User[] @relation("UserFollows")
}
```

## Field Types

### Scalars

```prisma
model Example {
  // Strings
  name        String
  description String   @db.Text          // Long text
  code        String   @db.VarChar(10)   // Fixed length

  // Numbers
  count       Int
  amount      Float
  price       Decimal  @db.Decimal(10, 2)
  bigNumber   BigInt

  // Boolean
  isActive    Boolean  @default(true)

  // Dates
  createdAt   DateTime @default(now())
  publishedAt DateTime?

  // JSON
  metadata    Json     @default("{}")
  settings    Json?

  // Binary
  data        Bytes
}
```

### Composite Types (MongoDB)

```prisma
type Address {
  street  String
  city    String
  state   String
  zip     String
  country String @default("US")
}

model User {
  id      String  @id @default(cuid())
  address Address?
}
```

## Indexes

```prisma
model Post {
  id        String   @id
  title     String
  content   String
  authorId  String
  published Boolean
  createdAt DateTime

  // Single column
  @@index([authorId])

  // Compound index
  @@index([authorId, published])

  // Sorted index
  @@index([createdAt(sort: Desc)])

  // Full-text search (PostgreSQL)
  @@index([title, content], type: Gin)

  // Unique constraint
  @@unique([authorId, title])
}
```

## Database-Specific Features

### PostgreSQL

```prisma
model Post {
  id      String   @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  tags    String[] // Array type
  content String   @db.Text
  vector  Unsupported("tsvector")? // Full-text search

  @@index([tags], type: Gin)
}
```

### MySQL

```prisma
model Post {
  id      Int      @id @default(autoincrement())
  content String   @db.LongText

  @@index([content(length: 100)]) // Prefix index
}
```

## Soft Delete Pattern

```prisma
model Post {
  id        String    @id @default(cuid())
  title     String
  deletedAt DateTime?

  @@index([deletedAt])
}
```

```typescript
// Middleware for soft delete
prisma.$use(async (params, next) => {
  if (params.model === 'Post') {
    if (params.action === 'delete') {
      params.action = 'update';
      params.args.data = { deletedAt: new Date() };
    }
    if (params.action === 'findMany') {
      params.args.where = { ...params.args.where, deletedAt: null };
    }
  }
  return next(params);
});
```
