# アーキテクチャ詳細

## 全体構成

```
src/
├── shared/                    # 共有インフラストラクチャ
│   ├── lib/
│   │   ├── result.ts          # Result<T, E> 型
│   │   ├── errors.ts          # 共通エラー型
│   │   ├── db/                # Drizzle DB設定
│   │   │   ├── index.ts
│   │   │   └── schema.ts      # 全テーブル定義
│   │   ├── event-store/       # イベントストア
│   │   │   ├── types.ts       # DomainEvent, EventMetadata
│   │   │   ├── EventStore.ts  # load/append/getAllEvents
│   │   │   ├── replay.ts      # リプレイユーティリティ
│   │   │   └── upcaster.ts    # スキーマ進化対応
│   │   └── command-log/       # コマンドログ（AI追跡）
│   └── infrastructure/
│       └── startup.ts         # 起動時初期化
│
├── entities/                  # ドメインモデル層
│   └── <entity>/
│       ├── model/
│       │   ├── schema.ts      # Zodスキーマ（型定義）
│       │   ├── events.ts      # イベント型・ファクトリ
│       │   └── index.ts
│       └── ui/                # 表示専用UI（オプション）
│
├── features/                  # ユースケース層
│   └── <feature>/
│       ├── model/
│       │   ├── decide.ts      # 決定ロジック（純粋関数）
│       │   ├── apply.ts       # 適用ロジック（純粋関数）
│       │   ├── commands.ts    # コマンド実行（velona DI）
│       │   ├── queries.ts     # クエリ
│       │   ├── projector.ts   # Projection更新
│       │   └── projection-handler.ts
│       ├── api/
│       │   ├── routes.ts      # Hono APIルート
│       │   ├── contracts.ts   # RPC型定義
│       │   └── schemas.ts     # バリデーションスキーマ
│       ├── hooks/             # TanStack Query（オプション）
│       └── ui/                # UIコンポーネント（オプション）
│
├── widgets/                   # 複合UIブロック
│   └── <widget>/
│       ├── ui/
│       ├── model/
│       └── index.ts
│
├── pages/                     # ルートコンポーネント（TanStack Router）
│
└── app/                       # アプリケーション初期化
```

## Event Sourcing フロー

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Command   │───▶│   decide()  │───▶│   Events    │
│  (Write)    │    │ (純粋関数)   │    │ (発生事実)  │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                             │
                   ┌─────────────────────────┼─────────────────────────┐
                   │                         ▼                         │
                   │  ┌─────────────┐    ┌─────────────┐              │
                   │  │ EventStore  │───▶│   apply()   │              │
                   │  │  (永続化)    │    │ (純粋関数)   │              │
                   │  └─────────────┘    └──────┬──────┘              │
                   │                            │                      │
                   │                            ▼                      │
                   │                   ┌─────────────┐                │
                   │                   │  Projector  │                │
                   │                   │ (投影更新)   │                │
                   │                   └──────┬──────┘                │
                   │                          │                        │
                   │                          ▼                        │
                   │                 ┌─────────────┐                  │
                   │                 │ Projection  │◀── Query (Read)  │
                   │                 │  (SQLite)   │                  │
                   │                 └─────────────┘                  │
                   └───────────────────────────────────────────────────┘
```

## イベントストアテーブル

```sql
CREATE TABLE events (
  sequence INTEGER PRIMARY KEY AUTOINCREMENT,  -- 厳密順序
  id TEXT NOT NULL UNIQUE,
  aggregate_type TEXT NOT NULL,
  aggregate_id TEXT NOT NULL,
  type TEXT NOT NULL,
  version INTEGER NOT NULL,
  timestamp TEXT NOT NULL,
  data TEXT NOT NULL,      -- JSON
  metadata TEXT,           -- JSON (actor, correlationId, etc.)

  UNIQUE(aggregate_type, aggregate_id, version)
);
```

**ポイント**:
- `sequence`: 同時刻でも順序を保証
- `(aggregate_type, aggregate_id, version)`: 楽観的ロック
- 複数集約タイプを1テーブルで管理

## EventMetadata

```typescript
interface EventMetadata {
  actor?: Actor;           // 誰が
  correlationId?: string;  // リクエスト追跡
  causationId?: string;    // 因果関係
  sessionId?: string;      // セッション
  requestId?: string;      // 冪等性キー
  schemaVersion?: number;  // Upcaster用
}

