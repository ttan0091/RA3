#!/usr/bin/env npx tsx
/**
 * Feature Scaffolding Script
 *
 * 新しいfeatureのボイラープレートを生成する。
 * FSD + CQRS + Event Sourcing パターンに従った構造を作成。
 *
 * @usage
 * ```bash
 * npx tsx .claude/skills/fsd-es-lite/scripts/scaffold-feature.ts <feature-name>
 * # Example: npx tsx .claude/skills/fsd-es-lite/scripts/scaffold-feature.ts user
 * ```
 *
 * @generated
 * - src/entities/<feature>/model/schema.ts    - Zodスキーマ
 * - src/entities/<feature>/model/events.ts    - イベント型定義
 * - src/features/<feature>/model/decide.ts    - 決定ロジック
 * - src/features/<feature>/model/apply.ts     - 適用ロジック
 * - src/features/<feature>/model/commands.ts  - コマンド実行
 * - src/features/<feature>/model/queries.ts   - クエリ実行
 * - src/features/<feature>/model/projector.ts - Projection更新
 * - src/features/<feature>/api/routes.ts      - APIルート
 * - src/features/<feature>/api/schemas.ts     - APIスキーマ
 */

import * as fs from "node:fs";
import * as path from "node:path";

// =============================================================================
// Configuration
// =============================================================================

const SRC_DIR = path.join(process.cwd(), "src");

// =============================================================================
// Template Functions
// =============================================================================

function capitalize(str: string): string {
	return str.charAt(0).toUpperCase() + str.slice(1);
}

function pascalCase(str: string): string {
	return str.split(/[-_]/).map(capitalize).join("");
}

// =============================================================================
// Templates
// =============================================================================

function entitySchemaTemplate(name: string): string {
	const pascal = pascalCase(name);
	return `/**
 * ${pascal} Entity Schema
 *
 * Zodを使用した${pascal}ドメインのスキーマ定義。
 *
 * @module entities/${name}/model/schema
 */

import { z } from "zod";

// =============================================================================
// Status
// =============================================================================

export const ${name}StatusSchema = z.enum(["active", "inactive", "deleted"]);
export type ${pascal}Status = z.infer<typeof ${name}StatusSchema>;

// =============================================================================
// Aggregate
// =============================================================================

/**
 * ${pascal}集約スキーマ
 */
export const ${name}AggregateSchema = z.object({
	id: z.string().uuid(),
	// TODO: Add domain-specific fields
	name: z.string().min(1).max(100),
	status: ${name}StatusSchema,
	version: z.number().int().nonnegative(),
	isDeleted: z.boolean(),
	createdAt: z.string().datetime(),
	updatedAt: z.string().datetime(),
});

export type ${pascal}Aggregate = z.infer<typeof ${name}AggregateSchema>;

// =============================================================================
// Projection
// =============================================================================

/**
 * ${pascal}投影スキーマ（isDeleted除外）
 */
export const ${name}ProjectionSchema = ${name}AggregateSchema.omit({ isDeleted: true });
export type ${pascal}Projection = z.infer<typeof ${name}ProjectionSchema>;
`;
}

