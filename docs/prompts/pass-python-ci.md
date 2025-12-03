# Python CI を全通させる

## 概要
Python CI のすべてのチェック（lint, format, test）を通過させる。

## CI チェック内容
以下の 3 つのチェックを順番に通過させる：

1. **Ruff (Lint)**: `uv run ruff check packages/`
2. **Black (Format)**: `uv run black --check packages/`
3. **Pytest (Test)**: `uv run pytest packages/core/tests/ -v`

---

## タスク手順

### 1. Lint エラーの修正
```bash
# エラー確認
uv run ruff check packages/

# 自動修正を試す
uv run ruff check packages/ --fix

# 修正後に再確認
uv run ruff check packages/
```

### 2. Format エラーの修正
```bash
# エラー確認
uv run black --check packages/

# 自動フォーマット
uv run black packages/

# 修正後に再確認
uv run black --check packages/
```

### 3. テストの実行
```bash
# テスト実行
uv run pytest packages/core/tests/ -v

# 失敗したテストがあれば原因を調査し修正
```

---

## 確認事項
- [ ] `uv run ruff check packages/` が成功すること
- [ ] `uv run black --check packages/` が成功すること
- [ ] `uv run pytest packages/core/tests/ -v` が成功すること
- [ ] すべての変更が意図した修正であること
