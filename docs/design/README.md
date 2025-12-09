# Teto 設計ドキュメント

このディレクトリには、Teto プロジェクトの設計に関する詳細なドキュメントが含まれています。

---

## ドキュメント一覧

### 1. [プロジェクト全体概要](00_overview.md)

**内容**:

- プロジェクト概要と主な特徴
- プロジェクト構造
- アーキテクチャの階層（Script、Project、Generator）
- データフロー
- 主要コンポーネント
- 設計パターン
- 拡張ポイント
- 技術スタック

**対象読者**: 初めて Teto に触れる開発者、アーキテクチャの全体像を把握したい方

---

### 2. [データモデル詳細](01_data_models.md)

**内容**:

- Script モデル（高レベル API）
  - Script、Scene、NarrationSegment、Visual、VoiceConfig など
- Project モデル（実行モデル）
  - Project、Timeline
- Layer モデル
  - VideoLayer、ImageLayer、AudioLayer、SubtitleLayer、StampLayer
- Effect モデル
  - AnimationEffect、TransitionConfig
- Output Configuration
  - OutputSettings、OutputConfig、AspectRatio など

**対象読者**: データ構造を理解したい開発者、JSON スクリプトを作成する方

---

### 3. [Script → Project コンパイルパイプライン](02_compilation_pipeline.md)

**内容**:

- コンパイルの概要と目的
- ScriptCompiler アーキテクチャ
- コンパイルステップ詳細
  1. 準備
  2. TTS 生成
  3. タイミング計算
  4. レイヤー構築
  5. Project 組み立て
  6. メタデータ作成
- 音声設定の解決（シーン毎の音声変更）
- タイミング計算の詳細
- プリセットシステム
- エラーハンドリング
- パフォーマンス最適化

**対象読者**: コンパイルプロセスを理解したい開発者、カスタムコンパイラーを実装したい方

---

### 4. [Project → Video 生成パイプライン](03_generation_pipeline.md)

**内容**:

- 生成の概要と目的
- VideoGenerator アーキテクチャ
- 処理パイプライン
  1. VideoLayerProcessingStep
  2. AudioLayerProcessingStep
  3. AudioMergingStep
  4. StampLayerProcessingStep
  5. SubtitleProcessingStep
  6. VideoOutputStep
  7. CleanupStep
- レイヤープロセッサー
  - VideoLayerProcessor（Object Fit）
  - AudioLayerProcessor
  - SubtitleProcessor（焼き込み、SRT/VTT）
- エフェクトシステム
- マルチ出力生成
- 拡張ポイント（カスタムパイプライン、Pre/Post Hooks）
- パフォーマンス最適化

**対象読者**: 動画生成プロセスを理解したい開発者、カスタムエフェクトやパイプラインを実装したい方

---

### 5. [TTS システムとキャッシング戦略](04_tts_and_caching.md)

**内容**:

- TTS システム概要
- TTS プロバイダー
  - Google Cloud TTS
  - ElevenLabs TTS
  - Gemini TTS
- TTSProvider インターフェース
- キャッシュシステム
  - TTSCacheManager
  - キャッシュキー生成
  - キャッシュディレクトリ構造
- 音声設定の解決（優先順位）
- パフォーマンス最適化
  - キャッシュヒット率の向上
  - キャッシュ統計
- トラブルシューティング

**対象読者**: TTS システムを理解したい開発者、新しい TTS プロバイダーを追加したい方

---

## 推奨読書順序

### 初めての方

1. [プロジェクト全体概要](00_overview.md) - 全体像を把握
2. [データモデル詳細](01_data_models.md) - Script と Project の構造を理解
3. [シーン毎の音声変更機能](05_per_scene_voice_feature.md) - 実践的な機能を学ぶ

### 開発者向け

1. [プロジェクト全体概要](00_overview.md) - アーキテクチャを理解
2. [データモデル詳細](01_data_models.md) - データ構造を把握
3. [Script → Project コンパイルパイプライン](02_compilation_pipeline.md) - コンパイルプロセスを学ぶ
4. [Project → Video 生成パイプライン](03_generation_pipeline.md) - 生成プロセスを学ぶ
5. [TTS システムとキャッシング戦略](04_tts_and_caching.md) - TTS とキャッシュを理解

### 拡張を検討している方

1. [プロジェクト全体概要](00_overview.md) - 拡張ポイントを確認
2. [Project → Video 生成パイプライン](03_generation_pipeline.md) - カスタムパイプライン、エフェクト
3. [TTS システムとキャッシング戦略](04_tts_and_caching.md) - カスタム TTS プロバイダー
4. [Script → Project コンパイルパイプライン](02_compilation_pipeline.md) - カスタムプリセット、コンパイラー

---

## ドキュメントの使い方

### サンプルコードの参照

各ドキュメントには実装例やサンプルコードが含まれています。実際のコードは以下の場所にあります：

```
packages/core/teto_core/
├── script/              # Script モデル、コンパイラー
├── project/             # Project モデル
├── layer/               # Layer モデル、プロセッサー
├── effect/              # エフェクトシステム
├── tts/                 # TTS クライアント
├── generator/           # 動画生成パイプライン
├── cache/               # キャッシュシステム
└── video_generator.py   # VideoGenerator

examples/scripts/        # サンプルスクリプト
```

### サンプルスクリプト

実際の使用例を見たい場合は、`examples/scripts/` ディレクトリにあるサンプルスクリプトを参照してください：

- `13_script_multi_platform.json` - マルチプラットフォーム出力
- `14_script_dialogue_direct_voice.json` - 直接 voice 指定
- `15_script_dialogue_voice_profiles.json` - 名前付きプロファイル

---

## 貢献ガイドライン

### ドキュメントの更新

新機能を追加した場合や既存の機能を変更した場合は、関連するドキュメントを更新してください：

1. **新機能の場合**:

   - 該当するドキュメントに新しいセクションを追加
   - 必要に応じて新しいドキュメントを作成
   - この README を更新

2. **既存機能の変更の場合**:

   - 影響を受けるドキュメントを更新
   - サンプルコードも更新

3. **ドキュメントのスタイル**:
   - Markdown 形式
   - 見出しは階層的に（h1 → h2 → h3）
   - コードブロックには言語を指定（\`\`\`python, \`\`\`json）
   - 図やテーブルを活用
   - 具体例を豊富に含める

### レビュープロセス

- ドキュメントの変更も PR でレビュー
- 技術的な正確性を確認
- 読みやすさ、わかりやすさをチェック

---

## フィードバック

ドキュメントに関するフィードバックや改善提案は、以下の方法でお寄せください：

- GitHub Issues: バグや誤記の報告
- Pull Requests: 直接修正や追加
- Discussions: 質問や議論

---

## ライセンス

このドキュメントは Teto プロジェクトの一部であり、プロジェクトと同じライセンスが適用されます。

---

## 更新履歴

- **2025-12-09**: 初版作成
  - プロジェクト全体概要
  - データモデル詳細
  - コンパイルパイプライン
  - 生成パイプライン
  - TTS とキャッシング
  - シーン毎の音声変更機能

---

このドキュメントセットが、Teto プロジェクトの理解と開発に役立つことを願っています！