function entityEventsTemplate(name: string): string {
	const pascal = pascalCase(name);
	const upper = name.toUpperCase();
	return `/**
 * ${pascal} Events
 *
 * ${pascal}ドメインのイベント型定義。
 *
 * @module entities/${name}/model/events
 */

import type { DomainEvent } from "@/shared/lib/event-store/types";

// =============================================================================
// Constants
// =============================================================================

export const ${upper}_AGGREGATE_TYPE = "${pascal}";

// =============================================================================
// Event Types
// =============================================================================

export type ${pascal}CreatedEvent = DomainEvent<
	"${pascal}Created",
	{
		name: string;
		// TODO: Add domain-specific fields
	}
>;

export type ${pascal}UpdatedEvent = DomainEvent<
	"${pascal}Updated",
	{
		name?: string;
		// TODO: Add domain-specific fields
	}
>;

export type ${pascal}DeletedEvent = DomainEvent<"${pascal}Deleted", object>;

// =============================================================================
// Union Type
// =============================================================================

export type ${pascal}Event =
	| ${pascal}CreatedEvent
	| ${pascal}UpdatedEvent
	| ${pascal}DeletedEvent;

// =============================================================================
// Event Factory Functions
// =============================================================================

interface EventMeta {
	id: string;
	aggregateId: string;
	version: number;
	timestamp: string;
	correlationId: string;
}

export function create${pascal}CreatedEvent(
	meta: EventMeta,
	data: ${pascal}CreatedEvent["data"],
): ${pascal}CreatedEvent {
	return {
		id: meta.id,
		type: "${pascal}Created",
		aggregateId: meta.aggregateId,
		aggregateType: ${upper}_AGGREGATE_TYPE,
		version: meta.version,
		timestamp: meta.timestamp,
		data,
		metadata: { correlationId: meta.correlationId },
	};
}

export function create${pascal}UpdatedEvent(
	meta: EventMeta,
	data: ${pascal}UpdatedEvent["data"],
): ${pascal}UpdatedEvent {
	return {
		id: meta.id,
		type: "${pascal}Updated",
		aggregateId: meta.aggregateId,
		aggregateType: ${upper}_AGGREGATE_TYPE,
		version: meta.version,
		timestamp: meta.timestamp,
		data,
		metadata: { correlationId: meta.correlationId },
	};
}

export function create${pascal}DeletedEvent(
	meta: EventMeta,
): ${pascal}DeletedEvent {
	return {
		id: meta.id,
		type: "${pascal}Deleted",
		aggregateId: meta.aggregateId,
		aggregateType: ${upper}_AGGREGATE_TYPE,
		version: meta.version,
		timestamp: meta.timestamp,
		data: {},
		metadata: { correlationId: meta.correlationId },
	};
}
`;
}