interface Actor {
  type: "user" | "ai" | "system";
  id?: string;
}
```

## CommandLog（AI操作追跡）

```sql
CREATE TABLE command_logs (
  id TEXT PRIMARY KEY,
  correlation_id TEXT NOT NULL,
  causation_id TEXT,

  command_name TEXT NOT NULL,
  command_version INTEGER NOT NULL DEFAULT 1,
  command TEXT NOT NULL,           -- JSON

  aggregate_type TEXT,
  aggregate_id TEXT,

  actor TEXT NOT NULL,             -- JSON
  session_id TEXT,
  request_id TEXT,

  ai_info TEXT,                    -- JSON (modelId, runId, etc.)
  result TEXT,                     -- JSON (status, eventIds, error)

  started_at TEXT NOT NULL,
  completed_at TEXT
);
```

## FSD層の責務

| 層 | 責務 | 含めるもの |
|----|------|-----------|
| shared | 共通インフラ | DB, EventStore, Result, Errors |
| entities | ドメインモデル | Zodスキーマ, イベント型, 表示UI |
| features | ユースケース | decide/apply, commands, queries, API, hooks |
| widgets | 複合UI | 複数entities/featuresを組み合わせたブロック |
| pages | ルート | TanStack Router, ページコンポーネント |
| app | 初期化 | Providers, 起動処理 |

## 依存方向

```
app → pages → widgets → features → entities → shared
```

**上位は下位を参照可能、逆は不可**

## velona DIパターン

```typescript
import { depend } from "velona";

// 依存を持つ関数
export const executeCommand = depend(
  {
    eventStore: defaultEventStore,
    projector: defaultProjector,
    clock: () => new Date().toISOString(),
    idGen: () => crypto.randomUUID(),
  },
  async (deps, command: Command, correlationId: string) => {
    const { events, version } = await deps.eventStore.load(aggregateType, aggregateId);
    const state = events.reduce(apply, null);

    const meta = { id: deps.idGen(), now: deps.clock(), correlationId };
    const decision = decide(state, command, meta);
    if (decision.isErr()) return decision;

    const appendResult = await deps.eventStore.append(
      aggregateType, aggregateId, decision.value, version
    );
    if (appendResult.isErr()) return appendResult;

    const next = decision.value.reduce(apply, state);
    if (next) await deps.projector.save(next);

    return ok({ aggregateId, events: decision.value });
  }
);

// テスト時のモック注入
const mockEventStore = { load: vi.fn(), append: vi.fn() };
const testExecute = executeCommand.inject({ eventStore: mockEventStore });
await testExecute(command, "test-correlation");
```

## Hono + TanStack Query統合

```typescript
// features/<name>/api/routes.ts
export const routes = new Hono()
  .get("/", async (c) => {
    const result = await queryAll();
    return c.json({ data: result });
  })
  .post("/", zValidator("json", createSchema), async (c) => {
    const body = c.req.valid("json");
    const correlationId = crypto.randomUUID();
    const result = await executeCommand({ type: "Create", ...body }, correlationId);
    if (result.isErr()) return c.json({ error: result.error }, 400);
    return c.json({ data: { id: result.value.aggregateId } }, 201);
  });

// features/<name>/api/contracts.ts
import { hc } from "hono/client";
import type { routes } from "./routes";

const _client = hc<typeof routes>("/");
export type GetList = typeof _client.$get;
export type Create = typeof _client.$post;

// features/<name>/hooks/useList.ts
import { queryOptions } from "@tanstack/react-query";
import type { GetList } from "../api/contracts";

export const listQueryOptions = (getList: GetList) => queryOptions({
  queryKey: ["items", "list"],
  queryFn: async () => {
    const res = await getList();
    if (!res.ok) throw new Error("Failed");
    return (await res.json()).data;
  },
});
```

## Upcaster（スキーマ進化）

```typescript
// イベントスキーマが変更された場合の変換
const upcaster: Upcaster = {
  eventType: "ItemCreated",
  fromVersion: 1,
  toVersion: 2,
  upcast: (event) => ({
    ...event,
    data: {
      ...event.data,
      priority: event.data.priority ?? "medium",  // 新フィールド追加
    },
  }),
};

const chain = createUpcasterChain([upcaster]);
const upcastedEvents = chain.upcastAll(oldEvents);
```

## 起動時リプレイ

```typescript
// shared/infrastructure/startup.ts
export const initializeApp = depend(
  { db, eventStore, projector },
  async (deps) => {
    // 1. Projectionをクリア
    await deps.projector.clear();

    // 2. 全イベント取得（sequence順）
    const events = await deps.eventStore.getAllEvents();

    // 3. リプレイ
    for (const event of events) {
      if (handler.canHandle(event)) {
        await handler.handle(event);
      }
    }
  }
);
```
