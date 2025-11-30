# packages/lib セットアップタスク

## 概要

packages/lib に React を用いた共通ライブラリを構築する。UIコンポーネント、スキーマ、ドメインロジックを管理し、apps/desktop (Electron) と apps/web (Next.js App Router) の両方から利用可能にする。

## 前提条件

- Tailwind CSS v4.1 を使用
- apps としては Electron デスクトップアプリと Next.js Web アプリを想定
- TypeScript を使用
- モノレポ構成（既存の packages/core, packages/api, packages/cli は Python ベース）
- Valibot を使用（軽量なバリデーションライブラリ）

## 設計原則

### 環境非依存の実装

- **含めるもの**: UIコンポーネント、スキーマ、ドメインロジック（純粋関数）、型定義、ユーティリティ
- **含めないもの**: ルーティング、環境固有のAPI (Electron IPC, Server Actions)、データフェッチング

### Next.js と Electron の互換性

- すべてのインタラクティブコンポーネントに `'use client'` ディレクティブを使用
- Electron では `'use client'` は無視され、Next.js では Client Component として扱われる
- 環境依存の機能は抽象インターフェースとして定義し、各 app で実装

### コンポーネント設計パターン

- **Compound Component Pattern**: 基本的なコンポーネント設計パターンとして採用
- **スコープ付きステート管理**: 共通コンポーネントやドメイン固有コンポーネントでは、valtio を用いた Provider パターンでスコープに閉じた状態管理を実装

---

## Phase 1: プロジェクト基盤のセットアップ

### 1.1 パッケージマネージャーとワークスペース設定

- [ ] **pnpm** をパッケージマネージャーとして使用
- [ ] pnpm のインストール (`npm install -g pnpm`)
- [ ] ルート pnpm-workspace.yaml の作成

  ```yaml
  packages:
    - "packages/*"
    - "apps/*"
  ```

- [ ] ルート package.json にワークスペース設定を追加
- [ ] packages/lib のディレクトリ作成
- [ ] packages/lib/package.json の初期設定

### 1.2 TypeScript 環境構築

- [ ] packages/lib/tsconfig.json の作成
  - React 用の設定（JSX サポート）
  - パス alias 設定（`@/` など）
  - 型定義の出力設定
- [ ] ルート tsconfig.json の作成（共通設定）
- [ ] 型定義ファイルのビルド設定

### 1.3 ビルドツール設定（tsdown）

- [ ] **tsdown** をビルドツールとして使用
  - React + Tailwind CSS ライブラリに最適化
  - Rust 製で超高速（tsup の 10-30倍）
  - TypeScript 型定義ファイル (.d.ts) を自動生成
- [ ] tsdown のインストール (`pnpm add -D tsdown`)
- [ ] tsdown.config.ts の作成

  ```typescript
  import { defineConfig } from "tsdown";

  export default defineConfig({
    entry: ["src/index.ts"],
    format: ["esm"],
    dts: true,
    clean: true,
    external: ["react", "react/jsx-runtime", "react-dom"],
  });
  ```

- [ ] Tailwind CSS プラグインのインストール
  - `pnpm add -D @bosh-code/tsdown-plugin-tailwindcss`
  - `pnpm add -D @bosh-code/tsdown-plugin-inject-css`
- [ ] package.json にビルドスクリプト追加

  ```json
  {
    "scripts": {
      "build": "tsdown",
      "dev": "tsdown --watch"
    }
  }
  ```

- [ ] エントリポイントの設定（main, module, types フィールド）
- [ ] package.json に `"sideEffects": false` を設定し、CSS が src/index.ts のインポート経由でバンドルされることを確認
  - CSS は src/index.ts で `import './styles/globals.css'` としてインポート
  - tsdown が CSS を JS に自動インジェクトし、dist/index.js 経由で適用される

---

## Phase 2: Tailwind CSS セットアップ

### 2.1 Tailwind CSS インストールと設定

- [ ] Tailwind CSS v4 のインストール (`pnpm add -D tailwindcss`)
- [ ] src/styles/globals.css の作成（Tailwind v4 の CSS ベース設定）

  ```css
  @import "tailwindcss";

  /* テーマカスタマイズ (CSS 変数で定義) */
  @theme {
    /* カラーパレット */
    --color-primary: #3b82f6;
    --color-secondary: #8b5cf6;
    --color-accent: #f59e0b;

    /* フォント */
    --font-sans: "Inter", system-ui, sans-serif;
    --font-mono: "Fira Code", monospace;

    /* スペーシング */
    --spacing-xs: 0.5rem;
    --spacing-sm: 1rem;
    --spacing-md: 1.5rem;
    --spacing-lg: 2rem;
    --spacing-xl: 3rem;

    /* ブレークポイント */
    --breakpoint-sm: 640px;
    --breakpoint-md: 768px;
    --breakpoint-lg: 1024px;
    --breakpoint-xl: 1280px;
  }
  ```

- [ ] プラグインが必要な場合は、CSS の `@plugin` ディレクティブで追加
  ```css
  @plugin "@tailwindcss/forms";
  ```

- [ ] tsdown.config.ts に Tailwind プラグインを追加

  ```typescript
  import { defineConfig } from "tsdown";
  import tailwindcss from "@bosh-code/tsdown-plugin-tailwindcss";
  import injectCSS from "@bosh-code/tsdown-plugin-inject-css";

  export default defineConfig({
    entry: ["src/index.ts"],
    format: ["esm"],
    dts: true,
    clean: true,
    external: ["react", "react/jsx-runtime", "react-dom"],
    plugins: [tailwindcss(), injectCSS()],
  });
  ```

### 2.2 CSS バンドル設定

- [ ] tsdown の CSS プラグインによる自動バンドル
  - `@bosh-code/tsdown-plugin-inject-css` が CSS を自動的に JavaScript にインジェクト
  - ビルド時に CSS が dist/ にバンドルされる
- [ ] package.json の sideEffects フィールドを `false` に設定

  ```json
  {
    "sideEffects": false
  }
  ```

- [ ] src/index.ts で `import './styles/globals.css';` を行い、tsdown が CSS を JS に自動インジェクト

  ```typescript
  import "./styles/globals.css";
  ```

  - dist/index.js のインポートのみで CSS が適用されることを確認

- [ ] apps/desktop での動作確認
  - `import { Button } from '@teto/lib'` のみで CSS が自動的に適用されることを確認
  - lib の Tailwind CSS テーマ（`@theme` で定義した変数）が適用されることを確認