function featureDecideTemplate(name: string): string {
	const pascal = pascalCase(name);
	const upper = name.toUpperCase();
	return `/**
 * ${pascal} Decide - 決定ロジック（純粋関数）
 *
 * コマンドと現在状態から新しいイベントを生成する。
 *
 * @module features/${name}/model/decide
 */

import { ok, err, type Result } from "@/shared/lib/result";
import { DecisionError } from "@/shared/lib/errors";
import type { ${pascal}Aggregate } from "@/entities/${name}/model/schema";
import {
	type ${pascal}Event,
	${upper}_AGGREGATE_TYPE,
	create${pascal}CreatedEvent,
	create${pascal}UpdatedEvent,
	create${pascal}DeletedEvent,
} from "@/entities/${name}/model/events";

// =============================================================================
// Commands
// =============================================================================

export type Create${pascal}Command = {
	type: "Create${pascal}";
	name: string;
	// TODO: Add domain-specific fields
};

export type Update${pascal}Command = {
	type: "Update${pascal}";
	aggregateId: string;
	expectedVersion: number;
	name?: string;
	// TODO: Add domain-specific fields
};

export type Delete${pascal}Command = {
	type: "Delete${pascal}";
	aggregateId: string;
	expectedVersion: number;
};

export type ${pascal}Command =
	| Create${pascal}Command
	| Update${pascal}Command
	| Delete${pascal}Command;

// =============================================================================
// Meta
// =============================================================================

interface EventMeta {
	id: string;
	aggregateId: string;
	timestamp: string;
	correlationId: string;
	version: number;
}

// =============================================================================
// Decide Function
// =============================================================================

/**
 * ${pascal}コマンドを処理して新しいイベントを生成する
 */
export function decide${pascal}(
	state: ${pascal}Aggregate | null,
	command: ${pascal}Command,
	meta: EventMeta,
): Result<${pascal}Event[], DecisionError> {
	switch (command.type) {
		case "Create${pascal}":
			return decideCreate(state, command, meta);
		case "Update${pascal}":
			return decideUpdate(state, command, meta);
		case "Delete${pascal}":
			return decideDelete(state, command, meta);
		default: {
			const exhaustiveCheck: never = command;
			return err(
				new DecisionError(
					\`Unknown command type: \${(exhaustiveCheck as ${pascal}Command).type}\`,
				),
			);
		}
	}
}

function decideCreate(
	state: ${pascal}Aggregate | null,
	command: Create${pascal}Command,
	meta: EventMeta,
): Result<${pascal}Event[], DecisionError> {
	if (state !== null) {
		return err(new DecisionError("${pascal} already exists"));
	}

	return ok([
		create${pascal}CreatedEvent(meta, {
			name: command.name,
		}),
	]);
}

function decideUpdate(
	state: ${pascal}Aggregate | null,
	command: Update${pascal}Command,
	meta: EventMeta,
): Result<${pascal}Event[], DecisionError> {
	if (state === null) {
		return err(new DecisionError("${pascal} not found", 404));
	}
	if (state.isDeleted) {
		return err(new DecisionError("${pascal} is deleted", 410));
	}
	if (state.version !== command.expectedVersion) {
		return err(
			new DecisionError(
				\`Version mismatch: expected \${command.expectedVersion}, got \${state.version}\`,
				409,
			),
		);
	}

	// 変更がない場合はイベントを生成しない
	if (command.name === undefined) {
		return ok([]);
	}

	return ok([
		create${pascal}UpdatedEvent(meta, {
			name: command.name,
		}),
	]);
}

function decideDelete(
	state: ${pascal}Aggregate | null,
	command: Delete${pascal}Command,
	meta: EventMeta,
): Result<${pascal}Event[], DecisionError> {
	if (state === null) {
		return err(new DecisionError("${pascal} not found", 404));
	}
	if (state.isDeleted) {
		return ok([]); // 冪等性: 既に削除済みなら何もしない
	}
	if (state.version !== command.expectedVersion) {
		return err(
			new DecisionError(
				\`Version mismatch: expected \${command.expectedVersion}, got \${state.version}\`,
				409,
			),
		);
	}

	return ok([create${pascal}DeletedEvent(meta)]);
}
`;
}

function featureApplyTemplate(name: string): string {
	const pascal = pascalCase(name);
	return `/**
 * ${pascal} Apply - 適用ロジック（純粋関数）
 *
 * イベントを集約に適用する。
 *
 * @module features/${name}/model/apply
 */

import type { ${pascal}Event } from "@/entities/${name}/model/events";
import type { ${pascal}Aggregate } from "@/entities/${name}/model/schema";

/**
 * ${pascal}イベントを${pascal}集約に適用する
 */
export function apply${pascal}EventToAggregate(
	state: ${pascal}Aggregate | null,
	event: ${pascal}Event,
): ${pascal}Aggregate {
	switch (event.type) {
		case "${pascal}Created":
			return {
				id: event.aggregateId,
				name: event.data.name,
				status: "active",
				version: event.version,
				isDeleted: false,
				createdAt: event.timestamp,
				updatedAt: event.timestamp,
			};

		case "${pascal}Updated":
			if (!state) throw new Error("Cannot update non-existent ${pascal}");
			return {
				...state,
				name: event.data.name ?? state.name,
				version: event.version,
				updatedAt: event.timestamp,
			};

		case "${pascal}Deleted":
			if (!state) throw new Error("Cannot delete non-existent ${pascal}");
			return {
				...state,
				isDeleted: true,
				version: event.version,
				updatedAt: event.timestamp,
			};

		default: {
			const exhaustiveCheck: never = event;
			throw new Error(
				\`Unknown event type: \${(exhaustiveCheck as ${pascal}Event).type}\`,
			);
		}
	}
}
`;
}

