#!/usr/bin/env npx tsx
/**
 * Widget Scaffolding Script
 *
 * 新しいwidgetのボイラープレートを生成する。
 * FSD構造に従ったwidget層の最小構成を作成。
 * 具体的なコンポーネントはドメインに合わせて追加する。
 *
 * @usage
 * ```bash
 * npx tsx .claude/skills/fsd-es-lite/scripts/scaffold-widget.ts <widget-name>
 * # Example: npx tsx .claude/skills/fsd-es-lite/scripts/scaffold-widget.ts dashboard
 * ```
 *
 * @generated
 * - src/widgets/<widget>/ui/<Widget>.tsx  - メインコンポーネント（実装必須）
 * - src/widgets/<widget>/ui/index.ts      - UIエクスポート
 * - src/widgets/<widget>/model/index.ts   - モデルエクスポート
 * - src/widgets/<widget>/index.ts         - パブリックAPI
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

function widgetComponentTemplate(name: string): string {
	const pascal = pascalCase(name);
	return `/**
 * ${pascal} Widget
 *
 * ${pascal}ウィジェットのメインコンポーネント。
 * 複数のentities/featuresを組み合わせた複合UIブロック。
 *
 * @module widgets/${name}/ui/${pascal}
 *
 * @todo 以下を実装する:
 * - 必要なentities/featuresからのimport
 * - propsの型定義
 * - UIレイアウトの実装
 * - 状態管理が必要な場合はmodel/state.tsを作成
 */

// =============================================================================
// Types
// =============================================================================

interface ${pascal}Props {
	/** ウィジェットのタイトル */
	title?: string;
	/** 子要素 */
	children?: React.ReactNode;
	// TODO: 必要なpropsを追加
}

// =============================================================================
// Component
// =============================================================================

/**
 * ${pascal}ウィジェット
 *
 * @todo ドメインに合わせて実装する
 *
 * @example
 * \`\`\`tsx
 * <${pascal} title="ダッシュボード">
 *   <SomeFeatureComponent />
 * </${pascal}>
 * \`\`\`
 */
export function ${pascal}({ title = "${pascal}", children }: ${pascal}Props) {
	// TODO: ドメインに合わせた実装
	return (
		<div className="rounded-lg border border-gray-200 bg-white shadow-sm">
			{/* Header */}
			<div className="border-b border-gray-200 px-4 py-3">
				<h2 className="text-lg font-semibold text-gray-900">{title}</h2>
			</div>

			{/* Content */}
			<div className="p-4">
				{children ?? (
					<div className="py-8 text-center text-gray-500">
						{/* TODO: デフォルトコンテンツを実装 */}
						コンテンツがありません
					</div>
				)}
			</div>
		</div>
	);
}
`;
}

function uiIndexTemplate(name: string): string {
	const pascal = pascalCase(name);
	return `/**
 * ${pascal} Widget UI Exports
 *
 * @module widgets/${name}/ui
 */

export { ${pascal} } from "./${pascal}";
`;
}

function modelIndexTemplate(name: string): string {
	const pascal = pascalCase(name);
	return `/**
 * ${pascal} Widget Model Exports
 *
 * @module widgets/${name}/model
 *
 * @description
 * ここにwidgetのローカル状態管理をexportする。
 * 例:
 * export { use${pascal}State } from "./state";
 * export type { ${pascal}State } from "./state";
 */

// TODO: 状態管理が必要な場合に追加
`;
}

function widgetIndexTemplate(name: string): string {
	const pascal = pascalCase(name);
	return `/**
 * ${pascal} Widget Public API
 *
 * @module widgets/${name}
 *
 * @description
 * widgetのパブリックAPIを定義。
 * 外部からはこのファイル経由でアクセスする。
 */

// UI Components
export * from "./ui";

// Model (状態管理が必要な場合)
export * from "./model";
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
		// UI
		{
			path: `widgets/${name}/ui/${pascal}.tsx`,
			content: widgetComponentTemplate(name),
		},
		{
			path: `widgets/${name}/ui/index.ts`,
			content: uiIndexTemplate(name),
		},

		// Model
		{
			path: `widgets/${name}/model/index.ts`,
			content: modelIndexTemplate(name),
		},

		// Public API
		{
			path: `widgets/${name}/index.ts`,
			content: widgetIndexTemplate(name),
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
			"Usage: npx tsx .claude/skills/fsd-es-lite/scripts/scaffold-widget.ts <widget-name>",
		);
		console.error(
			"Example: npx tsx .claude/skills/fsd-es-lite/scripts/scaffold-widget.ts dashboard",
		);
		process.exit(1);
	}

	const widgetName = args[0].toLowerCase().replace(/[^a-z0-9-_]/g, "");

	if (!widgetName) {
		console.error(
			"Invalid widget name. Use only letters, numbers, hyphens, and underscores.",
		);
		process.exit(1);
	}

	console.log(`\n🚀 Scaffolding widget: ${widgetName}\n`);

	const files = generateFiles(widgetName);

	for (const file of files) {
		writeFile(file.path, file.content);
	}

	const pascal = pascalCase(widgetName);

	console.log(`
✨ Widget scaffolded successfully!

Generated files:
- widgets/${widgetName}/ui/${pascal}.tsx   - メインコンポーネント ⚠️ 実装必須
- widgets/${widgetName}/ui/index.ts        - UIエクスポート
- widgets/${widgetName}/model/index.ts     - モデルエクスポート
- widgets/${widgetName}/index.ts           - パブリックAPI

⚠️ 実装が必要な項目:
1. ${pascal}.tsx: entities/featuresを組み合わせたUI実装（TODOコメント参照）
2. 状態管理が必要な場合はmodel/state.tsを作成してuseStateやuseReducerで管理
`);
}

main();
