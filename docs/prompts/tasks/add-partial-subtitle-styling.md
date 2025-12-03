# 字幕の部分スタイル変更機能の追加

## 概要

字幕テキスト内で部分的にスタイルを変更できる機能を追加する。XMLライクなマークアップ（例: `<A>こんにちは</A><B>世界</B>`）を使用して、同一字幕内でフォント色・太さなどを切り替える。

## 背景と目的

### ユースケース

1. **強調表示**: 重要なキーワードを赤字・太字で強調（例: `<emphasis>重要:</emphasis> これは説明です`）
2. **話者区別**: 複数話者の会話を色で区別（例: `<speaker1>田中:</speaker1> <speaker2>こんにちは</speaker2>`）
3. **ハイライト**: 特定の単語を目立たせる（例: `新機能 <highlight>AI字幕</highlight> を紹介`）

### なぜこのアプローチを選んだか

**選定理由**:

1. **XMLマークアップ方式**: 可読性が高く、AI生成との親和性が良い
2. **スタイル定義の分離**: レイヤーレベルでスタイルを定義し、テキスト内で参照することで再利用性を確保
3. **後方互換性**: マークアップがない場合は従来通りの動作を維持

**比較検討した代替案**:

| 方式 | メリット | デメリット |
|------|----------|------------|
| スパン配列方式 | パース不要 | 記述が冗長、AI生成時に複雑 |
| インラインスタイル方式 | 直感的 | 再利用性がない、バリデーション複雑 |
| **XMLマークアップ方式（採用）** | 可読性・再利用性・AI親和性 | XMLパーサーが必要 |

### 要件

- 字幕テキスト内でXMLライクなマークアップを使用してスタイルを切り替える
- スタイルはレイヤーレベルで定義し、マークアップタグ名で参照する
- マークアップがない場合は従来通りレイヤー全体のスタイルを適用（後方互換性）
- 音声生成時はマークアップを除去した素のテキストを使用する
- スタイルは `font_color`, `font_weight` を部分適用可能とする（縁取りはレイヤー全体で統一）

## 前提条件

- 現在の字幕レンダリングは PILの `draw.multiline_text()` で一括描画している
- SubtitleLayer モデルに `styles` フィールドを追加する
- 音声生成は別のパイプラインで処理される

---

## アーキテクチャとデザインパターン

### 採用するデザインパターン

#### 1. パーサーパターン（マークアップ解析）

XMLライクなマークアップをパースしてスパンのリストに変換する。

```python
from dataclasses import dataclass

@dataclass
class TextSpan:
    """テキストスパン（スタイル適用単位）"""
    text: str
    style_name: str | None = None  # None の場合はデフォルトスタイル


def parse_styled_text(text: str) -> list[TextSpan]:
    """マークアップテキストをスパンのリストに変換"""
    # <A>text</A> 形式をパース
    # マークアップがない場合は単一スパンを返す
    pass


def strip_markup(text: str) -> str:
    """マークアップを除去して素のテキストを返す（音声生成用）"""
    pass
```

#### 2. スタイルマージパターン（スタイル解決）

スパンのスタイル名からレイヤーの `styles` 定義を参照し、デフォルトスタイルとマージする。

```python
def resolve_span_style(
    span: TextSpan,
    styles: dict[str, PartialStyle],
    default_style: PartialStyle
) -> ResolvedStyle:
    """スパンのスタイルを解決する"""
    if span.style_name and span.style_name in styles:
        return default_style.merge(styles[span.style_name])
    return default_style
```

### 設計の単純化

- **縁取りは部分適用しない**: 縁取りを部分適用すると描画が複雑になるため、レイヤー全体で統一
- **入れ子マークアップは非対応**: `<A><B>text</B></A>` のような入れ子は初期実装では非対応
- **折り返しはスパン単位で処理**: 既存の日本語折り返しロジックを活用

---

## ディレクトリ構造

```
packages/core/teto_core/
├── layer/
│   └── models.py              # SubtitleLayer に styles フィールド追加
│
├── utils/
│   ├── markup_utils.py        # 新規: マークアップパーサー
│   └── image_utils.py         # 変更: スパンごとの描画対応
│
└── tests/
    └── utils/
        └── test_markup_utils.py  # 新規: パーサーのテスト
```