- [ ] apps/web での動作確認
  - Next.js でも CSS が正しく適用されることを確認
  - lib の Tailwind CSS テーマが正しく継承されていることを確認
  - transpilePackages が設定されていることを再確認

---

## Phase 3: ディレクトリ構造とアーキテクチャ

### 3.1 基本ディレクトリ構造の作成

```
packages/lib/
├── src/
│   ├── components/           # UIコンポーネント
│   │   ├── ui/              # 基本UIコンポーネント
│   │   │   ├── button/
│   │   │   │   ├── button.tsx
│   │   │   │   ├── button.test.tsx
│   │   │   │   ├── button.stories.tsx
│   │   │   │   └── index.ts
│   │   │   ├── input/
│   │   │   ├── card/
│   │   │   └── index.ts
│   │   ├── layout/          # レイアウトコンポーネント
│   │   │   ├── container/
│   │   │   ├── grid/
│   │   │   ├── stack/
│   │   │   └── index.ts
│   │   ├── feedback/        # フィードバックコンポーネント
│   │   │   ├── alert/
│   │   │   ├── toast/
│   │   │   ├── spinner/
│   │   │   └── index.ts
│   │   └── index.ts
│   │
│   ├── schemas/             # Valibot スキーマ定義
│   │   ├── video/
│   │   │   ├── project.schema.ts
│   │   │   ├── timeline.schema.ts
│   │   │   └── index.ts
│   │   ├── subtitle/
│   │   │   ├── subtitle.schema.ts
│   │   │   ├── style.schema.ts
│   │   │   └── index.ts
│   │   ├── animation/
│   │   │   ├── animation.schema.ts
│   │   │   ├── keyframe.schema.ts
│   │   │   └── index.ts
│   │   ├── common/
│   │   │   ├── primitives.schema.ts  # 基本型（Color, Duration など）
│   │   │   └── index.ts
│   │   └── index.ts
│   │
│   ├── domain/              # ドメインロジック
│   │   ├── interfaces/      # 環境依存機能の抽象インターフェース
│   │   │   ├── project-storage.ts
│   │   │   ├── file-system.ts
│   │   │   └── index.ts
│   │   ├── video/
│   │   │   ├── video-project.ts
│   │   │   ├── timeline.ts
│   │   │   ├── operations/
│   │   │   │   ├── create-project.ts
│   │   │   │   ├── export-project.ts
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   ├── subtitle/
│   │   │   ├── subtitle.ts
│   │   │   ├── subtitle-style.ts
│   │   │   ├── operations/
│   │   │   │   ├── parse-subtitle.ts
│   │   │   │   ├── format-subtitle.ts
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   ├── animation/
│   │   │   ├── animation.ts
│   │   │   ├── keyframe.ts
│   │   │   ├── operations/
│   │   │   │   ├── interpolate.ts
│   │   │   │   ├── easing.ts
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   └── index.ts
│   │
│   ├── hooks/               # カスタムフック
│   │   ├── use-project.ts
│   │   ├── use-timeline.ts
│   │   ├── use-validation.ts
│   │   ├── use-debounce.ts
│   │   └── index.ts
│   │
│   ├── stores/              # グローバルステート管理（valtio）
│   │   ├── global-store.ts
│   │   ├── use-global-store.ts
│   │   └── index.ts
│   │
│   ├── utils/               # ユーティリティ関数
│   │   ├── validation/
│   │   │   ├── validate.ts
│   │   │   ├── parse.ts
│   │   │   └── index.ts
│   │   ├── formatting/
│   │   │   ├── time.ts
│   │   │   ├── color.ts
│   │   │   └── index.ts
│   │   ├── cn.ts           # className マージユーティリティ
│   │   └── index.ts
│   │
│   ├── types/               # 共通型定義
│   │   ├── common.ts
│   │   ├── component.ts
│   │   └── index.ts
│   │
│   ├── constants/           # 定数定義
│   │   ├── colors.ts
│   │   ├── animations.ts
│   │   └── index.ts
│   │
│   └── index.ts             # メインエントリポイント
│
├── styles/
│   ├── globals.css          # Tailwind CSS ディレクティブ
│   └── themes/
│       └── default.css      # カスタムテーマ変数
│
├── .storybook/              # Storybook 設定（オプション）
│   ├── main.ts
│   ├── preview.ts
│   └── preview-head.html
│
├── __tests__/               # 統合テスト
│   └── setup.ts
│
├── scripts/                 # ビルド・開発スクリプト
│   └── build-css.ts
│
├── tsconfig.json
├── tsconfig.build.json
├── tsdown.config.ts         # tsdown 設定
├── .eslintrc.json
├── .prettierrc
├── vitest.config.ts
├── package.json
└── README.md
```

- [ ] 上記ディレクトリ構造の作成
- [ ] 各主要ディレクトリに index.ts を配置（barrel exports）
- [ ] .gitignore の設定（dist/, node_modules/, .turbo/ など）
- [ ] README.md の基本構造作成

**ディレクトリ構成の設計思想**:

