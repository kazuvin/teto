# キャラクター配置機能 設計書

## 概要

Script モデルにキャラクター配置機能を追加し、テキストセグメント毎に表情を変えたり、アニメーションを付与できるようにする。

---

## 目次

1. [要件](#要件)
2. [データ構造設計](#データ構造設計)
3. [使用例](#使用例)
4. [実装方針](#実装方針)
5. [今後のステップ](#今後のステップ)

---

## 要件

### 機能要件

1. **キャラクター定義**: Script レベルで複数のキャラクターを定義できる
2. **表情切り替え**: 各テキストセグメント毎にキャラクターの表情を指定できる
3. **配置位置**: キャラクターの配置位置を指定できる（右下、左下、カスタム位置など）
4. **アニメーション**: キャラクターに揺れ、バウンドなどのアニメーションを付与できる
5. **複数キャラクター**: 1シーンに複数のキャラクターを配置できる
6. **音声連携**: キャラクターにボイスプロファイルを紐づけ、自動適用できる

### 非機能要件

- 既存の Script モデルとの後方互換性を維持
- AI が生成しやすいシンプルな構造
- 将来的な拡張（リップシンク、自動瞬きなど）に対応可能な設計

---

## 設計方針

| 項目 | 方針 | 理由 |
|------|------|------|
| レイヤー設計 | `CharacterLayer` を新設 | キャラクター固有機能の拡張性・コードの明確さ |
| Z オーダー | リストの順序で決定 | シンプルさ優先、AI 生成しやすい |
| 音声連携 | オプショナルで `voice_profile` と連携 | 利便性向上、後方互換性維持 |
| アニメーション | `CharacterAnimation` 専用モデル | キャラクター固有パラメータを明示 |

---

## データ構造設計

### Script レベル: キャラクター定義

```python
class CharacterExpression(BaseModel):
    """キャラクターの表情定義"""

    name: str = Field(..., description="表情名（例: 'normal', 'smile', 'angry'）")
    path: str = Field(..., description="表情画像ファイルパス")


class CharacterPosition(str, Enum):
    """キャラクター配置位置プリセット"""

    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
    BOTTOM_CENTER = "bottom-center"
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class CharacterAnimationType(str, Enum):
    """キャラクターアニメーションタイプ"""

    NONE = "none"           # アニメーションなし
    BOUNCE = "bounce"       # バウンド（上下に弾む）
    SHAKE = "shake"         # 揺れ（左右に小刻みに揺れる）
    NOD = "nod"             # 頷き（上下に小さく動く）
    SWAY = "sway"           # 揺らぎ（ゆっくり左右に揺れる）
    BREATHE = "breathe"     # 呼吸（拡大縮小）
    FLOAT = "float"         # 浮遊（上下にゆっくり動く）
    PULSE = "pulse"         # 脈動（リズミカルに拡大縮小）


class CharacterAnimation(BaseModel):
    """キャラクターアニメーション設定"""

    type: CharacterAnimationType = Field(
        CharacterAnimationType.NONE,
        description="アニメーションタイプ"
    )
    intensity: float = Field(
        1.0,
        description="アニメーション強度（0.5〜2.0）",
        ge=0.5, le=2.0
    )
    speed: float = Field(
        1.0,
        description="アニメーション速度（0.5〜2.0）",
        ge=0.5, le=2.0
    )


class CharacterDefinition(BaseModel):
    """キャラクター定義（Script レベル）"""

    id: str = Field(..., description="キャラクター識別子（参照用）")
    name: str = Field(..., description="キャラクター名（表示・メタデータ用）")

    # 表情定義
    expressions: list[CharacterExpression] = Field(
        ...,
        description="表情リスト（最低1つの表情が必要）",
        min_length=1
    )
    default_expression: str = Field(
        "normal",
        description="デフォルト表情名"
    )

    # 配置設定
    position: CharacterPosition = Field(
        CharacterPosition.BOTTOM_RIGHT,
        description="デフォルト配置位置"
    )
    custom_position: tuple[int, int] | None = Field(
        None,
        description="カスタム位置（x, y）※position より優先"
    )

    # サイズ設定
    scale: float = Field(
        1.0,
        description="キャラクターサイズ倍率",
        gt=0, le=3.0
    )

    # デフォルトアニメーション
    default_animation: CharacterAnimation = Field(
        default_factory=CharacterAnimation,
        description="デフォルトアニメーション設定"
    )

    # 音声連携（オプショナル）
    voice_profile: str | None = Field(
        None,
        description="このキャラクターに紐づくボイスプロファイル名（Script.voice_profiles から参照）"
    )


# Script モデルへの追加
class Script(BaseModel):
    # ... 既存フィールド ...

    # キャラクター定義
    characters: dict[str, CharacterDefinition] | None = Field(
        None,
        description="キャラクター定義（ID をキーとした辞書）"
    )
```

### NarrationSegment レベル: キャラクター状態指定

```python
class CharacterState(BaseModel):
    """セグメント内でのキャラクター状態"""

    character_id: str = Field(..., description="キャラクター ID")
    expression: str | None = Field(
        None,
        description="表情名（未指定時はデフォルト表情）"
    )
    animation: CharacterAnimation | None = Field(
        None,
        description="アニメーション設定（未指定時はデフォルトアニメーション）"
    )
    visible: bool = Field(
        True,
        description="表示/非表示"
    )


# NarrationSegment への追加
class NarrationSegment(BaseModel):
    # ... 既存フィールド ...

    # キャラクター状態
    character_states: list[CharacterState] = Field(
        default_factory=list,
        description="このセグメント中のキャラクター状態リスト"
    )
```

### Scene レベル: シーン単位のキャラクター設定

```python
class SceneCharacterConfig(BaseModel):
    """シーン単位のキャラクター設定"""

    character_id: str = Field(..., description="キャラクター ID")

    # シーン固有の上書き設定
    position: CharacterPosition | None = Field(
        None,
        description="このシーンでの配置位置（上書き）"
    )
    custom_position: tuple[int, int] | None = Field(
        None,
        description="このシーンでのカスタム位置（上書き）"
    )
    scale: float | None = Field(
        None,
        description="このシーンでのサイズ倍率（上書き）"
    )
    visible: bool = Field(
        True,
        description="このシーンでの表示/非表示"
    )


# Scene への追加
class Scene(BaseModel):
    # ... 既存フィールド ...

    # キャラクター設定（リスト順が Z オーダー：後のキャラクターが前面）
    characters: list[SceneCharacterConfig] = Field(
        default_factory=list,
        description="このシーンで表示するキャラクターの設定"
    )
```

### CharacterLayer（Project レベル：実行モデル）

```python
class CharacterLayer(BaseModel):
    """キャラクターレイヤー（実行用）

    Script の CharacterDefinition + CharacterState から生成される。
    各セグメントの表情・アニメーション変化毎に別レイヤーとして生成。
    """

    # 識別情報
    character_id: str = Field(..., description="キャラクター ID")
    character_name: str = Field(..., description="キャラクター名")
    expression: str = Field(..., description="表情名")

    # アセット
    path: str = Field(..., description="表情画像ファイルパス")

    # タイミング
    start_time: float = Field(..., description="開始時刻（秒）")
    end_time: float = Field(..., description="終了時刻（秒）")

    # 配置
    position: CharacterPosition = Field(
        CharacterPosition.BOTTOM_RIGHT,
        description="配置位置"
    )
    custom_position: tuple[int, int] | None = Field(
        None,
        description="カスタム位置（x, y）"
    )

    # スタイル
    scale: float = Field(1.0, description="サイズ倍率")
    opacity: float = Field(1.0, description="不透明度（0.0〜1.0）")

    # アニメーション
    animation: CharacterAnimation = Field(
        default_factory=CharacterAnimation,
        description="アニメーション設定"
    )

    # 将来の拡張用
    # lip_sync: bool = False
    # auto_blink: bool = False


# Timeline への追加
class Timeline(BaseModel):
    # ... 既存フィールド ...

    character_layers: list[CharacterLayer] = Field(
        default_factory=list,
        description="キャラクターレイヤーリスト"
    )
```

---

## 使用例

### JSON スクリプト例

```json
{
  "title": "キャラクター解説動画",
  "voice_profiles": {
    "teto_voice": {
      "provider": "google",
      "voice_id": "ja-JP-Wavenet-A"
    }
  },
  "characters": {
    "teto": {
      "id": "teto",
      "name": "テト",
      "expressions": [
        {"name": "normal", "path": "assets/characters/teto/normal.png"},
        {"name": "smile", "path": "assets/characters/teto/smile.png"},
        {"name": "surprise", "path": "assets/characters/teto/surprise.png"},
        {"name": "think", "path": "assets/characters/teto/think.png"}
      ],
      "default_expression": "normal",
      "position": "bottom-right",
      "scale": 0.8,
      "default_animation": {
        "type": "breathe",
        "intensity": 0.5,
        "speed": 0.8
      },
      "voice_profile": "teto_voice"
    }
  },
  "scenes": [
    {
      "visual": {"path": "background1.jpg"},
      "characters": [
        {"character_id": "teto"}
      ],
      "narrations": [
        {
          "text": "こんにちは！今日はTetoの使い方を説明します。",
          "character_states": [
            {"character_id": "teto", "expression": "smile"}
          ]
        },
        {
          "text": "実は、すごい機能があるんです！",
          "character_states": [
            {
              "character_id": "teto",
              "expression": "surprise",
              "animation": {"type": "bounce", "intensity": 1.5}
            }
          ]
        },
        {
          "text": "どんな機能だと思いますか？",
          "character_states": [
            {"character_id": "teto", "expression": "think"}
          ]
        }
      ]
    }
  ]
}
```

### 複数キャラクター例

```json
{
  "title": "対話動画",
  "voice_profiles": {
    "host_voice": {"provider": "google", "voice_id": "ja-JP-Wavenet-A"},
    "guest_voice": {"provider": "google", "voice_id": "ja-JP-Wavenet-B"}
  },
  "characters": {
    "host": {
      "id": "host",
      "name": "ホスト",
      "expressions": [
        {"name": "normal", "path": "assets/host/normal.png"},
        {"name": "smile", "path": "assets/host/smile.png"}
      ],
      "position": "bottom-left",
      "voice_profile": "host_voice"
    },
    "guest": {
      "id": "guest",
      "name": "ゲスト",
      "expressions": [
        {"name": "normal", "path": "assets/guest/normal.png"},
        {"name": "smile", "path": "assets/guest/smile.png"}
      ],
      "position": "bottom-right",
      "voice_profile": "guest_voice"
    }
  },
  "scenes": [
    {
      "visual": {"path": "studio.jpg"},
      "characters": [
        {"character_id": "host"},
        {"character_id": "guest"}
      ],
      "narrations": [
        {
          "text": "今日はゲストをお迎えしています！",
          "character_states": [
            {"character_id": "host", "expression": "smile"},
            {"character_id": "guest", "expression": "normal"}
          ]
        },
        {
          "text": "よろしくお願いします！",
          "voice_profile": "guest_voice",
          "character_states": [
            {"character_id": "host", "expression": "normal"},
            {"character_id": "guest", "expression": "smile", "animation": {"type": "nod"}}
          ]
        }
      ]
    }
  ]
}
```

### Python API 例

```python
from teto_core.script.models import (
    Script, Scene, NarrationSegment, Visual,
    CharacterDefinition, CharacterExpression,
    CharacterState, CharacterAnimation, SceneCharacterConfig,
    CharacterAnimationType, CharacterPosition, VoiceConfig
)

script = Script(
    title="キャラクター解説動画",
    voice_profiles={
        "teto_voice": VoiceConfig(provider="google", voice_id="ja-JP-Wavenet-A")
    },
    characters={
        "teto": CharacterDefinition(
            id="teto",
            name="テト",
            expressions=[
                CharacterExpression(name="normal", path="assets/teto/normal.png"),
                CharacterExpression(name="smile", path="assets/teto/smile.png"),
            ],
            position=CharacterPosition.BOTTOM_RIGHT,
            default_animation=CharacterAnimation(
                type=CharacterAnimationType.BREATHE,
                intensity=0.5
            ),
            voice_profile="teto_voice"
        )
    },
    scenes=[
        Scene(
            visual=Visual(path="bg.jpg"),
            characters=[SceneCharacterConfig(character_id="teto")],
            narrations=[
                NarrationSegment(
                    text="こんにちは！",
                    character_states=[
                        CharacterState(character_id="teto", expression="smile")
                    ]
                )
            ]
        )
    ]
)
```

---

## 実装方針

### 1. データモデル追加

**ファイル**: `packages/core/teto_core/script/models.py`

- `CharacterExpression`、`CharacterPosition`、`CharacterAnimationType`、`CharacterAnimation` を追加
- `CharacterDefinition`、`CharacterState`、`SceneCharacterConfig` を追加
- `Script` に `characters` フィールドを追加
- `Scene` に `characters` フィールドを追加
- `NarrationSegment` に `character_states` フィールドを追加

### 2. レイヤーモデル追加

**ファイル**: `packages/core/teto_core/layer/models.py`

- `CharacterLayer` を新設
- `Timeline` に `character_layers` フィールドを追加

### 3. コンパイラ拡張

**ファイル**: `packages/core/teto_core/script/compiler.py`

- キャラクター定義を解析し、各セグメントの開始/終了時刻に合わせて `CharacterLayer` を生成
- 表情・アニメーション変化毎に別レイヤーとして生成
- `voice_profile` が設定されている場合、自動的に音声設定を適用

### 4. キャラクターアニメーションエフェクト追加

**ファイル**: `packages/core/teto_core/effect/strategies/`

- `CharacterAnimationStrategy` を追加
- 各アニメーションタイプ（bounce, shake, breathe 等）の実装

### 5. レンダリングパイプライン拡張

**ファイル**: `packages/core/teto_core/generator/steps/`

- `CharacterLayerProcessing` ステップを追加
- キャラクター配置位置の計算ロジック
- アニメーション適用ロジック

### 6. プロセッサー追加

**ファイル**: `packages/core/teto_core/layer/processors/`

- `CharacterLayerProcessor` を追加
- 画像のリサイズ、配置、アニメーション適用

---

## 今後のステップ

1. 本設計書のレビュー・承認
2. データモデルの実装（Script レベル）
3. CharacterLayer の実装（Project レベル）
4. コンパイラの拡張
5. アニメーションエフェクトストラテジーの追加
6. CharacterLayerProcessor の実装
7. レンダリングパイプラインの拡張
8. テストの追加
9. サンプルスクリプトの作成
10. ドキュメントの更新

---

## 将来の拡張候補

- **リップシンク**: 音声に合わせた口パク自動生成
- **自動瞬き**: 一定間隔での瞬きアニメーション
- **表情トランジション**: 表情切り替え時のクロスフェード
- **Live2D 対応**: Live2D モデルの読み込み・制御

---

## 参考

- 既存ドキュメント: `docs/design/01_data_models.md`
- 既存モデル: `packages/core/teto_core/script/models.py`
- エフェクト: `packages/core/teto_core/effect/models.py`
- レイヤー: `packages/core/teto_core/layer/models.py`