function featureCommandsTemplate(name: string): string {
	const pascal = pascalCase(name);
	const upper = name.toUpperCase();
	return `/**
 * ${pascal} Commands - Write Path実装
 *
 * @module features/${name}/model/commands
 */

import { depend } from "velona";
import { decide${pascal}, type ${pascal}Command } from "./decide";
import { apply${pascal}EventToAggregate } from "./apply";
import { ok, err, type Result } from "@/shared/lib/result";
import type { DecisionError, ConflictError } from "@/shared/lib/errors";
import type { ${pascal}Event } from "@/entities/${name}/model/events";
import { ${upper}_AGGREGATE_TYPE } from "@/entities/${name}/model/events";
import type { ${pascal}Aggregate } from "@/entities/${name}/model/schema";
import type { IEventStore } from "@/shared/lib/event-store/EventStore";
import { eventStore as defaultEventStore } from "@/shared/lib/event-store/EventStore";
import { drizzle${pascal}Projector, type I${pascal}Projector } from "./projector";

// =============================================================================
// Constants
// =============================================================================

const AGGREGATE_TYPE = ${upper}_AGGREGATE_TYPE;

// =============================================================================
// Types
// =============================================================================

type CommandResult = Result<
	{ aggregateId: string; events: ${pascal}Event[] },
	DecisionError | ConflictError
>;

interface CommandDependencies {
	eventStore: IEventStore;
	projector: I${pascal}Projector;
	clock: () => string;
	idGen: () => string;
}

// =============================================================================
// Default Dependencies
// =============================================================================

const defaultDependencies: CommandDependencies = {
	eventStore: defaultEventStore,
	projector: drizzle${pascal}Projector,
	clock: () => new Date().toISOString(),
	idGen: () => crypto.randomUUID(),
};

// =============================================================================
// Command Executor
// =============================================================================

export const execute${pascal}Command = depend(
	defaultDependencies,
	async (
		deps,
		command: ${pascal}Command,
		correlationId: string,
	): Promise<CommandResult> => {
		const aggregateId =
			"aggregateId" in command ? command.aggregateId : deps.idGen();

		const { events, version } = await deps.eventStore.load(
			AGGREGATE_TYPE,
			aggregateId,
		);
		const state = events.reduce<${pascal}Aggregate | null>(
			(acc, event) => apply${pascal}EventToAggregate(acc, event as ${pascal}Event),
			null,
		);

		const meta = {
			id: deps.idGen(),
			aggregateId,
			timestamp: deps.clock(),
			correlationId,
			version: version + 1,
		};
		const decision = decide${pascal}(state, command, meta);
		if (decision.isErr()) {
			return err(decision.error);
		}

		if (decision.value.length === 0) {
			return ok({ aggregateId, events: [] });
		}

		const appendResult = await deps.eventStore.append(
			AGGREGATE_TYPE,
			aggregateId,
			decision.value,
			version,
		);
		if (appendResult.isErr()) {
			return err(appendResult.error);
		}

		const next = decision.value.reduce<${pascal}Aggregate | null>(
			(acc, event) => apply${pascal}EventToAggregate(acc, event),
			state,
		);

		if (next) {
			try {
				await deps.projector.save(next);
			} catch (error) {
				console.warn("Projection save failed:", error);
			}
		}

		return ok({ aggregateId, events: decision.value });
	},
);
`;
}

