# [対象モジュール]のリファクタリング - [パターン名]への変更

## 概要
[リファクタリングの概要と目的を簡潔に説明]

## 現在の問題点

**場所**: `[ファイルパス:行番号]`

```python
# 現在の問題のあるコード例
def problematic_function():
    if condition1:
        # ...
    elif condition2:
        # ...
    # ... 長い条件分岐
```

### 問題
- [問題点1]
- [問題点2]
- [問題点3]
- [違反している原則（例: Open/Closed Principle）]

---

## 目標設計

### [採用するパターン名]による実装

```python
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """基底クラスの説明"""

    @abstractmethod
    def execute(self, data) -> Result:
        """メソッドの説明"""
        pass


class ConcreteStrategyA(BaseStrategy):
    """具体的な戦略Aの説明"""

    def execute(self, data) -> Result:
        # 実装
        pass


class RefactoredProcessor:
    """リファクタリング後のプロセッサー"""

    _strategies: dict[str, BaseStrategy] = {
        "strategy_a": ConcreteStrategyA(),
        "strategy_b": ConcreteStrategyB(),
    }

    @classmethod
    def register_strategy(cls, name: str, strategy: BaseStrategy) -> None:
        """カスタム戦略を登録"""
        cls._strategies[name] = strategy

    def process(self, data, strategy_name: str):
        strategy = self._strategies.get(strategy_name)
        if strategy:
            return strategy.execute(data)
        raise ValueError(f"Unknown strategy: {strategy_name}")
```

---

## タスク詳細

### Phase 1: 基盤の作成
- [ ] `[ディレクトリ名]/` ディレクトリを作成
- [ ] `[ディレクトリ名]/base.py` に基底クラスを作成
- [ ] `[ディレクトリ名]/__init__.py` でエクスポート設定

### Phase 2: 個別クラスの実装
各処理を個別のファイルに分割:

- [ ] `[ディレクトリ名]/[ファイル1].py` - `[クラス1]`, `[クラス2]`
- [ ] `[ディレクトリ名]/[ファイル2].py` - `[クラス3]`, `[クラス4]`

### Phase 3: プロセッサーのリファクタリング
- [ ] `[プロセッサー名]` を新しい設計に変更
- [ ] レジストリの実装
- [ ] 登録メソッドの追加
- [ ] 既存の static メソッドを削除

### Phase 4: ユーティリティの共通化
- [ ] `[ディレクトリ名]/utils.py` を作成
- [ ] 共通処理を抽出

### Phase 5: テストとドキュメント
- [ ] 各クラスの単体テストを作成
- [ ] カスタム拡張の追加方法をドキュメント化
- [ ] 既存のテストが引き続き動作することを確認

---

## 期待される効果

### メリット
1. **拡張性向上**: [説明]
2. **テスタビリティ向上**: [説明]
3. **可読性向上**: [説明]
4. **プラグインサポート**: [説明]
5. **責任の分離**: [説明]

### デメリット
1. [デメリット1]
2. [デメリット2]

---

## 検討事項
- [検討事項1]
- [検討事項2]
- [検討事項3]

---

## 参考
- [参考パターン/実装]: [説明や場所]
- [パターン比較]: [他のパターンとの比較と選定理由]

---

> **Note**: すべてのタスクが完了したら、このファイルを `tasks/completed/` ディレクトリに移動してください。
