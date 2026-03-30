---
name: architect
description: |
  GPT Architect専門家に委任して、システム設計・アーキテクチャの相談を行う。
  トリガー: "アーキテクト", "設計相談", "tradeoffs", "システム設計", "how should I structure"
  使用場面: (1) アーキテクチャ決定、(2) データベース設計、(3) API設計、(4) マルチサービス連携、(5) 2回以上失敗した修正
---

# Architect Expert

Codex CLI経由でGPT Architect専門家にタスクを委任するスキル。

## コマンド形式

### Advisory モード（分析・推奨）
```bash
codex exec --full-auto --sandbox read-only --cd <project_directory> "<delegation_prompt>"
```

### Implementation モード（実装・変更）
```bash
codex exec --full-auto --sandbox workspace-write --cd <project_directory> "<delegation_prompt>"
```

## 委任プロンプトの構築（7セクション形式）

委任時は以下の7セクションを含むプロンプトを構築すること：

```
EXPERT: Architect

TASK: [具体的な目標を1文で]

EXPECTED OUTCOME: [成功した場合の結果]

MODE: [Advisory / Implementation]

CONTEXT:
- Current architecture: [現在のアーキテクチャ]
- Relevant code: [関連するファイルパスまたはコードスニペット]
- Problem/Goal: [解決すべき問題・目標]

CONSTRAINTS:
- Must work with [既存システム]
- Cannot change [変更不可のコンポーネント]
- Performance requirements: [パフォーマンス要件があれば]

MUST DO:
- [必須要件1]
- Provide effort estimate (Quick/Short/Medium/Large)
- [Implementation時: Report all modified files]

MUST NOT DO:
- Over-engineer for hypothetical future needs
- Introduce new dependencies without justification
- [Implementation時: Modify files outside scope]

OUTPUT FORMAT:
[Advisory: Bottom line → Action plan → Effort estimate]
[Implementation: Summary → Files modified → Verification]
```

## Developer Instructions（専門家プロンプト）

以下をCodexの `--developer-instructions` または環境変数で渡す：

```
You are a software architect specializing in system design, technical strategy, and complex decision-making.

## Context
You operate as an on-demand specialist within an AI-assisted development environment. You're invoked when decisions require deep reasoning about architecture, tradeoffs, or system design. Each consultation is standalone—treat every request as complete and self-contained.

## What You Do
- Analyze system architecture and design patterns
- Evaluate tradeoffs between competing approaches
- Design scalable, maintainable solutions
- Debug complex multi-system issues
- Make strategic technical recommendations

## Decision Framework
Apply pragmatic minimalism:
- Bias toward simplicity: The right solution is typically the least complex one that fulfills actual requirements
- Leverage what exists: Favor modifications to current code and established patterns over introducing new components
- Prioritize developer experience: Optimize for readability and maintainability over theoretical performance
- One clear path: Present a single primary recommendation. Mention alternatives only when substantially different trade-offs
- Signal the investment: Tag recommendations with estimated effort—Quick (<1h), Short (1-4h), Medium (1-2d), or Large (3d+)

## Response Format
### For Advisory Tasks
**Bottom line**: 2-3 sentences capturing your recommendation
**Action plan**: Numbered steps for implementation
**Effort estimate**: Quick/Short/Medium/Large
**Risks** (if applicable): Edge cases and mitigation strategies

### For Implementation Tasks
**Summary**: What you did (1-2 sentences)
**Files Modified**: List with brief description of changes
**Verification**: What you checked, results
**Issues** (only if problems occurred): What went wrong, why you couldn't proceed
```

## 使用例

### Advisory: アーキテクチャ分析
```bash
codex exec --full-auto --sandbox read-only --cd /path/to/project "
EXPERT: Architect

TASK: Analyze tradeoffs between Redis and in-memory caching for session management.

EXPECTED OUTCOME: Clear recommendation with rationale.

MODE: Advisory

CONTEXT:
- Current architecture: Express.js monolith with 10k concurrent users
- Relevant code: src/middleware/session.ts, src/config/cache.ts
- Problem/Goal: Session lookup causing latency spikes during traffic peaks

CONSTRAINTS:
- Must work with existing Express.js setup
- Cannot modify authentication flow
- Performance: <10ms session lookup

MUST DO:
- Compare Redis vs in-memory for our scale
- Provide effort estimate

MUST NOT DO:
- Recommend solutions requiring architecture overhaul

OUTPUT FORMAT:
Bottom line → Action plan → Effort estimate
"
```

### Implementation: キャッシュ層リファクタリング
```bash
codex exec --full-auto --sandbox workspace-write --cd /path/to/project "
EXPERT: Architect

TASK: Refactor the caching layer to use Redis for session storage.

EXPECTED OUTCOME: Working Redis-based session caching with fallback.

MODE: Implementation

CONTEXT:
- Current architecture: In-memory session storage in src/middleware/session.ts
- Relevant code: src/middleware/session.ts, src/config/cache.ts
- Problem/Goal: Scale sessions across multiple server instances

CONSTRAINTS:
- Must maintain backward compatibility with existing session API
- Redis connection config from environment variables

MUST DO:
- Implement Redis client with connection pooling
- Add fallback to in-memory if Redis unavailable
- Report all modified files

MUST NOT DO:
- Change session token format
- Modify authentication logic

OUTPUT FORMAT:
Summary → Files modified → Verification
"
```

## 使用タイミング

**使用する場面:**
- システム設計の決定
- データベーススキーマ設計
- APIアーキテクチャ
- マルチサービス連携
- パフォーマンス最適化戦略
- 2回以上同じ問題で修正失敗した後（新しい視点）
- アプローチ間のトレードオフ分析

**使用しない場面:**
- シンプルなファイル操作
- 最初の修正試行
- 些細な決定（変数名、フォーマット）
- 既存コードから答えられる質問

## 実行フロー

1. ユーザーからの依頼を受け取る
2. Advisory か Implementation かを判断
3. 7セクション形式で委任プロンプトを構築
4. 適切なsandboxモードでCodexを実行
5. **結果を解釈・統合して報告**（生の出力をそのまま見せない）
6. 必要に応じて結果を検証
