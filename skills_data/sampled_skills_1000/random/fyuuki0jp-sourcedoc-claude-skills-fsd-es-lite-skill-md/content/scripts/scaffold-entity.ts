#!/usr/bin/env npx tsx
/**
 * Entity Scaffolding Script
 *
 * 新しいentityのボイラープレートを生成する。
 * FSD構造に従ったentity層のモデルファイルのみを作成。
 * UIは生成しない（ドメインに合わせて必要なものを追加する）。
 *
 * @usage
 * ```bash
 * npx tsx .claude/skills/fsd-es-lite/scripts/scaffold-entity.ts <entity-name>
 * # Example: npx tsx .claude/skills/fsd-es-lite/scripts/scaffold-entity.ts product
 * ```
 *
 * @generated
 * - src/entities/<entity>/model/schema.ts    - Zodスキーマ
 * - src/entities/<entity>/model/events.ts    - イベント型定義
 * - src/entities/<entity>/model/index.ts     - エクスポート
 * - src/entities/<entity>/ui/<Entity>.tsx    - UIコンポーネント（実装必須）
 * - src/entities/<entity>/ui/index.ts        - UIエクスポート
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

function schemaTemplate(name: string): string {
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
// Status（必要に応じてカスタマイズ）
// =============================================================================

export const ${name}StatusSchema = z.enum(["active", "inactive", "archived"]);
export type ${pascal}Status = z.infer<typeof ${name}StatusSchema>;

// =============================================================================
// Aggregate（イベントリプレイ後の状態）
// =============================================================================

/**
 * ${pascal}集約スキーマ
 *
 * @description
 * イベントリプレイ後の完全な状態を表す。
 * ドメインに合わせてフィールドを追加する。
 */
export const ${name}AggregateSchema = z.object({
	id: z.string().uuid(),
	// TODO: ドメイン固有フィールドを追加
	name: z.string().min(1).max(100),
	status: ${name}StatusSchema,
	// メタデータ
	version: z.number().int().nonnegative(),
	isDeleted: z.boolean(),
	createdAt: z.string().datetime(),
	updatedAt: z.string().datetime(),
});

export type ${pascal}Aggregate = z.infer<typeof ${name}AggregateSchema>;

// =============================================================================
// Projection（クエリ用、isDeleted除外）
// =============================================================================

/**
 * ${pascal}投影スキーマ
 *
 * @description
 * クエリ用の投影。isDeletedを除外。
 */
export const ${name}ProjectionSchema = ${name}AggregateSchema.omit({ isDeleted: true });
export type ${pascal}Projection = z.infer<typeof ${name}ProjectionSchema>;
`;
}

function eventsTemplate(name: string): string {
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
		// TODO: 初期データのフィールドを追加
	}
>;

export type ${pascal}UpdatedEvent = DomainEvent<
	"${pascal}Updated",
	{
		name?: string;
		// TODO: 更新可能フィールドを追加
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

function modelIndexTemplate(name: string): string {
	return `/**
 * ${pascalCase(name)} Model Exports
 *
 * @module entities/${name}/model
 */

export * from "./schema";
export * from "./events";
`;
}

function uiComponentTemplate(name: string): string {
	const pascal = pascalCase(name);
	return `/**
 * ${pascal} UI Component
 *
 * ${pascal}エンティティの表示コンポーネント。
 * entities層のUIは表示専用（stateless）で、状態を持たない。
 *
 * @module entities/${name}/ui/${pascal}
 *
 * @todo 以下を実装する:
 * - propsの型定義（${pascal}Projectionを受け取る）
 * - 表示ロジック（ドメインに合わせたUI）
 * - イベントハンドラの受け取り（onEdit, onDelete等）
 */

import type { ${pascal}Projection } from "../model/schema";

// =============================================================================
// Types
// =============================================================================

interface ${pascal}Props {
	/** 表示するエンティティ */
	${name}: ${pascal}Projection;
	/** 編集ハンドラ（オプション） */
	onEdit?: (id: string) => void;
	/** 削除ハンドラ（オプション） */
	onDelete?: (id: string) => void;
}