- **components/**: 機能別に分類（ui, layout, feedback）してスケーラビリティを確保
  - 各コンポーネントはフォルダ単位で管理（コンポーネント本体、テスト、Storybook を同居）
  - インタラクティブなコンポーネントには `'use client'` ディレクティブを追加
- **schemas/**: ドメイン別に分類（video, subtitle, animation）
  - Valibot スキーマと型定義を一箇所で管理
- **domain/**: ビジネスロジックをドメイン別に整理
  - **interfaces/**: 環境依存機能の抽象インターフェース（Electron, Next.js の両方で実装）
  - operations/ でドメイン操作を純粋関数として実装
- **hooks/**: カスタムフックを集約してコンポーネントから分離
  - `'use client'` ディレクティブが必要
- **stores/**: グローバルステート管理（valtio）
  - モジュールレベルで `proxy()` をエクスポート
  - カスタムフックで Facade パターンを実装
- **utils/**: 機能別にサブディレクトリ化（validation, formatting など）
- **constants/**: マジックナンバーを避けるための定数管理

### 3.2 エクスポート戦略の設計

- [ ] package.json の exports フィールド設定例
  - CSS の独立エクスポート (`"./styles"`) は削除し、メインエントリポイント (`.`) に一本化:

  ```json
  {
    "exports": {
      ".": {
        "types": "./dist/index.d.ts",
        "import": "./dist/index.js"
      },
      "./components": {
        "types": "./dist/components/index.d.ts",
        "import": "./dist/components/index.js"
      },
      "./components/ui": {
        "types": "./dist/components/ui/index.d.ts",
        "import": "./dist/components/ui/index.js"
      },
      "./schemas": {
        "types": "./dist/schemas/index.d.ts",
        "import": "./dist/schemas/index.js"
      },
      "./domain": {
        "types": "./dist/domain/index.d.ts",
        "import": "./dist/domain/index.js"
      },
      "./hooks": {
        "types": "./dist/hooks/index.d.ts",
        "import": "./dist/hooks/index.js"
      },
      "./stores": {
        "types": "./dist/stores/index.d.ts",
        "import": "./dist/stores/index.js"
      },
      "./utils": {
        "types": "./dist/utils/index.d.ts",
        "import": "./dist/utils/index.js"
      }
    }
  }
  ```

- [ ] Tree-shaking 対応の確認
- [ ] サイドエフェクトの有無を package.json に明記（`"sideEffects": ["*.css"]`）

---

## Phase 4: 開発環境とツール

### 4.1 コード品質ツール

- [ ] ESLint 設定
  - React hooks ルール
  - TypeScript ルール
  - Tailwind CSS クラス順序（prettier-plugin-tailwindcss）
- [ ] Prettier 設定
- [ ] packages/lib/.eslintrc.json 作成
- [ ] packages/lib/.prettierrc 作成

### 4.2 テスト環境

- [ ] テストフレームワークの選定（Vitest）
- [ ] React Testing Library のセットアップ
- [ ] テスト設定ファイルの作成
- [ ] サンプルテストの作成

### 4.3 開発用ツール

- [ ] Storybook のセットアップ（コンポーネントカタログ）
- [ ] または代替の開発環境（Vite でのプレイグラウンドなど）
- [ ] ホットリロード設定

---

## Phase 5: UI コンポーネント基盤

### 5.1 デザインシステムの基礎

- [ ] カラーパレットの定義（src/styles/globals.css の `@theme` 内）
  - プライマリ、セカンダリ、アクセントカラー
  - セマンティックカラー（success, warning, error など）
- [ ] タイポグラフィ設定（`@theme` 内）
  - フォントファミリー
  - フォントサイズスケール
  - 行間
- [ ] スペーシングシステム（`@theme` 内）
  - 一貫したスペーシングスケール
- [ ] ブレークポイント定義（`@theme` 内）
  - モバイル、タブレット、デスクトップ

### 5.2 基本コンポーネントの実装

- [ ] **class-variance-authority (cva) のインストール（必須）**
  - `pnpm add class-variance-authority`
  - バリアント管理に必須のライブラリ
- [ ] Button コンポーネント
  - **重要**: ファイル先頭に `'use client'` ディレクティブを追加
  - **必須**: class-variance-authority を使用してバリアント管理
  - バリアント（primary, secondary, outline など）
  - サイズ（sm, md, lg）
  - disabled, loading 状態
  - **実装後、直ちに Phase 8 の apps/desktop および apps/web でのインポートと動作確認を先行実行**
    - `import { Button } from '@teto/lib'` で CSS が適用されることを確認
    - 両環境で同じスタイルが適用されることを確認
- [ ] Input コンポーネント
  - **重要**: `'use client'` ディレクティブを追加
  - cva でバリアント管理
- [ ] Card コンポーネント
  - インタラクティブな機能がない場合は `'use client'` 不要
  - cva でバリアント管理（必要に応じて）
- [ ] Layout コンポーネント（Container, Grid など）
  - インタラクティブな機能がない場合は `'use client'` 不要

### 5.3 コンポーネント設計パターン

- [ ] コンポーネント Props の型定義方法
- [ ] **Compound Components パターンの採用（基本方針）**
  - 親コンポーネントと子コンポーネントを組み合わせて柔軟性を提供
  - Context API または valtio で状態を共有
  - 例: `<Select>`, `<Select.Trigger>`, `<Select.Content>`, `<Select.Item>`
- [ ] スタイリング手法
  - **必須**: class-variance-authority (cva) でバリアント管理
  - clsx と tailwind-merge で className マージ
- [ ] `'use client'` ディレクティブの使用ルール策定
  - イベントハンドラー (onClick, onChange など) を使用するコンポーネント
  - React hooks (useState, useEffect など) を使用するコンポーネント
  - ブラウザ API (localStorage, window など) を使用するコンポーネント
- [ ] 複雑なコンポーネント（Dialog, Select など）の実装方針
  - 必要になった場合、Radix UI の導入を検討
  - Radix UI はヘッドレス UI プリミティブとして使用

### 5.4 ステート管理（valtio）

- [ ] valtio のインストール (`pnpm add valtio`)
- [ ] **スコープ付きステート管理**の実装方針策定
  - **適用対象**: 共通コンポーネント、ドメイン固有コンポーネント
  - **パターン**: Context + valtio の組み合わせ
  - **利点**: コンポーネントツリー内でスコープに閉じた状態管理、テストが容易
  - **重要**: ストアファイル、Context ファイル、カスタムフックすべてに `'use client'` を付与
- [ ] **グローバルステート管理**の実装方針策定
  - **適用対象**: アプリケーション全体で共有する状態
  - **パターン**: valtio の `proxy()` をモジュールレベルでエクスポート
  - **利点**: シンプルで軽量、Provider 不要
  - **重要**: ストアファイルとカスタムフックに `'use client'` を付与
- [ ] ステート管理のデザインパターン選定
  - **推奨**: **Facade パターン** + **Custom Hooks パターン**
  - カスタムフック (`useXxxStore`) で状態の取得・更新ロジックをカプセル化
  - **必須**: カスタムフックに `'use client'` ディレクティブを付与（`useSnapshot` 使用のため）
  - コンポーネントは直接 store を触らず、hooks 経由でアクセス
- [ ] サンプル実装とベストプラクティスの策定

---

## Phase 6: スキーマ定義（Valibot）

### 6.1 Valibot セットアップ

- [ ] Valibot のインストール (`pnpm add valibot`)
- [ ] スキーマ定義の基本構造とパターンの決定
- [ ] 基本型スキーマの作成（`src/schemas/common/primitives.schema.ts`）
  - Color スキーマ（hex, rgb, rgba）
  - Duration スキーマ（秒、ミリ秒）
  - Position スキーマ（x, y）
  - Size スキーマ（width, height）

### 6.2 ドメインスキーマの実装

- [ ] Video プロジェクトスキーマ（`src/schemas/video/project.schema.ts`）

  ```typescript
  import * as v from "valibot";

  export const VideoProjectSchema = v.object({
    id: v.string(),
    name: v.string(),
    width: v.number(),
    height: v.number(),
    fps: v.number(),
    duration: v.number(),
    // ...
  });

  export type VideoProject = v.InferOutput<typeof VideoProjectSchema>;
  ```

- [ ] Subtitle スキーマ（`src/schemas/subtitle/subtitle.schema.ts`）
- [ ] Animation スキーマ（`src/schemas/animation/animation.schema.ts`）
- [ ] Timeline スキーマ（`src/schemas/video/timeline.schema.ts`）

### 6.3 バリデーションユーティリティ

- [ ] 汎用バリデーション関数の作成（`src/utils/validation/validate.ts`）

  ```typescript
  import * as v from "valibot";

  export function validate<T>(schema: v.BaseSchema, data: unknown): T {
    return v.parse(schema, data);
  }

  export function safeParse<T>(schema: v.BaseSchema, data: unknown) {
    return v.safeParse(schema, data);
  }
  ```

- [ ] パース関数の作成（`src/utils/validation/parse.ts`）
- [ ] 既存の JSON ファイル（examples/\*.json）との互換性確認
- [ ] カスタムバリデーションの実装（必要に応じて）

### 6.4 型推論とエクスポート

- [ ] Valibot スキーマから TypeScript 型の推論（`v.InferOutput<typeof Schema>`）
- [ ] 型とスキーマの両方をエクスポート
- [ ] スキーマバリデーションのテスト作成

---

## Phase 7: ドメインロジック

### 7.1 ビジネスロジックの抽出

- [ ] 既存の Python コア（teto_core）からの移植対象の特定
- [ ] ドメインモデルの TypeScript 実装
- [ ] 純粋関数としてのロジック実装（環境非依存）

### 7.2 環境依存機能の抽象化

- [ ] 永続化インターフェースの定義（ProjectSaver, ProjectLoader など）

  ```typescript
  // packages/lib/src/domain/interfaces/project-storage.ts
  export interface ProjectStorage {
    save(project: VideoProject): Promise<void>;
    load(id: string): Promise<VideoProject>;
  }
  ```

- [ ] 各 app での実装は含めない（apps/desktop, apps/web で実装）
- [ ] ドメインロジックはインターフェースに依存

### 7.3 グローバル状態管理（valtio）

- [ ] グローバル状態の設計
  - アプリケーション全体で共有する状態を定義
  - 例: ユーザー設定、テーマ、現在のプロジェクト情報など
- [ ] valtio を使ったグローバルストアの実装
  - **重要**: ストアファイル (`global-store.ts`) に `'use client'` ディレクティブを付与
  - モジュールレベルで `proxy()` をエクスポート
  - Provider 不要でシンプル
- [ ] カスタムフックでアクセスをカプセル化
  - **必須**: `useGlobalStore()` などのカスタムフックに `'use client'` ディレクティブを付与
  - `useSnapshot` を使用するため、`'use client'` が必須
  - Facade パターンで状態の取得・更新ロジックをカプセル化

---

## Phase 8: apps との統合

### 8.1 apps/desktop (Electron) との統合

#### 8.1.1 依存関係の設定

- [ ] apps/desktop の package.json に packages/lib を追加
  - pnpm ワークスペース参照（`"@teto/lib": "workspace:*"`）
  - `pnpm add @teto/lib --workspace` でインストール
- [ ] TypeScript パス解決の設定
- [ ] Vite での alias 設定

#### 8.1.2 Tailwind CSS の統合

- [ ] apps/desktop に Tailwind CSS をインストール (`pnpm add -D tailwindcss`)
- [ ] apps/desktop/src/styles/globals.css の作成

  ```css
  /* packages/lib の Tailwind CSS を継承 */
  @import "@teto/lib/styles/globals.css";

  /* アプリ固有のカスタマイズ（必要に応じて） */
  @theme {
    /* desktop 固有のテーマ設定 */
  }
  ```

- [ ] apps/desktop のエントリポイント（main.tsx など）で CSS をインポート
  ```typescript
  import './styles/globals.css';
  ```

#### 8.1.3 環境依存機能の実装

- [ ] Electron IPC 通信を使った ProjectStorage の実装

  ```typescript
  // apps/desktop/src/services/electron-project-storage.ts
  import { ProjectStorage } from "@teto/lib/domain/interfaces";

  export class ElectronProjectStorage implements ProjectStorage {
    async save(project: VideoProject) {
      await window.electronAPI.saveProject(project);
    }
    async load(id: string) {
      return await window.electronAPI.loadProject(id);
    }
  }
  ```

#### 8.1.4 ビルドとバンドル

- [ ] 開発モードでのホットリロード確認
- [ ] 本番ビルドでの動作確認
- [ ] Electron パッケージング時の動作確認

### 8.2 apps/web (Next.js) との統合

#### 8.2.1 依存関係の設定

- [ ] apps/web の package.json に packages/lib を追加
  - pnpm ワークスペース参照（`"@teto/lib": "workspace:*"`）
  - `pnpm add @teto/lib --workspace` でインストール
- [ ] next.config.js に transpilePackages を追加

  ```javascript
  module.exports = {
    transpilePackages: ["@teto/lib"],
  };
  ```

- [ ] TypeScript パス解決の設定

#### 8.2.2 Tailwind CSS の統合

- [ ] apps/web に Tailwind CSS をインストール (`pnpm add -D tailwindcss`)
- [ ] apps/web/src/app/globals.css の作成（Next.js App Router の場合）

  ```css
  /* packages/lib の Tailwind CSS を継承 */
  @import "@teto/lib/styles/globals.css";

  /* アプリ固有のカスタマイズ（必要に応じて） */
  @theme {
    /* web 固有のテーマ設定 */
  }
  ```

- [ ] app/layout.tsx で CSS をインポート
  ```typescript
  import './globals.css';
  ```

#### 8.2.3 環境依存機能の実装

- [ ] API 経由の ProjectStorage の実装

  ```typescript
  // apps/web/src/services/api-project-storage.ts
  import { ProjectStorage } from "@teto/lib/domain/interfaces";

  export class ApiProjectStorage implements ProjectStorage {
    async save(project: VideoProject) {
      await fetch("/api/projects", {
        method: "POST",
        body: JSON.stringify(project),
      });
    }
    async load(id: string) {
      const res = await fetch(`/api/projects/${id}`);
      return await res.json();
    }
  }
  ```

- [ ] Server Actions は使用せず、API Routes を使用

#### 8.2.4 ビルドとバンドル

- [ ] 開発モードでのホットリロード確認
- [ ] 本番ビルドでの動作確認
- [ ] 'use client' ディレクティブが正しく機能していることを確認

---

## Phase 9: ドキュメントとサンプル

### 9.1 README とドキュメント

- [ ] packages/lib/README.md の作成
  - インストール方法
  - 使用方法
  - コンポーネントカタログへのリンク
- [ ] 各主要コンポーネントの JSDoc コメント

### 9.2 サンプル実装

- [ ] apps/desktop でのサンプルページ作成
- [ ] 主要コンポーネントの使用例
- [ ] スキーマバリデーションの使用例

---

## Phase 10: CI/CD とメンテナンス

### 10.1 自動化

- [ ] GitHub Actions でのビルド確認
- [ ] リント・テストの自動実行
- [ ] 型チェックの自動実行

### 10.2 バージョン管理

- [ ] セマンティックバージョニング戦略
- [ ] CHANGELOG.md の運用方針
- [ ] packages/lib の更新フロー

---

## 補足: 技術スタック候補

### 必須

- React 18+
- TypeScript 5+
- Tailwind CSS 3+

### 推奨

- **ライブラリバンドラー**: tsdown（React + Tailwind CSS に最適化、超高速）
- **バリデーション**: Valibot（軽量で高速）
- **スタイリング**: class-variance-authority (cva), clsx, tailwind-merge
- **テスト**: Vitest + React Testing Library
- **リント**: ESLint + prettier-plugin-tailwindcss
- **開発環境**: Storybook
- **コンポーネント状態管理**: valtio（Provider パターンでスコープ付き状態管理）
- **グローバル状態管理**: valtio（モジュールレベル）

### オプション

- **フォーム**: React Hook Form + Valibot resolver (@modular-forms/react または自作）
- **アイコン**: lucide-react または heroicons
- **UI ベース**: Radix UI（ヘッドレス UI プリミティブ）

### tsdown の利点（ライブラリバンドラー）

- **超高速**: Rust 製（Rolldown + Oxc）で tsup の 10-30倍高速
- **React + Tailwind に最適**: 専用プラグインで簡単に統合
  - `@bosh-code/tsdown-plugin-tailwindcss`: Tailwind CSS のビルド
  - `@bosh-code/tsdown-plugin-inject-css`: CSS の自動インジェクト
- **シンプル**: ライブラリ開発に特化した sensible defaults
- **型定義自動生成**: .d.ts ファイルを高速生成
- **複数フォーマット**: ESM、CommonJS、IIFE、UMD に対応
- **プラグインエコシステム**: Rollup/Rolldown/unplugin プラグインをサポート

### Valibot の利点（バリデーション）

- **軽量**: Zod の約 10 分の 1 のバンドルサイズ（~600B vs ~14KB）
- **高速**: パフォーマンスが優れている
- **モジュラー**: Tree-shaking に最適化
- **型安全**: TypeScript との統合が優れている

### valtio の利点（統一的なステート管理）

- **シンプル**: プロキシベースで直感的な状態更新（`state.count++` のように書ける）
- **軽量**: 小さなバンドルサイズ（~3KB）
- **柔軟性**: スコープ付き（Provider）とグローバル（モジュールレベル）の両方に対応
  - **スコープ付き**: Provider パターンで複数インスタンスを作成可能（コンポーネント状態）
  - **グローバル**: モジュールレベルで export、Provider 不要（アプリケーション状態）
- **React 統合**: `useSnapshot` で自動的に最適化された再レンダリング
- **Next.js 対応**: `'use client'` と組み合わせて使用可能
- **学習コスト低**: Zustand や Jotai と比べてシンプルな API

### Next.js App Router と Electron の共通化のポイント

#### 'use client' ディレクティブ

- **Next.js**: Client Component として扱われ、クライアントサイドでのみ実行
- **Electron**: ディレクティブは無視され、通常の React コンポーネントとして動作
- **推奨**: イベントハンドラー、hooks、ブラウザAPI を使うコンポーネントには必ず付ける

#### 環境依存機能の分離

- **packages/lib**: 抽象インターフェースのみ定義
- **apps/desktop**: Electron IPC を使った実装
- **apps/web**: API Routes を使った実装
- **利点**: ビジネスロジックを環境に依存せず再利用可能

#### Tailwind CSS

- **Tailwind CSS v4 の CSS ベース設定を使用**
- packages/lib で `@theme` を使ってテーマを定義
- apps/desktop と apps/web は `@import` で lib の CSS を継承
- 各アプリで独自の `@theme` を追加してカスタマイズ可能

#### ビルド設定

- **packages/lib**: tsdown でライブラリをビルド（ESM フォーマット）
  - React と Tailwind CSS を含むコンポーネントライブラリ
  - 型定義ファイル (.d.ts) を自動生成
- **apps/desktop (Electron)**: Vite でアプリをビルド
  - packages/lib を ESM として import
- **apps/web (Next.js)**: Next.js ビルドシステム
  - `transpilePackages: ['@teto/lib']` で lib をトランスパイル
- **重要**: `package.json` の `exports` フィールドを正しく設定

### valtio でのステート管理デザインパターン

#### 推奨パターン: Facade パターン + Custom Hooks パターン

**Facade パターン**

- 複雑な状態管理ロジックをシンプルなインターフェースで隠蔽
- コンポーネントは内部実装を知る必要がない

**Custom Hooks パターン**

- `useXxxStore` のようなカスタムフックで状態へのアクセスを提供
- 状態の取得と更新のロジックをカプセル化
- テストが容易（hooks を個別にテスト可能）

**実装の構成**

1. **Store ファイル** (`xxx-store.ts`): `proxy()` で状態オブジェクトを作成
2. **Context ファイル** (`xxx-context.tsx`): React Context で store を提供
3. **Custom Hook ファイル** (`use-xxx.ts`):
   - `useSnapshot()` で状態を取得
   - 状態更新関数を提供（Facade）
   - コンポーネントはこの hook のみを使用

**利点**

- **カプセル化**: コンポーネントは store の内部構造を知らない
- **テスタビリティ**: hooks を独立してテスト可能
- **保守性**: 状態管理ロジックの変更がコンポーネントに影響しない
- **型安全**: TypeScript で完全に型付けされたインターフェース
- **再利用性**: 同じコンポーネントを複数インスタンス化可能（Provider でスコープ分離）

**状態の取得と更新の原則**

- **取得**: `useSnapshot(store)` で不変のスナップショットを取得（自動的に最適化された再レンダリング）
- **更新**: 直接 `store.xxx` を変更（プロキシが変更を検知）
- **派生状態**: カスタムフック内で計算して返す（コンポーネントをシンプルに保つ）

**例**

```typescript
// ❌ 悪い例: コンポーネントが store を直接操作
function MyComponent() {
  const store = useAccordionContext();
  const snap = useSnapshot(store);

  // コンポーネントがロジックを持つのは NG
  const toggle = (id: string) => {
    if (store.openItems.has(id)) {
      store.openItems.delete(id);
    } else {
      if (!store.allowMultiple) {
        store.openItems.clear();
      }
      store.openItems.add(id);
    }
  };

  return <button onClick={() => toggle('item-1')}>Toggle</button>;
}

