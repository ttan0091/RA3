// @ts-nocheck
// Prisma Client Singleton Template
// Location: lib/prisma.ts
// Prevents connection exhaustion in development with hot reload

import { PrismaClient } from '@prisma/client';

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
  });

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma;
}

export default prisma;

// Extended Client with Logging (alternative)
//
// import { PrismaClient, Prisma } from '@prisma/client';
//
// const prisma = new PrismaClient({
//   log: [
//     { level: 'query', emit: 'event' },
//     { level: 'error', emit: 'stdout' },
//   ],
// });
//
// // Log slow queries
// prisma.$on('query', (e: Prisma.QueryEvent) => {
//   if (e.duration > 100) {
//     console.warn(`Slow query (${e.duration}ms):`, e.query);
//   }
// });
//
// export default prisma;

// Usage:
//
// import prisma from '@/lib/prisma';
//
// // In Server Components
// const users = await prisma.user.findMany();
//
// // In Server Actions
// export async function createUser(data: UserData) {
//   return prisma.user.create({ data });
// }
//
// // With transactions
// await prisma.$transaction([
//   prisma.user.create({ data: userData }),
//   prisma.profile.create({ data: profileData }),
// ]);
