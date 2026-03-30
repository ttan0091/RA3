# コードパターン集

## 1. Zodスキーマ定義

```typescript
// entities/<name>/model/schema.ts
import { z } from "zod";

// ステータスenum
export const statusSchema = z.enum(["active", "inactive", "archived"]);
export type Status = z.infer<typeof statusSchema>;

// 集約スキーマ（イベントリプレイ後の状態）
export const aggregateSchema = z.object({
  id: z.string().uuid(),
  // ドメイン固有フィールド
  name: z.string().min(1).max(100),
  status: statusSchema,
  // メタデータ
  version: z.number().int().nonnegative(),
  isDeleted: z.boolean(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});
export type Aggregate = z.infer<typeof aggregateSchema>;

// 投影スキーマ（クエリ用、isDeleted除外）
export const projectionSchema = aggregateSchema.omit({ isDeleted: true });
export type Projection = z.infer<typeof projectionSchema>;
```

## 2. イベント型定義

```typescript
// entities/<name>/model/events.ts
import type { DomainEvent } from "@/shared/lib/event-store/types";

export const AGGREGATE_TYPE = "EntityName";

// イベント型
export type CreatedEvent = DomainEvent<
  "EntityNameCreated",
  { name: string; /* 初期データ */ }
>;

export type UpdatedEvent = DomainEvent<
  "EntityNameUpdated",
  { name?: string; /* 更新可能フィールド */ }
>;

export type DeletedEvent = DomainEvent<"EntityNameDeleted", object>;

// Union型
export type EntityEvent = CreatedEvent | UpdatedEvent | DeletedEvent;

// ファクトリ関数
interface EventMeta {
  id: string;
  aggregateId: string;
  version: number;
  timestamp: string;
  correlationId: string;
}

export function createCreatedEvent(
  meta: EventMeta,
  data: CreatedEvent["data"]
): CreatedEvent {
  return {
    id: meta.id,
    type: "EntityNameCreated",
    aggregateId: meta.aggregateId,
    aggregateType: AGGREGATE_TYPE,
    version: meta.version,
    timestamp: meta.timestamp,
    data,
    metadata: { correlationId: meta.correlationId },
  };
}
```

## 3. decide（決定ロジック）

```typescript
// features/<name>/model/decide.ts
import type { Result } from "@/shared/lib/result";
import { ok, err } from "@/shared/lib/result";
import type { Aggregate } from "@/entities/<name>/model/schema";
import type { EntityEvent } from "@/entities/<name>/model/events";
import { createCreatedEvent, createUpdatedEvent } from "@/entities/<name>/model/events";

// コマンド型
export type Command =
  | { type: "Create"; name: string }
  | { type: "Update"; aggregateId: string; name?: string; expectedVersion: number }
  | { type: "Delete"; aggregateId: string; expectedVersion: number };

// エラー型
export type DecisionError =
  | { code: "ALREADY_EXISTS"; message: string }
  | { code: "NOT_FOUND"; message: string }
  | { code: "VERSION_MISMATCH"; message: string }
  | { code: "ALREADY_DELETED"; message: string };

// Meta型
interface Meta {
  id: string;
  now: string;
  correlationId: string;
}

// 決定関数（純粋関数）
export function decide(
  state: Aggregate | null,
  command: Command,
  meta: Meta
): Result<EntityEvent[], DecisionError> {
  switch (command.type) {
    case "Create": {
      if (state) {
        return err({ code: "ALREADY_EXISTS", message: "Entity already exists" });
      }
      return ok([
        createCreatedEvent(
          { ...meta, aggregateId: meta.id, version: 1, timestamp: meta.now },
          { name: command.name }
        ),
      ]);
    }

    case "Update": {
      if (!state) {
        return err({ code: "NOT_FOUND", message: "Entity not found" });
      }
      if (state.isDeleted) {
        return err({ code: "ALREADY_DELETED", message: "Entity is deleted" });
      }
      if (state.version !== command.expectedVersion) {
        return err({ code: "VERSION_MISMATCH", message: "Version mismatch" });
      }
      return ok([
        createUpdatedEvent(
          { ...meta, aggregateId: command.aggregateId, version: state.version + 1, timestamp: meta.now },
          { name: command.name }
        ),
      ]);
    }

    case "Delete": {
      if (!state) {
        return err({ code: "NOT_FOUND", message: "Entity not found" });
      }
      if (state.isDeleted) {
        return err({ code: "ALREADY_DELETED", message: "Entity is deleted" });
      }
      if (state.version !== command.expectedVersion) {
        return err({ code: "VERSION_MISMATCH", message: "Version mismatch" });
      }
      return ok([
        createDeletedEvent(
          { ...meta, aggregateId: command.aggregateId, version: state.version + 1, timestamp: meta.now }
        ),
      ]);
    }
  }
}

// in-source testing
if (import.meta.vitest) {
  const { describe, it, expect } = import.meta.vitest;

  describe("decide", () => {
    const meta = { id: "event-1", now: "2025-01-01T00:00:00Z", correlationId: "req-1" };

    it("Createは状態がnullの場合にイベントを生成", () => {
      const result = decide(null, { type: "Create", name: "Test" }, meta);
      expect(result.isOk()).toBe(true);
      if (result.isOk()) {
        expect(result.value[0].type).toBe("EntityNameCreated");
      }
    });

    it("Createは既存エンティティがある場合にエラー", () => {
      const state = { id: "1", name: "Existing", version: 1, isDeleted: false } as Aggregate;
      const result = decide(state, { type: "Create", name: "Test" }, meta);
      expect(result.isErr()).toBe(true);
    });
  });
}
```