// ✅ 良い例: カスタムフックでロジックをカプセル化
function MyComponent() {
  const { toggleItem, isOpen } = useAccordion(); // Facade

  return <button onClick={() => toggleItem('item-1')}>Toggle</button>;
}
```

#### スコープ付き vs グローバルの使い分け

**スコープ付きステート（Provider パターン）**

- **適用場面**: コンポーネント固有の状態、同じコンポーネントの複数インスタンスが必要
- **例**: Accordion の開閉状態、Dialog の表示状態、Form の入力値
- **特徴**:
  - Provider 内でのみ状態が共有される
  - 同じコンポーネントを複数配置しても状態が分離される
  - テストが容易（Provider に渡す store をモック可能）

```typescript
// 複数の Accordion インスタンスが独立して動作
<div>
  <Accordion>...</Accordion>  {/* 状態A */}
  <Accordion>...</Accordion>  {/* 状態B */}
</div>
```

**グローバルステート（モジュールレベル）**

- **適用場面**: アプリケーション全体で共有する状態
- **例**: 現在のプロジェクト、ユーザー設定、テーマ、認証状態
- **特徴**:
  - Provider 不要でシンプル
  - どのコンポーネントからもアクセス可能
  - アプリ全体で1つの状態を共有

```typescript
// どのコンポーネントからも同じ状態にアクセス
function Header() {
  const { theme } = useGlobalStore();
  return <div>Theme: {theme}</div>;
}

