# Prisma Migrations Reference

Database migration workflow and best practices.

## Migration Commands

```bash
# Create migration from schema changes
npx prisma migrate dev --name add_user_profile

# Apply migrations in production
npx prisma migrate deploy

# Reset database (dev only - deletes all data)
npx prisma migrate reset

# Check migration status
npx prisma migrate status

# Resolve failed migration (mark as applied/rolled-back)
npx prisma migrate resolve --applied "migration_name"
npx prisma migrate resolve --rolled-back "migration_name"

# Generate Prisma Client
npx prisma generate

# Format schema
npx prisma format

# Validate schema
npx prisma validate

# Open Prisma Studio
npx prisma studio
```

## Migration File Structure

```text
prisma/
├── migrations/
│   ├── 20240101120000_init/
│   │   └── migration.sql
│   ├── 20240115090000_add_user_profile/
│   │   └── migration.sql
│   └── migration_lock.toml
└── schema.prisma
```

## Custom Migration SQL

When Prisma can't auto-generate the migration:

```sql
-- prisma/migrations/20240115090000_custom_migration/migration.sql

-- Add column with default (data migration)
ALTER TABLE "posts" ADD COLUMN "slug" TEXT;
UPDATE "posts" SET "slug" = LOWER(REPLACE("title", ' ', '-'));
ALTER TABLE "posts" ALTER COLUMN "slug" SET NOT NULL;

-- Create unique index
CREATE UNIQUE INDEX "posts_slug_key" ON "posts"("slug");

-- Add check constraint
ALTER TABLE "posts" ADD CONSTRAINT "posts_view_count_positive"
  CHECK ("view_count" >= 0);

-- Create function and trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON posts
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();
```

## Schema Changes Reference

### Adding Fields

```prisma
// Safe: Add nullable field
model User {
  bio String?  // ✅ Safe
}

// Safe: Add field with default
model User {
  status String @default("active")  // ✅ Safe
}

// Breaking: Add required field without default
model User {
  status String  // ❌ Requires data migration
}
```

### Renaming

```prisma
// Use @map to rename in DB only
model User {
  firstName String @map("first_name")  // ✅ No data migration
}

// Or rename column with custom migration
// 1. Create empty migration: prisma migrate dev --create-only
// 2. Add: ALTER TABLE "users" RENAME COLUMN "name" TO "full_name"
// 3. Update schema and apply
```

### Relations

```prisma
// One-to-One
model User {
  profile Profile?
}
model Profile {
  userId String @unique
  user   User   @relation(fields: [userId], references: [id])
}

// One-to-Many
model User {
  posts Post[]
}
model Post {
  authorId String
  author   User   @relation(fields: [authorId], references: [id])
}

// Many-to-Many (implicit)
model Post {
  tags Tag[]
}
model Tag {
  posts Post[]
}

// Many-to-Many (explicit)
model Post {
  tags PostTag[]
}
model Tag {
  posts PostTag[]
}
model PostTag {
  postId String
  tagId  String
  post   Post @relation(fields: [postId], references: [id])
  tag    Tag  @relation(fields: [tagId], references: [id])

  @@id([postId, tagId])
}
```

## Production Deployment

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
jobs:
  deploy:
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Generate Prisma Client
        run: npx prisma generate

      - name: Run migrations
        run: npx prisma migrate deploy
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}

      - name: Deploy application
        run: npm run deploy
```

### Baseline Existing Database

```bash
# For existing databases not managed by Prisma
npx prisma db pull                    # Introspect existing schema
npx prisma migrate dev --name init    # Create initial migration
# Mark as applied without running
npx prisma migrate resolve --applied init
```

### Rollback Strategy

```bash
# 1. Create rollback migration manually
npx prisma migrate dev --create-only --name rollback_feature_x

# 2. Write reverse SQL in migration file

# 3. Apply rollback
npx prisma migrate deploy

# Alternative: Restore from backup
pg_restore -d mydb backup.dump
```

## Seeding

```typescript
// prisma/seed.ts
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  // Clear existing data (optional)
  await prisma.post.deleteMany();
  await prisma.user.deleteMany();

  // Create users
  const user = await prisma.user.create({
    data: {
      email: 'admin@example.com',
      name: 'Admin',
      role: 'ADMIN',
      posts: {
        create: [
          { title: 'First Post', slug: 'first-post', published: true },
          { title: 'Second Post', slug: 'second-post' },
        ],
      },
    },
  });

  console.log('Seeded:', user);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
```

```json
// package.json
{
  "prisma": {
    "seed": "ts-node --compiler-options {\"module\":\"CommonJS\"} prisma/seed.ts"
  }
}
```

```bash
# Run seed
npx prisma db seed

# Auto-seed on reset
npx prisma migrate reset  # Runs seed automatically
```