function featureProjectorTemplate(name: string): string {
	const pascal = pascalCase(name);
	return `/**
 * ${pascal} Projector - Projection更新ロジック
 *
 * @module features/${name}/model/projector
 */

import { eq } from "drizzle-orm";
import { depend } from "velona";
import type {
	${pascal}Aggregate,
	${pascal}Projection,
} from "@/entities/${name}/model/schema";
import type { DrizzleDatabase } from "@/shared/lib/db";
import { db as defaultDb } from "@/shared/lib/db";
// TODO: Import ${name}s table from schema when created
// import { ${name}s } from "@/shared/lib/db/schema";

// =============================================================================
// Interface
// =============================================================================

export interface I${pascal}Projector {
	save(aggregate: ${pascal}Aggregate): Promise<${pascal}Projection | null>;
	clear(): Promise<void>;
}

// =============================================================================
// Helper
// =============================================================================

function buildProjection(aggregate: ${pascal}Aggregate): ${pascal}Projection {
	const { isDeleted: _, ...projection } = aggregate;
	return projection;
}

// =============================================================================
// Projector Functions
// =============================================================================

interface ProjectorDeps {
	db: DrizzleDatabase;
}

export const save${pascal}Projection = depend(
	{ db: defaultDb },
	async (
		deps: ProjectorDeps,
		aggregate: ${pascal}Aggregate,
	): Promise<${pascal}Projection | null> => {
		// TODO: Implement when ${name}s table is created
		// if (aggregate.isDeleted) {
		//   await deps.db.delete(${name}s).where(eq(${name}s.id, aggregate.id));
		//   return null;
		// }
		// const projection = buildProjection(aggregate);
		// await deps.db.insert(${name}s).values({...}).onConflictDoUpdate({...});
		// return projection;

		console.warn("${pascal}Projector.save not implemented yet");
		return buildProjection(aggregate);
	},
);

export const clear${pascal}Projections = depend(
	{ db: defaultDb },
	async (deps: ProjectorDeps): Promise<void> => {
		// TODO: Implement when ${name}s table is created
		// await deps.db.delete(${name}s);
		console.warn("${pascal}Projector.clear not implemented yet");
	},
);

// =============================================================================
// Default Projector
// =============================================================================

export const drizzle${pascal}Projector: I${pascal}Projector = {
	save: (aggregate: ${pascal}Aggregate) => save${pascal}Projection(aggregate),
	clear: () => clear${pascal}Projections(),
};
`;
}

function featureQueriesTemplate(name: string): string {
	const pascal = pascalCase(name);
	return `/**
 * ${pascal} Queries - Read Path実装
 *
 * @module features/${name}/model/queries
 */

import { eq, desc } from "drizzle-orm";
import { depend } from "velona";
import type { ${pascal}Projection } from "@/entities/${name}/model/schema";
import { ok, err, type Result } from "@/shared/lib/result";
import { NotFoundError } from "@/shared/lib/errors";
import type { DrizzleDatabase } from "@/shared/lib/db";
import { db as defaultDb } from "@/shared/lib/db";
// TODO: Import ${name}s table from schema when created
// import { ${name}s } from "@/shared/lib/db/schema";

// =============================================================================
// Types
// =============================================================================

interface QueryDeps {
	db: DrizzleDatabase;
}

// =============================================================================
// Query Functions
// =============================================================================

export const queryAll${pascal}s = depend(
	{ db: defaultDb },
	async (deps: QueryDeps): Promise<Result<${pascal}Projection[], never>> => {
		// TODO: Implement when ${name}s table is created
		// const rows = await deps.db.select().from(${name}s).orderBy(desc(${name}s.createdAt));
		// return ok(rows);
		console.warn("queryAll${pascal}s not implemented yet");
		return ok([]);
	},
);

export const query${pascal}ById = depend(
	{ db: defaultDb },
	async (
		deps: QueryDeps,
		id: string,
	): Promise<Result<${pascal}Projection, NotFoundError>> => {
		// TODO: Implement when ${name}s table is created
		// const rows = await deps.db.select().from(${name}s).where(eq(${name}s.id, id));
		// if (rows.length === 0) {
		//   return err(new NotFoundError("${pascal}", id));
		// }
		// return ok(rows[0]);
		console.warn("query${pascal}ById not implemented yet");
		return err(new NotFoundError("${pascal}", id));
	},
);
`;
}