function Sidebar() {
  const { theme, toggleTheme } = useGlobalStore();
  return <button onClick={toggleTheme}>Toggle</button>;
}
```

**推奨事項**

- **デフォルトはスコープ付き**: テストしやすく、状態の影響範囲が明確
- **必要に応じてグローバル**: 本当にアプリ全体で共有が必要な状態のみ

---

## マイルストーン

1. **Week 1**: Phase 1-2（基盤とTailwind）
2. **Week 2**: Phase 3-4（構造と開発環境）
3. **Week 3**: Phase 5-6（UIとスキーマ）
4. **Week 4**: Phase 7（ドメインロジックとインターフェース抽象化）
5. **Week 5**: Phase 8（Electron と Next.js の両方での統合テスト）
6. **Week 6**: Phase 9-10（ドキュメントとCI/CD）

---

## 次のステップ

このタスクリストを基に、以下の順序で進めることを推奨：

1. **Phase 1-2** を完了させ、最小限の環境を構築
   - tsdown のセットアップ
   - Tailwind CSS プラグインの設定
2. **Phase 5** で Button など1つの基本コンポーネントを実装
   - `'use client'` ディレクティブの動作確認
   - tsdown でビルドして dist/ に出力されることを確認
3. **Phase 8.1** で Electron アプリでの動作確認
   - packages/lib を import して CSS が適用されることを確認
4. **Phase 8.2** で Next.js アプリでの動作確認
   - 両方で同じコンポーネントが動作することを確認
5. その後、各 Phase を順次進める

### 重要な確認ポイント

- [ ] tsdown で正しくビルドできるか（`pnpm build` が成功）
- [ ] 全てのインタラクティブコンポーネントに `'use client'` が付いているか
- [ ] **valtio 関連のすべてのファイルに `'use client'` が付いているか**
  - ストアファイル (`xxx-store.ts`, `global-store.ts`)
  - Context ファイル (`xxx-context.tsx`)
  - カスタムフック (`use-xxx.ts`, `use-global-store.ts`)
- [ ] 環境依存の機能が抽象インターフェースとして定義されているか
- [ ] Electron と Next.js の両方でビルドが成功するか
- [ ] Tailwind CSS が両方の環境で正しく動作するか
- [ ] CSS が自動的にインジェクトされているか（`@bosh-code/tsdown-plugin-inject-css` の動作確認）
- [ ] `sideEffects: false` の設定で CSS が正しくバンドルされているか

必要に応じてタスクを追加・削除・変更してください。

---

## 使用例イメージ

### apps/desktop (Electron) での利用例

```typescript
// apps/desktop/src/app.tsx
import { Button } from '@teto/lib/components/ui';
import { VideoProjectSchema } from '@teto/lib/schemas';
import { createProject } from '@teto/lib/domain/video';
import { useProject } from '@teto/lib/hooks';
import { ElectronProjectStorage } from './services/electron-project-storage';
import '@teto/lib/styles';