## 4. apply（適用ロジック）

```typescript
// features/<name>/model/apply.ts
import type { Aggregate } from "@/entities/<name>/model/schema";
import type { EntityEvent } from "@/entities/<name>/model/events";

// 適用関数（純粋関数）
export function apply(
  state: Aggregate | null,
  event: EntityEvent
): Aggregate {
  switch (event.type) {
    case "EntityNameCreated":
      return {
        id: event.aggregateId,
        name: event.data.name,
        status: "active",
        version: event.version,
        isDeleted: false,
        createdAt: event.timestamp,
        updatedAt: event.timestamp,
      };

    case "EntityNameUpdated":
      if (!state) throw new Error("Cannot update non-existent entity");
      return {
        ...state,
        name: event.data.name ?? state.name,
        version: event.version,
        updatedAt: event.timestamp,
      };

    case "EntityNameDeleted":
      if (!state) throw new Error("Cannot delete non-existent entity");
      return {
        ...state,
        isDeleted: true,
        version: event.version,
        updatedAt: event.timestamp,
      };

    default:
      return state!;
  }
}

// in-source testing
if (import.meta.vitest) {
  const { describe, it, expect } = import.meta.vitest;

  describe("apply", () => {
    it("CreatedイベントでAggregateを生成", () => {
      const event = {
        id: "e1",
        type: "EntityNameCreated" as const,
        aggregateId: "a1",
        aggregateType: "EntityName",
        version: 1,
        timestamp: "2025-01-01T00:00:00Z",
        data: { name: "Test" },
        metadata: {},
      };
      const result = apply(null, event);
      expect(result.id).toBe("a1");
      expect(result.name).toBe("Test");
      expect(result.version).toBe(1);
    });
  });
}
```

## 5. commands（コマンド実行）