function featureApiSchemasTemplate(name: string): string {
	const pascal = pascalCase(name);
	return `/**
 * ${pascal} API Schemas
 *
 * APIリクエスト/レスポンスのZodスキーマ。
 *
 * @module features/${name}/api/schemas
 */

import { z } from "zod";

// =============================================================================
// Request Schemas
// =============================================================================

export const ${name}IdParamSchema = z.object({
	id: z.string().uuid(),
});

export const create${pascal}BodySchema = z.object({
	name: z.string().min(1).max(100),
	// TODO: Add domain-specific fields
});

export const update${pascal}BodySchema = z.object({
	name: z.string().min(1).max(100).optional(),
	expectedVersion: z.number().int().nonnegative(),
	// TODO: Add domain-specific fields
});

export const delete${pascal}BodySchema = z.object({
	expectedVersion: z.number().int().nonnegative(),
});

// =============================================================================
// Type Exports
// =============================================================================

export type ${pascal}IdParam = z.infer<typeof ${name}IdParamSchema>;
export type Create${pascal}Body = z.infer<typeof create${pascal}BodySchema>;
export type Update${pascal}Body = z.infer<typeof update${pascal}BodySchema>;
export type Delete${pascal}Body = z.infer<typeof delete${pascal}BodySchema>;
`;
}

function featureApiRoutesTemplate(name: string): string {
	const pascal = pascalCase(name);
	return `/**
 * ${pascal} API Routes
 *
 * @module features/${name}/api/routes
 */

import { zValidator } from "@hono/zod-validator";
import { Hono } from "hono";
import { execute${pascal}Command } from "../model/commands";
import { queryAll${pascal}s, query${pascal}ById } from "../model/queries";
import { validationHook } from "@/shared/lib/validation/zod-validator-hook";
import {
	${name}IdParamSchema,
	create${pascal}BodySchema,
	update${pascal}BodySchema,
	delete${pascal}BodySchema,
} from "./schemas";

// =============================================================================
// Route Factory
// =============================================================================

export const create${pascal}sApi = () => {
	return new Hono()
		// GET / - List all
		.get("/", async (c) => {
			const result = await queryAll${pascal}s();
			return c.json({ data: result.value }, 200);
		})

		// GET /:id - Get by ID
		.get(
			"/:id",
			zValidator("param", ${name}IdParamSchema, validationHook),
			async (c) => {
				const { id } = c.req.valid("param");
				const result = await query${pascal}ById(id);

				if (result.isErr()) {
					return c.json(
						{ error: result.error.toJSON() },
						result.error.httpStatus as 404,
					);
				}
				return c.json({ data: result.value }, 200);
			},
		)

		// POST / - Create
		.post(
			"/",
			zValidator("json", create${pascal}BodySchema, validationHook),
			async (c) => {
				const body = c.req.valid("json");
				const correlationId = crypto.randomUUID();
				const result = await execute${pascal}Command(
					{ type: "Create${pascal}", ...body },
					correlationId,
				);

				if (result.isErr()) {
					return c.json(
						{ error: result.error.toJSON() },
						result.error.httpStatus as 400 | 409,
					);
				}
				return c.json({ data: { id: result.value.aggregateId } }, 201);
			},
		)

		// PATCH /:id - Update
		.patch(
			"/:id",
			zValidator("param", ${name}IdParamSchema, validationHook),
			zValidator("json", update${pascal}BodySchema, validationHook),
			async (c) => {
				const { id } = c.req.valid("param");
				const body = c.req.valid("json");
				const correlationId = crypto.randomUUID();
				const result = await execute${pascal}Command(
					{ type: "Update${pascal}", aggregateId: id, ...body },
					correlationId,
				);

				if (result.isErr()) {
					return c.json(
						{ error: result.error.toJSON() },
						result.error.httpStatus as 400 | 404 | 409,
					);
				}
				return c.json({ success: true as const }, 200);
			},
		)

		// DELETE /:id - Delete
		.delete(
			"/:id",
			zValidator("param", ${name}IdParamSchema, validationHook),
			zValidator("json", delete${pascal}BodySchema, validationHook),
			async (c) => {
				const { id } = c.req.valid("param");
				const body = c.req.valid("json");
				const correlationId = crypto.randomUUID();
				const result = await execute${pascal}Command(
					{ type: "Delete${pascal}", aggregateId: id, ...body },
					correlationId,
				);

				if (result.isErr()) {
					return c.json(
						{ error: result.error.toJSON() },
						result.error.httpStatus as 400 | 404 | 409,
					);
				}
				return c.json({ success: true as const }, 200);
			},
		);
};

export type ${pascal}sApiType = ReturnType<typeof create${pascal}sApi>;
`;
}