---

## データモデル定義

### models.py の変更

```python
from pydantic import BaseModel, Field
from typing import Literal, Union

class PartialStyle(BaseModel):
    """部分スタイル定義（マークアップで適用）"""

    font_color: str | None = Field(None, description="フォントカラー")
    font_weight: Literal["normal", "bold"] | None = Field(
        None, description="フォントの太さ"
    )


class SubtitleLayer(BaseModel):
    """字幕レイヤー（既存フィールドに styles を追加）"""

    # ... 既存フィールド ...

    # 新規: 部分スタイル定義
    styles: dict[str, PartialStyle] = Field(
        default_factory=dict,
        description="マークアップタグ名とスタイルのマッピング"
    )
```

### markup_utils.py（新規）

```python
import re
from dataclasses import dataclass


@dataclass
class TextSpan:
    """テキストスパン"""
    text: str
    style_name: str | None = None


def parse_styled_text(text: str) -> list[TextSpan]:
    """
    マークアップテキストをスパンのリストに変換

    例:
        "<A>hello</A><B>world</B>" -> [
            TextSpan(text="hello", style_name="A"),
            TextSpan(text="world", style_name="B")
        ]

        "plain text" -> [TextSpan(text="plain text", style_name=None)]
    """
    pass


def strip_markup(text: str) -> str:
    """
    マークアップを除去して素のテキストを返す

    例:
        "<A>hello</A><B>world</B>" -> "helloworld"
        "plain text" -> "plain text"
    """
    pass
```

---

## 実装詳細

### Phase 1: マークアップパーサーの実装

**ファイル**: `packages/core/teto_core/utils/markup_utils.py`

```python
import re
from dataclasses import dataclass


@dataclass
class TextSpan:
    """テキストスパン"""
    text: str
    style_name: str | None = None


# マークアップパターン: <TagName>content</TagName>
MARKUP_PATTERN = re.compile(r'<([A-Za-z_][A-Za-z0-9_]*)>(.*?)</\1>', re.DOTALL)


def parse_styled_text(text: str) -> list[TextSpan]:
    """マークアップテキストをスパンのリストに変換"""
    spans: list[TextSpan] = []
    last_end = 0

    for match in MARKUP_PATTERN.finditer(text):
        # マークアップ前のプレーンテキスト
        if match.start() > last_end:
            plain_text = text[last_end:match.start()]
            if plain_text:
                spans.append(TextSpan(text=plain_text, style_name=None))

        # マークアップ内のテキスト
        style_name = match.group(1)
        content = match.group(2)
        if content:
            spans.append(TextSpan(text=content, style_name=style_name))

        last_end = match.end()

    # 残りのプレーンテキスト
    if last_end < len(text):
        remaining = text[last_end:]
        if remaining:
            spans.append(TextSpan(text=remaining, style_name=None))

    # マークアップがない場合は元のテキストを単一スパンとして返す
    if not spans:
        spans.append(TextSpan(text=text, style_name=None))

    return spans


def strip_markup(text: str) -> str:
    """マークアップを除去して素のテキストを返す"""
    return MARKUP_PATTERN.sub(r'\2', text)
```

---

### Phase 2: データモデルの更新

**ファイル**: `packages/core/teto_core/layer/models.py`

SubtitleLayer に `styles` フィールドと `PartialStyle` モデルを追加。

---

### Phase 3: 画像レンダリングの変更

**ファイル**: `packages/core/teto_core/utils/image_utils.py`

スパンごとに描画する新しい関数を追加:

```python
def create_styled_text_image_with_pil(
    spans: list[TextSpan],
    styles: dict[str, PartialStyle],
    default_font_color: str,
    default_font_weight: str,
    font_path: str | None,
    font_size: int,
    max_width: int,
    stroke_width: int = 0,
    stroke_color: str = "black",
    outer_stroke_width: int = 0,
    outer_stroke_color: str = "white",
    video_height: int = 1080,
) -> tuple[np.ndarray, tuple[int, int]]:
    """スパンごとにスタイルを適用してテキスト画像を生成"""
    pass
```

