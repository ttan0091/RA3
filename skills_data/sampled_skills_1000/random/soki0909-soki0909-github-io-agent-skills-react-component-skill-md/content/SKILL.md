---
name: react-component
description: React + TypeScript コンポーネント作成ガイド
---

# React コンポーネント作成スキル

このプロジェクトでのReactコンポーネント作成規約とベストプラクティス。

## ディレクトリ構造

```
src/
├── components/      # 共通コンポーネント
├── pages/           # ページコンポーネント
├── hooks/           # カスタムフック
├── contexts/        # React Context
├── types/           # 型定義
└── utils/           # ユーティリティ
```

## コンポーネント作成手順

### 1. 型を先に定義する

`src/types/dataModels.ts` に型を追加：

```typescript
export interface NewComponentProps {
  title: string;
  items: string[];
  onAction?: () => void;
}
```

### 2. コンポーネントを作成

```typescript
import type { NewComponentProps } from '../types/dataModels';

export const NewComponent: React.FC<NewComponentProps> = ({
  title,
  items,
  onAction,
}) => {
  // 防御的プログラミング：必ずチェック
  if (!title || !Array.isArray(items)) return null;
  if (items.length === 0) return null;

  return (
    <section className="...">
      <h2>{title}</h2>
      {items.map((item, index) => (
        <div key={index}>{item}</div>
      ))}
    </section>
  );
};
```

## 命名規則

| 種別             | 規則            | 例                            |
| ---------------- | --------------- | ----------------------------- |
| コンポーネント   | PascalCase      | `MediaPlayer.tsx`             |
| フック           | camelCase + use | `useTimeline.ts`              |
| イベントハンドラ | handle + 動詞   | `handleClick`, `handleSubmit` |
| 定数             | UPPER_SNAKE     | `MAX_ITEMS`                   |

## 必須パターン

### 防御的レンダリング

```typescript
// ✅ 必須
const renderItems = () => {
  if (!Array.isArray(data?.items)) return null;
  if (data.items.length === 0) return <p>項目がありません</p>;
  return data.items.map(...);
};

// ❌ 禁止
data.items.map(...)
```

### Optional Chaining

```typescript
// ✅ 推奨
const value = obj?.nested?.value ?? 'default';

// ❌ 禁止
const value = obj.nested.value;
```

## スタイリング (Tailwind CSS 4)

```tsx
// インラインクラス
<div className="bg-gray-900 text-white p-4 rounded-lg">

// 条件付きクラス
<div className={cn(
  "base-class",
  isActive && "active-class",
  variant === 'primary' ? 'primary-style' : 'secondary-style'
)}>
```

## ファイル作成後のチェック

```bash
npm run format    # フォーマット
npm run lint      # ESLint
npm run build     # 型チェック
```