// =============================================================================
// File Generation
// =============================================================================

interface FileSpec {
	path: string;
	content: string;
}

function generateFiles(name: string): FileSpec[] {
	return [
		// Entities
		{
			path: `entities/${name}/model/schema.ts`,
			content: entitySchemaTemplate(name),
		},
		{
			path: `entities/${name}/model/events.ts`,
			content: entityEventsTemplate(name),
		},

		// Features - Model
		{
			path: `features/${name}/model/decide.ts`,
			content: featureDecideTemplate(name),
		},
		{
			path: `features/${name}/model/apply.ts`,
			content: featureApplyTemplate(name),
		},
		{
			path: `features/${name}/model/commands.ts`,
			content: featureCommandsTemplate(name),
		},
		{
			path: `features/${name}/model/projector.ts`,
			content: featureProjectorTemplate(name),
		},
		{
			path: `features/${name}/model/queries.ts`,
			content: featureQueriesTemplate(name),
		},

		// Features - API
		{
			path: `features/${name}/api/schemas.ts`,
			content: featureApiSchemasTemplate(name),
		},
		{
			path: `features/${name}/api/routes.ts`,
			content: featureApiRoutesTemplate(name),
		},
	];
}

function ensureDir(dirPath: string): void {
	if (!fs.existsSync(dirPath)) {
		fs.mkdirSync(dirPath, { recursive: true });
	}
}

function writeFile(filePath: string, content: string): void {
	const fullPath = path.join(SRC_DIR, filePath);
	const dir = path.dirname(fullPath);
	ensureDir(dir);

	if (fs.existsSync(fullPath)) {
		console.log(`⚠️  Skipped (exists): ${filePath}`);
		return;
	}

	fs.writeFileSync(fullPath, content);
	console.log(`✅ Created: ${filePath}`);
}

// =============================================================================
// Main
// =============================================================================

function main(): void {
	const args = process.argv.slice(2);

	if (args.length === 0) {
		console.error(
			"Usage: npx tsx .claude/skills/fsd-es-lite/scripts/scaffold-feature.ts <feature-name>",
		);
		console.error(
			"Example: npx tsx .claude/skills/fsd-es-lite/scripts/scaffold-feature.ts user",
		);
		process.exit(1);
	}

	const featureName = args[0].toLowerCase().replace(/[^a-z0-9-_]/g, "");

	if (!featureName) {
		console.error(
			"Invalid feature name. Use only letters, numbers, hyphens, and underscores.",
		);
		process.exit(1);
	}

	console.log(`\n🚀 Scaffolding feature: ${featureName}\n`);

	const files = generateFiles(featureName);

	for (const file of files) {
		writeFile(file.path, file.content);
	}

	console.log(`
✨ Feature scaffolded successfully!

Next steps:
1. Add ${featureName}s table to src/shared/lib/db/schema.ts
2. Update projector.ts and queries.ts to use the new table
3. Add routes to entry-server.tsx: app.route("/api/${featureName}s", ${featureName}sApi)
4. Run \`pnpm db:generate && pnpm db:push\` to apply migrations
`);
}

main();