const storage = new ElectronProjectStorage();

function App() {
  const { project, updateProject } = useProject();

  const handleCreateProject = async () => {
    const newProject = createProject({
      name: 'New Project',
      width: 1920,
      height: 1080,
      fps: 60,
    });

    // Valibot でバリデーション
    const validated = v.parse(VideoProjectSchema, newProject);

    // Electron IPC 経由で保存
    await storage.save(validated);
    updateProject(validated);
  };

  return (
    <div className="p-4">
      <Button
        variant="primary"
        size="lg"
        onClick={handleCreateProject}
      >
        Create Project
      </Button>
    </div>
  );
}
```

### apps/web (Next.js) での利用例

```typescript
// apps/web/src/app/page.tsx
'use client';  // Next.js App Router でクライアントコンポーネントとして明示

import { Button } from '@teto/lib/components/ui';
import { VideoProjectSchema } from '@teto/lib/schemas';
import { createProject } from '@teto/lib/domain/video';
import { useProject } from '@teto/lib/hooks';
import { ApiProjectStorage } from '@/services/api-project-storage';
import '@teto/lib/styles';

const storage = new ApiProjectStorage();

export default function HomePage() {
  const { project, updateProject } = useProject();

  const handleCreateProject = async () => {
    const newProject = createProject({
      name: 'New Project',
      width: 1920,
      height: 1080,
      fps: 60,
    });

    // Valibot でバリデーション
    const validated = v.parse(VideoProjectSchema, newProject);

    // API Routes 経由で保存
    await storage.save(validated);
    updateProject(validated);
  };

  return (
    <div className="p-4">
      <Button
        variant="primary"
        size="lg"
        onClick={handleCreateProject}
      >
        Create Project
      </Button>
    </div>
  );
}
```

### 環境依存機能の実装例

```typescript
// packages/lib/src/domain/interfaces/project-storage.ts
export interface ProjectStorage {
  save(project: VideoProject): Promise<void>;
  load(id: string): Promise<VideoProject>;
  list(): Promise<VideoProject[]>;
}

