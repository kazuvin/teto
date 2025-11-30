# Teto Core リファクタリングタスク

このディレクトリには、`teto_core` パッケージのリファクタリングタスクが含まれています。

## タスク一覧

### 優先度: 高

1. **[AnimationProcessor のリファクタリング](./refactor-animation-processor.md)**
   - 巨大な if-elif チェーンを Strategy/Command パターンに置き換え
   - 各エフェクトを独立したクラスとして実装
   - 拡張性とテスタビリティの向上

2. **[VideoGenerator のリファクタリング](./refactor-video-generator-pipeline.md)**
   - 100行の `generate()` メソッドを Pipeline パターンに分割
   - 各処理ステップを独立したクラスとして実装
   - カスタムパイプラインのサポート

### 優先度: 中

3. **[ProcessorBase の統合](./refactor-processor-base-integration.md)**
   - 未使用の `ProcessorBase` を活用
   - Template Method パターンの適用
   - Static メソッド中心の設計からオブジェクト指向設計への移行

### 優先度: 低（追加機能）

4. **[Builder パターンの導入](./add-builder-pattern.md)**
   - プロジェクト構築を簡略化する Builder パターンの実装
   - Fluent Interface による直感的な API
   - 初心者フレンドリーな設計

## タスクの依存関係

```
refactor-animation-processor (独立)
    ↓
refactor-processor-base-integration (AnimationProcessor の完了後に実施推奨)
    ↓
refactor-video-generator-pipeline (Processor の統合後に実施推奨)

add-builder-pattern (独立、いつでも実施可能)
```

## 推奨実施順序

1. **Phase 1**: AnimationProcessor のリファクタリング
   - 比較的独立しており、影響範囲が限定的
   - Strategy パターンの良い実践例となる

2. **Phase 2**: ProcessorBase の統合
   - AnimationProcessor で得た知見を活かせる
   - 全体的な設計の一貫性が向上

3. **Phase 3**: VideoGenerator のリファクタリング
   - Processor の設計が安定した後に実施
   - 大きな変更なので、他のリファクタリングが完了してから

4. **Phase 4** (オプション): Builder パターンの導入
   - ユーザー向けの API 改善
   - 内部設計が安定した後に実施

## 各タスクの影響範囲

| タスク | 影響範囲 | 破壊的変更 | 後方互換性 |
|--------|---------|-----------|-----------|
| AnimationProcessor | `processors/animation.py` のみ | なし | 完全互換 |
| ProcessorBase 統合 | 全 Processor | あり（内部） | 互換性レイヤーで対応 |
| VideoGenerator | `generator.py` とパイプライン | なし | 完全互換 |
| Builder パターン | 新規追加のみ | なし | 追加機能 |

## テスト戦略

各リファクタリングには以下のテストが必要:

1. **単体テスト**: 新しいクラス/メソッドのテスト
2. **統合テスト**: 既存機能との統合テスト
3. **回帰テスト**: 既存のテストがすべてパスすることを確認
4. **性能テスト**: リファクタリング前後の性能比較

## ドキュメント更新

各タスク完了後に更新が必要なドキュメント:

- API リファレンス
- 使用例とサンプルコード
- アーキテクチャドキュメント
- マイグレーションガイド（破壊的変更がある場合）

## 注意事項

- すべてのリファクタリングで既存の API との後方互換性を維持すること
- 段階的な移行パスを提供すること（deprecation warning など）
- 各フェーズでテストがパスすることを確認すること
- 大きな変更は feature ブランチで行い、レビューを経てマージすること

## 参考リソース

- [デザインパターン分析レポート](../../analysis/design-patterns.md)
- [GoF デザインパターン](https://en.wikipedia.org/wiki/Design_Patterns)
- [Martin Fowler - Refactoring](https://refactoring.com/)
- [Python デザインパターン](https://github.com/faif/python-patterns)