**描画ロジック**:

1. 各スパンのスタイルを解決（デフォルト + 部分スタイルのマージ）
2. 全体のテキストサイズを計算
3. 縁取りを先に描画（レイヤー全体で統一）
4. 各スパンを順番に描画（X座標を累積）

---

### Phase 4: 音声生成での対応

**対象ファイル**: 音声生成時にテキストを取得する箇所

```python
from teto_core.utils.markup_utils import strip_markup

# 音声生成用のテキスト取得
plain_text = strip_markup(subtitle_item.text)
```

---

## タスク詳細

### Phase 1: マークアップパーサー

- [ ] `markup_utils.py` を新規作成
- [ ] `parse_styled_text()` 関数を実装
- [ ] `strip_markup()` 関数を実装
- [ ] ユニットテストを作成

### Phase 2: データモデル

- [ ] `PartialStyle` モデルを追加
- [ ] `SubtitleLayer` に `styles` フィールドを追加
- [ ] JSON スキーマの更新確認

### Phase 3: レンダリング

- [ ] `create_styled_text_image_with_pil()` 関数を追加
- [ ] 既存のレンダラーから新関数を呼び出すよう修正
- [ ] スパンがない場合は従来の描画にフォールバック

### Phase 4: 音声生成対応

- [ ] 音声生成時に `strip_markup()` を使用するよう修正

### Phase 5: テストと例

- [ ] サンプルプロジェクトJSON を作成
- [ ] 統合テストを実施

---

## 使用例

### 基本的な使い方

```json
{
  "subtitle_layers": [{
    "type": "subtitle",
    "styles": {
      "emphasis": {
        "font_color": "red",
        "font_weight": "bold"
      },
      "highlight": {
        "font_color": "yellow"
      }
    },
    "items": [{
      "text": "<emphasis>重要:</emphasis> これは<highlight>ハイライト</highlight>された文章です",
      "start_time": 1.0,
      "end_time": 4.0
    }],
    "font_size": "lg",
    "font_color": "white",
    "font_weight": "normal",
    "stroke_width": "sm",
    "stroke_color": "black",
    "position": "bottom"
  }]
}
```

### 結果

- "重要:" → 赤色・太字
- " これは" → 白色・通常（デフォルト）
- "ハイライト" → 黄色・通常
- "された文章です" → 白色・通常（デフォルト）

### 後方互換性

```json
{
  "subtitle_layers": [{
    "items": [{
      "text": "マークアップなしのテキスト",
      "start_time": 1.0,
      "end_time": 3.0
    }],
    "font_color": "white"
  }]
}
```

従来通り動作する。

---

## 設計上の考慮事項

### 1. 縁取りの部分適用について

縁取りを部分適用すると以下の問題がある:
- スパン境界で縁取りが重なる・途切れる
- 視覚的に不自然になりやすい

**結論**: 縁取りはレイヤー全体で統一し、部分適用は `font_color` と `font_weight` のみとする。

### 2. 折り返し処理

スパンをまたぐ折り返しが発生した場合:
- 折り返し位置でスパンを分割
- 各行ごとに描画

### 3. 音声生成との整合性

`strip_markup()` を使用することで、音声生成には素のテキストが渡される。これにより音声の自然さを維持。

---

## 今後の拡張案

- [ ] 入れ子マークアップのサポート
- [ ] フォントサイズの部分変更
- [ ] アニメーション効果の部分適用（フェードイン等）
- [ ] Script ファイルでのマークアップサポート

---

## 参考資料

### 関連ファイル

- `packages/core/teto_core/layer/models.py`: SubtitleLayer モデル定義
- `packages/core/teto_core/utils/image_utils.py`: テキスト画像生成
- `packages/core/teto_core/layer/processors/subtitle_renderers.py`: 字幕レンダラー

---

> **Note**: すべてのタスクが完了したら、このファイルを `tasks/completed/` ディレクトリに移動してください。