// apps/desktop/src/services/electron-project-storage.ts
import { ProjectStorage } from "@teto/lib/domain/interfaces";
import { VideoProject } from "@teto/lib/schemas";

export class ElectronProjectStorage implements ProjectStorage {
  async save(project: VideoProject): Promise<void> {
    await window.electronAPI.saveProject(project);
  }

  async load(id: string): Promise<VideoProject> {
    return await window.electronAPI.loadProject(id);
  }

  async list(): Promise<VideoProject[]> {
    return await window.electronAPI.listProjects();
  }
}

// apps/web/src/services/api-project-storage.ts
import { ProjectStorage } from "@teto/lib/domain/interfaces";
import { VideoProject } from "@teto/lib/schemas";

export class ApiProjectStorage implements ProjectStorage {
  async save(project: VideoProject): Promise<void> {
    await fetch("/api/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(project),
    });
  }

  async load(id: string): Promise<VideoProject> {
    const res = await fetch(`/api/projects/${id}`);
    return await res.json();
  }

  async list(): Promise<VideoProject[]> {
    const res = await fetch("/api/projects");
    return await res.json();
  }
}
```

### コンポーネントの実装例

#### シンプルなコンポーネント（Button）

```typescript
// packages/lib/src/components/ui/button/button.tsx
'use client';  // Next.js 用、Electron では無視される

import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/utils/cn';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md font-medium transition-colors',
  {
    variants: {
      variant: {
        primary: 'bg-blue-600 text-white hover:bg-blue-700',
        secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
        outline: 'border border-gray-300 bg-transparent hover:bg-gray-100',
      },
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-base',
        lg: 'h-12 px-6 text-lg',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
}

export function Button({
  className,
  variant,
  size,
  loading,
  children,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? 'Loading...' : children}
    </button>
  );
}
```

#### Compound Component + valtio の実装例（Accordion）

```typescript
// packages/lib/src/components/ui/accordion/accordion-store.ts
'use client';

import { proxy } from 'valtio';

export interface AccordionState {
  openItems: Set<string>;
  allowMultiple: boolean;
}

export function createAccordionStore(allowMultiple = false): AccordionState {
  return proxy<AccordionState>({
    openItems: new Set(),
    allowMultiple,
  });
}

// packages/lib/src/components/ui/accordion/accordion-context.tsx
'use client';

import { createContext, useContext } from 'react';
import type { AccordionState } from './accordion-store';

const AccordionContext = createContext<AccordionState | null>(null);

export function useAccordionContext() {
  const context = useContext(AccordionContext);
  if (!context) {
    throw new Error('Accordion components must be used within <Accordion>');
  }
  return context;
}

export const AccordionProvider = AccordionContext.Provider;

// packages/lib/src/components/ui/accordion/use-accordion.ts
'use client';

import { useSnapshot } from 'valtio';
import { useAccordionContext } from './accordion-context';

/**
 * Facade パターン + Custom Hooks パターン
 * コンポーネントから状態の取得・更新ロジックをカプセル化
 */
export function useAccordion() {
  const store = useAccordionContext();
  const snap = useSnapshot(store);

  const toggleItem = (id: string) => {
    if (store.openItems.has(id)) {
      store.openItems.delete(id);
    } else {
      if (!store.allowMultiple) {
        store.openItems.clear();
      }
      store.openItems.add(id);
    }
  };

  const isOpen = (id: string) => snap.openItems.has(id);

  return {
    openItems: snap.openItems,
    allowMultiple: snap.allowMultiple,
    toggleItem,
    isOpen,
  };
}

// packages/lib/src/components/ui/accordion/accordion.tsx
'use client';

import { createAccordionStore } from './accordion-store';
import { AccordionProvider } from './accordion-context';
import { AccordionItem } from './accordion-item';
import { AccordionTrigger } from './accordion-trigger';
import { AccordionContent } from './accordion-content';

export interface AccordionProps {
  children: React.ReactNode;
  allowMultiple?: boolean;
  className?: string;
}

function AccordionRoot({ children, allowMultiple = false, className }: AccordionProps) {
  const store = createAccordionStore(allowMultiple);

  return (
    <AccordionProvider value={store}>
      <div className={className}>{children}</div>
    </AccordionProvider>
  );
}

// Compound Component パターン: サブコンポーネントを親に付与
export const Accordion = Object.assign(AccordionRoot, {
  Item: AccordionItem,
  Trigger: AccordionTrigger,
  Content: AccordionContent,
});

// packages/lib/src/components/ui/accordion/accordion-item.tsx
'use client';

import { createContext, useContext } from 'react';

const AccordionItemContext = createContext<string>('');

export function useAccordionItemContext() {
  return useContext(AccordionItemContext);
}

export interface AccordionItemProps {
  children: React.ReactNode;
  value: string;
  className?: string;
}

export function AccordionItem({ children, value, className }: AccordionItemProps) {
  return (
    <AccordionItemContext.Provider value={value}>
      <div className={className}>{children}</div>
    </AccordionItemContext.Provider>
  );
}

// packages/lib/src/components/ui/accordion/accordion-trigger.tsx
'use client';

import { useAccordion } from './use-accordion';
import { useAccordionItemContext } from './accordion-item';

export interface AccordionTriggerProps {
  children: React.ReactNode;
  className?: string;
}