```typescript
// features/<name>/model/commands.ts
import { depend } from "velona";
import type { Result } from "@/shared/lib/result";
import { ok } from "@/shared/lib/result";
import {
  type IEventStore,
  eventStore as defaultEventStore,
} from "@/shared/lib/event-store";
import { AGGREGATE_TYPE, type EntityEvent } from "@/entities/<name>/model/events";
import { decide, type Command, type DecisionError } from "./decide";
import { apply } from "./apply";
import { projector as defaultProjector, type IProjector } from "./projector";

interface CommandDeps {
  eventStore: IEventStore;
  projector: IProjector;
  clock: () => string;
  idGen: () => string;
}

type CommandResult = Result<
  { aggregateId: string; events: EntityEvent[] },
  DecisionError | { code: "CONFLICT"; message: string }
>;

export const executeCommand = depend(
  {
    eventStore: defaultEventStore,
    projector: defaultProjector,
    clock: () => new Date().toISOString(),
    idGen: () => crypto.randomUUID(),
  },
  async (deps: CommandDeps, command: Command, correlationId: string): Promise<CommandResult> => {
    const aggregateId = "aggregateId" in command ? command.aggregateId : deps.idGen();

    // 1. イベントリプレイで現在状態を取得
    const { events, version } = await deps.eventStore.load(AGGREGATE_TYPE, aggregateId);
    const state = events.reduce(apply, null);

    // 2. 決定（純粋関数）
    const meta = { id: deps.idGen(), now: deps.clock(), correlationId };
    const decision = decide(state, command, meta);
    if (decision.isErr()) return decision;

    // 3. 永続化（楽観ロック）
    const appendResult = await deps.eventStore.append(
      AGGREGATE_TYPE,
      aggregateId,
      decision.value,
      version
    );
    if (appendResult.isErr()) return appendResult;

    // 4. Projection更新（失敗はログのみ）
    const next = decision.value.reduce(apply, state);
    if (next) {
      try {
        await deps.projector.save(next);
      } catch (error) {
        console.warn("Projection save failed:", error);
      }
    }

    return ok({ aggregateId, events: decision.value });
  }
);
```

## 6. projector（投影更新）

```typescript
// features/<name>/model/projector.ts
import { depend } from "velona";
import { eq } from "drizzle-orm";
import type { DrizzleDatabase } from "@/shared/lib/db";
import { db as defaultDb } from "@/shared/lib/db";
import { entityTable } from "@/shared/lib/db/schema";
import type { Aggregate, Projection } from "@/entities/<name>/model/schema";

export interface IProjector {
  save(aggregate: Aggregate): Promise<Projection | null>;
  clear(): Promise<void>;
}

interface ProjectorDeps {
  db: DrizzleDatabase;
}

export const saveProjection = depend(
  { db: defaultDb },
  async (deps: ProjectorDeps, aggregate: Aggregate): Promise<Projection | null> => {
    if (aggregate.isDeleted) {
      await deps.db.delete(entityTable).where(eq(entityTable.id, aggregate.id));
      return null;
    }

    const projection: Projection = {
      id: aggregate.id,
      name: aggregate.name,
      status: aggregate.status,
      version: aggregate.version,
      createdAt: aggregate.createdAt,
      updatedAt: aggregate.updatedAt,
    };

    await deps.db
      .insert(entityTable)
      .values(projection)
      .onConflictDoUpdate({
        target: entityTable.id,
        set: {
          name: projection.name,
          status: projection.status,
          version: projection.version,
          updatedAt: projection.updatedAt,
        },
      });

    return projection;
  }
);

export const clearProjections = depend(
  { db: defaultDb },
  async (deps: ProjectorDeps): Promise<void> => {
    await deps.db.delete(entityTable);
  }
);

// IProjectorファサード
export const projector: IProjector = {
  save: (aggregate) => saveProjection(aggregate),
  clear: () => clearProjections(),
};
```

## 7. queries（クエリ）

```typescript
// features/<name>/model/queries.ts
import { depend } from "velona";
import { eq } from "drizzle-orm";
import type { DrizzleDatabase } from "@/shared/lib/db";
import { db as defaultDb } from "@/shared/lib/db";
import { entityTable } from "@/shared/lib/db/schema";
import type { Projection } from "@/entities/<name>/model/schema";

interface QueryDeps {
  db: DrizzleDatabase;
}

export const queryAll = depend(
  { db: defaultDb },
  async (deps: QueryDeps): Promise<Projection[]> => {
    return await deps.db.select().from(entityTable).all();
  }
);

export const queryById = depend(
  { db: defaultDb },
  async (deps: QueryDeps, id: string): Promise<Projection | null> => {
    const result = await deps.db
      .select()
      .from(entityTable)
      .where(eq(entityTable.id, id))
      .get();
    return result ?? null;
  }
);
```