// =============================================================================
// Component
// =============================================================================

/**
 * ${pascal}表示コンポーネント
 *
 * @todo ドメインに合わせてUIを実装する
 *
 * @example
 * \`\`\`tsx
 * <${pascal}
 *   ${name}={${name}Data}
 *   onEdit={(id) => navigate(\`/${name}s/\${id}/edit\`)}
 *   onDelete={(id) => deleteMutation.mutate(id)}
 * />
 * \`\`\`
 */
export function ${pascal}({ ${name}, onEdit, onDelete }: ${pascal}Props) {
	// TODO: ドメインに合わせたUIを実装
	return (
		<div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
			<div className="flex items-start justify-between">
				<div className="flex-1">
					{/* TODO: エンティティの主要情報を表示 */}
					<h3 className="text-lg font-semibold text-gray-900">
						{${name}.name}
					</h3>
					<p className="mt-1 text-sm text-gray-500">
						ID: {${name}.id}
					</p>
				</div>
				<div className="flex gap-2">
					{onEdit && (
						<button
							type="button"
							onClick={() => onEdit(${name}.id)}
							className="text-sm text-blue-600 hover:text-blue-800"
						>
							編集
						</button>
					)}
					{onDelete && (
						<button
							type="button"
							onClick={() => onDelete(${name}.id)}
							className="text-sm text-red-600 hover:text-red-800"
						>
							削除
						</button>
					)}
				</div>
			</div>
			<div className="mt-2 text-sm text-gray-500">
				作成: {new Date(${name}.createdAt).toLocaleString("ja-JP")}
			</div>
		</div>
	);
}
`;
}

function uiIndexTemplate(name: string): string {
	const pascal = pascalCase(name);
	return `/**
 * ${pascal} UI Exports
 *
 * @module entities/${name}/ui
 */

export { ${pascal} } from "./${pascal}";
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
	const pascal = pascalCase(name);
	return [
		// Model
		{
			path: `entities/${name}/model/schema.ts`,
			content: schemaTemplate(name),
		},
		{
			path: `entities/${name}/model/events.ts`,
			content: eventsTemplate(name),
		},
		{
			path: `entities/${name}/model/index.ts`,
			content: modelIndexTemplate(name),
		},
		// UI
		{
			path: `entities/${name}/ui/${pascal}.tsx`,
			content: uiComponentTemplate(name),
		},
		{
			path: `entities/${name}/ui/index.ts`,
			content: uiIndexTemplate(name),
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
			"Usage: npx tsx .claude/skills/fsd-es-lite/scripts/scaffold-entity.ts <entity-name>",
		);
		console.error(
			"Example: npx tsx .claude/skills/fsd-es-lite/scripts/scaffold-entity.ts product",
		);
		process.exit(1);
	}

	const entityName = args[0].toLowerCase().replace(/[^a-z0-9-_]/g, "");

	if (!entityName) {
		console.error(
			"Invalid entity name. Use only letters, numbers, hyphens, and underscores.",
		);
		process.exit(1);
	}

	console.log(`\n🚀 Scaffolding entity: ${entityName}\n`);

	const files = generateFiles(entityName);

	for (const file of files) {
		writeFile(file.path, file.content);
	}

	const pascal = pascalCase(entityName);
	console.log(`
✨ Entity scaffolded successfully!

Generated files:
- entities/${entityName}/model/schema.ts   - Zodスキーマ
- entities/${entityName}/model/events.ts   - イベント型定義
- entities/${entityName}/model/index.ts    - エクスポート
- entities/${entityName}/ui/${pascal}.tsx  - UIコンポーネント ⚠️ 実装必須
- entities/${entityName}/ui/index.ts       - UIエクスポート

⚠️ 実装が必要な項目:
1. schema.ts: ドメイン固有フィールドを追加（TODOコメント参照）
2. events.ts: イベントデータのフィールドを追加（TODOコメント参照）
3. ${pascal}.tsx: ドメインに合わせたUI表示を実装（TODOコメント参照）
`);
}

main();