export function AccordionTrigger({ children, className }: AccordionTriggerProps) {
  const { toggleItem, isOpen } = useAccordion();
  const itemId = useAccordionItemContext();

  return (
    <button
      onClick={() => toggleItem(itemId)}
      className={className}
      aria-expanded={isOpen(itemId)}
    >
      {children}
    </button>
  );
}

// packages/lib/src/components/ui/accordion/accordion-content.tsx
'use client';

import { useAccordion } from './use-accordion';
import { useAccordionItemContext } from './accordion-item';

export interface AccordionContentProps {
  children: React.ReactNode;
  className?: string;
}

export function AccordionContent({ children, className }: AccordionContentProps) {
  const { isOpen } = useAccordion();
  const itemId = useAccordionItemContext();

  if (!isOpen(itemId)) return null;

  return <div className={className}>{children}</div>;
}

// packages/lib/src/components/ui/accordion/index.ts
export { Accordion } from './accordion';
export type { AccordionProps } from './accordion';
```

#### Compound Component の使用例

```typescript
// apps/desktop/src/app.tsx または apps/web/src/app/page.tsx
'use client';

import { Accordion } from '@teto/lib/components/ui';

function MyComponent() {
  return (
    <Accordion allowMultiple={false} className="w-full">
      <Accordion.Item value="item-1" className="border-b">
        <Accordion.Trigger className="flex w-full items-center justify-between py-4">
          What is Teto?
        </Accordion.Trigger>
        <Accordion.Content className="pb-4">
          Teto is a video editing tool...
        </Accordion.Content>
      </Accordion.Item>

      <Accordion.Item value="item-2" className="border-b">
        <Accordion.Trigger className="flex w-full items-center justify-between py-4">
          How does it work?
        </Accordion.Trigger>
        <Accordion.Content className="pb-4">
          Teto uses React and Electron...
        </Accordion.Content>
      </Accordion.Item>
    </Accordion>
  );
}
```

#### グローバルステート管理の実装例（valtio）

```typescript
// packages/lib/src/stores/global-store.ts
"use client";

import { proxy } from "valtio";
import type { VideoProject } from "../schemas";

export interface GlobalState {
  currentProject: VideoProject | null;
  theme: "light" | "dark";
  sidebarOpen: boolean;
}

// モジュールレベルで proxy をエクスポート（Provider 不要）
export const globalStore = proxy<GlobalState>({
  currentProject: null,
  theme: "light",
  sidebarOpen: true,
});

// packages/lib/src/stores/use-global-store.ts
'use client';

import { useSnapshot } from "valtio";
import { globalStore } from "./global-store";
import type { VideoProject } from "../schemas";

/**
 * グローバルストアへのアクセスを提供する Facade
 */
export function useGlobalStore() {
  const snap = useSnapshot(globalStore);

  const setCurrentProject = (project: VideoProject | null) => {
    globalStore.currentProject = project;
  };

  const toggleTheme = () => {
    globalStore.theme = globalStore.theme === "light" ? "dark" : "light";
  };

  const toggleSidebar = () => {
    globalStore.sidebarOpen = !globalStore.sidebarOpen;
  };

  return {
    // 状態の取得
    currentProject: snap.currentProject,
    theme: snap.theme,
    sidebarOpen: snap.sidebarOpen,

    // 状態の更新
    setCurrentProject,
    toggleTheme,
    toggleSidebar,
  };
}

// packages/lib/src/stores/index.ts
export { globalStore } from "./global-store";
export { useGlobalStore } from "./use-global-store";
export type { GlobalState } from "./global-store";
```

#### グローバルステートの使用例

```typescript
// apps/desktop/src/components/header.tsx または apps/web/src/components/header.tsx
'use client';

import { useGlobalStore } from '@teto/lib/stores';
import { Button } from '@teto/lib/components/ui';

export function Header() {
  const { theme, sidebarOpen, toggleTheme, toggleSidebar } = useGlobalStore();

  return (
    <header className="flex items-center justify-between p-4">
      <Button onClick={toggleSidebar}>
        {sidebarOpen ? 'Close Sidebar' : 'Open Sidebar'}
      </Button>

      <Button onClick={toggleTheme}>
        Current Theme: {theme}
      </Button>
    </header>
  );
}

// apps/desktop/src/components/project-info.tsx
'use client';

import { useGlobalStore } from '@teto/lib/stores';

export function ProjectInfo() {
  const { currentProject, setCurrentProject } = useGlobalStore();

  if (!currentProject) {
    return <div>No project loaded</div>;
  }

  return (
    <div>
      <h2>{currentProject.name}</h2>
      <p>{currentProject.width} x {currentProject.height}</p>
      <button onClick={() => setCurrentProject(null)}>Close Project</button>
    </div>
  );
}
```

### package.json の設定例

```json
{
  "name": "@teto/lib",
  "version": "0.1.0",
  "type": "module",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js"
    },
    "./components/ui": {
      "types": "./dist/components/ui/index.d.ts",
      "import": "./dist/components/ui/index.js"
    },
    "./schemas": {
      "types": "./dist/schemas/index.d.ts",
      "import": "./dist/schemas/index.js"
    },
    "./domain": {
      "types": "./dist/domain/index.d.ts",
      "import": "./dist/domain/index.js"
    },
    "./hooks": {
      "types": "./dist/hooks/index.d.ts",
      "import": "./dist/hooks/index.js"
    },
    "./utils": {
      "types": "./dist/utils/index.d.ts",
      "import": "./dist/utils/index.js"
    }
  },
  "files": ["dist"],
  "sideEffects": false,
  "scripts": {
    "dev": "tsdown --watch",
    "build": "tsdown",
    "test": "vitest",
    "lint": "eslint . --ext .ts,.tsx",
    "format": "prettier --write \"src/**/*.{ts,tsx}\"",
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build"
  },
  "dependencies": {
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "valibot": "^0.30.0",
    "valtio": "^1.13.0"
  },
  "devDependencies": {
    "@bosh-code/tsdown-plugin-inject-css": "^0.1.0",
    "@bosh-code/tsdown-plugin-tailwindcss": "^0.1.0",
    "@storybook/react": "^7.6.0",
    "@storybook/react-vite": "^7.6.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "tailwindcss": "^3.4.0",
    "tsdown": "^0.2.0",
    "typescript": "^5.3.0",
    "vitest": "^1.0.0"
  },
  "peerDependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  }
}
```