## 8. APIルート

```typescript
// features/<name>/api/routes.ts
import { Hono } from "hono";
import { zValidator } from "@hono/zod-validator";
import { executeCommand } from "../model/commands";
import { queryAll, queryById } from "../model/queries";
import { createSchema, updateSchema } from "./schemas";

export const routes = new Hono()
  .get("/", async (c) => {
    const items = await queryAll();
    return c.json({ data: items });
  })
  .post("/", zValidator("json", createSchema), async (c) => {
    const body = c.req.valid("json");
    const correlationId = crypto.randomUUID();
    const result = await executeCommand({ type: "Create", ...body }, correlationId);

    if (result.isErr()) {
      return c.json({ error: result.error }, 400);
    }
    return c.json({ data: { id: result.value.aggregateId } }, 201);
  })
  .get("/:id", async (c) => {
    const id = c.req.param("id");
    const item = await queryById(id);

    if (!item) {
      return c.json({ error: { code: "NOT_FOUND", message: "Not found" } }, 404);
    }
    return c.json({ data: item });
  })
  .patch("/:id", zValidator("json", updateSchema), async (c) => {
    const id = c.req.param("id");
    const body = c.req.valid("json");
    const correlationId = crypto.randomUUID();
    const result = await executeCommand(
      { type: "Update", aggregateId: id, ...body },
      correlationId
    );

    if (result.isErr()) {
      const status = result.error.code === "NOT_FOUND" ? 404 : 400;
      return c.json({ error: result.error }, status);
    }
    return c.json({ data: { id } });
  })
  .delete("/:id", async (c) => {
    const id = c.req.param("id");
    const correlationId = crypto.randomUUID();
    const result = await executeCommand(
      { type: "Delete", aggregateId: id, expectedVersion: 0 },  // TODO: expectedVersion取得
      correlationId
    );

    if (result.isErr()) {
      const status = result.error.code === "NOT_FOUND" ? 404 : 400;
      return c.json({ error: result.error }, status);
    }
    return c.json({ data: { id } });
  });

export type Routes = typeof routes;
```

## 9. RPC型定義

```typescript
// features/<name>/api/contracts.ts
import { hc } from "hono/client";
import type { Routes } from "./routes";

const _client = hc<Routes>("/");

// 個別RPC関数型をexport
export type GetList = typeof _client.$get;
export type Create = typeof _client.$post;
export type GetById = typeof _client[":id"].$get;
export type Update = typeof _client[":id"].$patch;
export type Delete = typeof _client[":id"].$delete;
```

## 10. TanStack Query hooks

```typescript
// features/<name>/hooks/useList.ts
import { queryOptions, useQuery } from "@tanstack/react-query";
import type { GetList } from "../api/contracts";

export const listQueryOptions = (getList: GetList) =>
  queryOptions({
    queryKey: ["entities", "list"],
    queryFn: async () => {
      const res = await getList();
      if (!res.ok) throw new Error("Failed to fetch list");
      return (await res.json()).data;
    },
  });

export function useList(getList: GetList) {
  return useQuery(listQueryOptions(getList));
}

// features/<name>/hooks/useCreate.ts
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { Create } from "../api/contracts";

export function useCreate(create: Create) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { name: string }) => {
      const res = await create({ json: data });
      if (!res.ok) throw new Error("Failed to create");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["entities"] });
    },
  });
}
```

## 11. テストフィクスチャ

```typescript
// shared/lib/test/builders.ts
import type { Aggregate } from "@/entities/<name>/model/schema";

export function createTestAggregate(
  overrides: Partial<Aggregate> = {}
): Aggregate {
  return {
    id: crypto.randomUUID(),
    name: "Test Entity",
    status: "active",
    version: 0,
    isDeleted: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    ...overrides,
  };
}

export function testMeta(overrides: Partial<{ id: string; now: string; correlationId: string }> = {}) {
  return {
    id: crypto.randomUUID(),
    now: new Date().toISOString(),
    correlationId: crypto.randomUUID(),
    ...overrides,
  };
}
```
