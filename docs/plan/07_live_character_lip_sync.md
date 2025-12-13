# 動く立ち絵機能 - リップシンク実装計画 (MVP)

## 概要

キャラクターの目・口などの複数のパーツ画像を組み合わせ、字幕(音声)に合わせてリップモーション(口パク)を自動生成する機能を実装する。

**MVP版**: 音素解析は行わず、発話中に一定間隔で口をパクパクさせるシンプルな実装。将来的な音素解析対応への拡張性を持たせた設計とする。

---

## 目次

1. [要件定義](#要件定義)
2. [設計方針](#設計方針)
3. [データ構造設計](#データ構造設計)
4. [リップシンクアルゴリズム](#リップシンクアルゴリズム)
5. [実装計画](#実装計画)
6. [使用例](#使用例)
7. [将来の拡張](#将来の拡張)

---

## 要件定義

### MVP 機能要件

#### 1. レイヤードキャラクターシステム
- ✅ **パーツ分離**: キャラクターを複数のパーツ(ベース、目、口、髪など)に分離して定義
- ✅ **パーツ組み合わせ**: 各パーツの状態を組み合わせてキャラクター表情を構成
- ✅ **透明度対応**: PNG 透過画像で各パーツを重ね合わせ

#### 2. シンプルなリップシンク機能 (MVP)
- ✅ **パクパクアニメーション**: 発話中に一定間隔で口を開閉
- ✅ **タイミング同期**: 音声の開始/終了に合わせて口パクを制御
- ✅ **カスタマイズ可能**: 口パク速度・口の形状を設定可能
- 🔮 **将来対応**: 音素解析ベースのリップシンクへの拡張性を確保

#### 3. 目の動き
- ✅ **自動瞬き**: 一定間隔でランダムに瞬き
- ✅ **瞬きカスタマイズ**: 瞬き頻度・速度の調整
- ✅ **表情連動**: 表情状態に応じた目の変化

#### 4. その他のアニメーション
- ✅ **呼吸アニメーション**: 自然な呼吸の動き
- ✅ **頷き・揺れ**: 感情表現に応じた動き
- ✅ **表情遷移**: 表情切り替え時のスムーズなクロスフェード

### 非機能要件

- 🔧 **パフォーマンス**: リアルタイム性は不要、動画生成時に処理
- 🔧 **拡張性**: 将来的に音素解析、Live2D、VRM モデル対応可能な設計
- 🔧 **互換性**: 既存のキャラクターシステム(06_character_system.md)と統合
- 🔧 **使いやすさ**: AI が生成しやすい JSON 構造

---

## 設計方針

### アーキテクチャの選択

| 項目 | MVP 方針 | 将来の拡張 |
|------|---------|-----------|
| パーツシステム | レイヤー方式 | 変更なし |
| リップシンク | **固定間隔パクパク方式** | **音素マッピング方式** |
| 口の形状 | 1種類(開き口) + 閉じ口 | 5母音ベース(あいうえお) |
| 音声解析 | **不要** | **Google Cloud TTS の音素情報活用** |
| 瞬き生成 | ランダム + ルールベース | 変更なし |

### MVP の利点

- ✅ **実装期間短縮**: 音素解析を省略、約15日で完成
- ✅ **十分な表現力**: 視聴者には自然に見える口パク
- ✅ **軽量処理**: 複雑な音声解析が不要
- ✅ **拡張可能**: インターフェースを統一し、将来の音素解析対応が容易

### 拡張性の確保

リップシンクエンジンをインターフェースとして抽象化し、実装を切り替え可能にする:

```python
class LipSyncEngine(ABC):
    """リップシンクエンジンの抽象基底クラス"""

    @abstractmethod
    def generate_mouth_keyframes(
        self,
        audio_path: str,
        text: str,
        start_time: float,
        duration: float,
        config: LipSyncConfig
    ) -> list[MouthKeyframe]:
        """口のキーフレームを生成"""
        pass

class SimplePakuPakuEngine(LipSyncEngine):
    """シンプルなパクパク方式(MVP)"""
    pass

class PhonemeMappingEngine(LipSyncEngine):
    """音素マッピング方式(将来実装)"""
    pass
```

### 段階的実装アプローチ

#### Phase 1: レイヤードキャラクターシステム (基本)
- パーツベースのキャラクター定義
- パーツ組み合わせレンダリング
- 静的な表情切り替え

#### Phase 2: シンプルなリップシンク (MVP - コア機能)
- 固定間隔パクパクアルゴリズム
- タイミング同期
- 口の形状切り替え

#### Phase 3: 目の動き
- 自動瞬きアルゴリズム
- 瞬きアニメーション

#### Phase 4: 高度なアニメーション
- 表情遷移のクロスフェード
- 呼吸・揺れアニメーション

---

## データ構造設計

### 1. レイヤードキャラクター定義

```python
from pydantic import BaseModel, Field
from enum import Enum
from abc import ABC, abstractmethod

class CharacterPartType(str, Enum):
    """キャラクターパーツタイプ"""
    BASE = "base"              # ベース(顔の輪郭、体など)
    EYES = "eyes"              # 目
    MOUTH = "mouth"            # 口
    EYEBROWS = "eyebrows"      # 眉
    HAIR = "hair"              # 髪
    ACCESSORY = "accessory"    # アクセサリー
    EFFECT = "effect"          # エフェクト(汗、頬の赤みなど)

class MouthShape(str, Enum):
    """口の形状タイプ"""
    CLOSED = "closed"          # 閉じ口
    OPEN = "open"              # 開き口(MVP用)
    # 将来の拡張用
    A = "a"                    # あ
    I = "i"                    # い
    U = "u"                    # う
    E = "e"                    # え
    O = "o"                    # お
    SMILE = "smile"            # 笑顔(歯を見せる)
    NEUTRAL = "neutral"        # ニュートラル(リラックス)

class EyeState(str, Enum):
    """目の状態"""
    OPEN = "open"              # 開いている
    CLOSED = "closed"          # 閉じている
    HALF = "half"              # 半目
    SMILE = "smile"            # 笑顔(目を細める)
    WIDE = "wide"              # 見開く
    SURPRISED = "surprised"    # 驚き

class CharacterPart(BaseModel):
    """キャラクターパーツ定義"""

    type: CharacterPartType = Field(..., description="パーツタイプ")
    name: str = Field(..., description="パーツ名(識別用)")
    path: str = Field(..., description="パーツ画像ファイルパス")

    # 位置調整(ベース画像に対する相対位置)
    offset_x: int = Field(0, description="X方向オフセット(px)")
    offset_y: int = Field(0, description="Y方向オフセット(px)")

    # Z-index (レイヤー順序)
    z_index: int = Field(0, description="Z順序(大きいほど前面)")

class LipSyncMode(str, Enum):
    """リップシンクモード"""
    SIMPLE_PAKU_PAKU = "simple_paku_paku"  # シンプルなパクパク(MVP)
    PHONEME_MAPPING = "phoneme_mapping"     # 音素マッピング(将来実装)
    DISABLED = "disabled"                   # リップシンク無効

class LipSyncConfig(BaseModel):
    """リップシンク設定"""

    mode: LipSyncMode = Field(
        LipSyncMode.SIMPLE_PAKU_PAKU,
        description="リップシンクモード"
    )

    # === シンプルパクパク方式の設定 (MVP) ===
    paku_interval: float = Field(
        0.15,
        description="口の開閉間隔(秒)",
        ge=0.05, le=0.5
    )
    paku_open_shape: MouthShape = Field(
        MouthShape.OPEN,
        description="口を開く時の形状"
    )
    paku_closed_shape: MouthShape = Field(
        MouthShape.CLOSED,
        description="口を閉じる時の形状"
    )
    paku_transition_duration: float = Field(
        0.05,
        description="口の開閉遷移時間(秒)",
        ge=0.01, le=0.1
    )

    # === 音素マッピング方式の設定 (将来実装) ===
    phoneme_map: dict[str, MouthShape] | None = Field(
        None,
        description="音素→口の形状マッピング(phoneme_mapping モード用)"
    )
    mouth_open_duration: float = Field(
        0.1,
        description="口を開ける動作の時間(秒)",
        ge=0.05, le=0.3
    )
    mouth_close_duration: float = Field(
        0.1,
        description="口を閉じる動作の時間(秒)",
        ge=0.05, le=0.3
    )
    default_mouth_hold: float = Field(
        0.15,
        description="口の形状を保持する時間(秒)",
        ge=0.1, le=0.5
    )

class BlinkConfig(BaseModel):
    """自動瞬き設定"""

    enabled: bool = Field(True, description="自動瞬き有効化")

    # 瞬き頻度(秒)
    blink_interval_min: float = Field(
        2.0,
        description="瞬き間隔の最小値(秒)",
        ge=0.5
    )
    blink_interval_max: float = Field(
        5.0,
        description="瞬き間隔の最大値(秒)",
        ge=1.0
    )

    # 瞬き動作の速度
    blink_duration: float = Field(
        0.15,
        description="瞬き1回の時間(秒)",
        ge=0.05, le=0.3
    )

    # 瞬き抑制(発話中は瞬きを減らす)
    suppress_during_speech: bool = Field(
        True,
        description="発話中の瞬きを抑制"
    )

class LayeredCharacterDefinition(BaseModel):
    """レイヤードキャラクター定義"""

    id: str = Field(..., description="キャラクター識別子")
    name: str = Field(..., description="キャラクター名")

    # パーツ定義
    parts: dict[str, list[CharacterPart]] = Field(
        ...,
        description="パーツグループ。キーは状態名(例: 'eyes.open', 'mouth.open')"
    )

    # デフォルト状態
    default_parts: dict[CharacterPartType, str] = Field(
        ...,
        description="各パーツタイプのデフォルト状態名"
    )

    # リップシンク設定
    lip_sync: LipSyncConfig = Field(
        default_factory=LipSyncConfig,
        description="リップシンク設定"
    )

    # 瞬き設定
    blink: BlinkConfig = Field(
        default_factory=BlinkConfig,
        description="自動瞬き設定"
    )

    # 配置設定
    position: "CharacterPosition" = Field(
        "bottom-right",
        description="デフォルト配置位置"
    )
    custom_position: tuple[int, int] | None = Field(
        None,
        description="カスタム位置(x, y)"
    )
    scale: float = Field(
        1.0,
        description="キャラクターサイズ倍率",
        gt=0, le=3.0
    )

    # 音声連携(オプショナル)
    voice_profile: str | None = Field(
        None,
        description="このキャラクターに紐づくボイスプロファイル名"
    )
```

### 2. パーツ状態指定(Narration Segment レベル)

```python
class CharacterPartState(BaseModel):
    """パーツ状態指定"""

    part_type: CharacterPartType = Field(..., description="パーツタイプ")
    state_name: str = Field(..., description="状態名")

class LayeredCharacterState(BaseModel):
    """レイヤードキャラクター状態(Segment レベル)"""

    character_id: str = Field(..., description="キャラクター ID")

    # パーツ状態のオーバーライド
    part_states: list[CharacterPartState] = Field(
        default_factory=list,
        description="パーツ状態リスト(指定がない場合はデフォルト)"
    )

    # リップシンク設定
    lip_sync_enabled: bool | None = Field(
        None,
        description="このセグメントのリップシンク有効化(None=デフォルト設定を使用)"
    )

    # 瞬き設定
    blink_enabled: bool | None = Field(
        None,
        description="このセグメントの瞬き有効化(None=デフォルト設定を使用)"
    )

    visible: bool = Field(True, description="表示/非表示")

# NarrationSegment への追加
class NarrationSegment(BaseModel):
    # ... 既存フィールド ...

    # レイヤードキャラクター状態
    layered_character_states: list[LayeredCharacterState] = Field(
        default_factory=list,
        description="レイヤードキャラクター状態リスト"
    )
```

### 3. レンダリング用モデル(Project レベル)

```python
class MouthKeyframe(BaseModel):
    """口のキーフレーム"""

    time: float = Field(..., description="時刻(秒)")
    shape: MouthShape = Field(..., description="口の形状")
    opacity: float = Field(1.0, description="不透明度(遷移用)", ge=0.0, le=1.0)

class EyeKeyframe(BaseModel):
    """目のキーフレーム"""

    time: float = Field(..., description="時刻(秒)")
    state: EyeState = Field(..., description="目の状態")
    opacity: float = Field(1.0, description="不透明度(遷移用)", ge=0.0, le=1.0)

class LayeredCharacterLayer(BaseModel):
    """レイヤードキャラクターレイヤー(実行用)"""

    # 識別情報
    character_id: str = Field(..., description="キャラクター ID")
    character_name: str = Field(..., description="キャラクター名")

    # タイミング
    start_time: float = Field(..., description="開始時刻(秒)")
    end_time: float = Field(..., description="終了時刻(秒)")

    # パーツ構成
    parts: list[CharacterPart] = Field(..., description="レンダリングするパーツリスト")

    # アニメーションキーフレーム
    mouth_keyframes: list[MouthKeyframe] = Field(
        default_factory=list,
        description="口のキーフレームリスト"
    )
    eye_keyframes: list[EyeKeyframe] = Field(
        default_factory=list,
        description="目のキーフレームリスト"
    )

    # 配置・スタイル
    position: str = Field("bottom-right", description="配置位置")
    custom_position: tuple[int, int] | None = Field(None, description="カスタム位置")
    scale: float = Field(1.0, description="サイズ倍率")
    opacity: float = Field(1.0, description="不透明度")

    # アニメーション
    animation: "CharacterAnimation | None" = Field(
        None,
        description="全体アニメーション(揺れ、呼吸など)"
    )

# Timeline への追加
class Timeline(BaseModel):
    # ... 既存フィールド ...

    layered_character_layers: list[LayeredCharacterLayer] = Field(
        default_factory=list,
        description="レイヤードキャラクターレイヤーリスト"
    )
```

---

## リップシンクアルゴリズム

### MVP: シンプルなパクパク方式

#### アルゴリズム概要

```
発話開始時刻: start_time
発話終了時刻: end_time
パクパク間隔: paku_interval

キーフレーム生成:
1. start_time: 口を閉じる
2. start_time + paku_interval/2: 口を開く
3. start_time + paku_interval: 口を閉じる
4. start_time + paku_interval*1.5: 口を開く
5. ...
6. end_time: 口を閉じる
```

#### 実装例

```python
class SimplePakuPakuEngine(LipSyncEngine):
    """シンプルなパクパク方式のリップシンクエンジン(MVP)"""

    def generate_mouth_keyframes(
        self,
        audio_path: str,
        text: str,
        start_time: float,
        duration: float,
        config: LipSyncConfig
    ) -> list[MouthKeyframe]:
        """口のキーフレームを生成"""

        keyframes = []
        current_time = start_time
        is_open = False

        # 開始時は閉じ口
        keyframes.append(MouthKeyframe(
            time=current_time,
            shape=config.paku_closed_shape,
            opacity=1.0
        ))

        # パクパクアニメーション
        while current_time < start_time + duration:
            # 次のキーフレーム時刻
            current_time += config.paku_interval / 2

            if current_time >= start_time + duration:
                break

            # 開閉を交互に
            is_open = not is_open
            shape = config.paku_open_shape if is_open else config.paku_closed_shape

            keyframes.append(MouthKeyframe(
                time=current_time,
                shape=shape,
                opacity=1.0
            ))

        # 終了時は閉じ口
        keyframes.append(MouthKeyframe(
            time=start_time + duration,
            shape=config.paku_closed_shape,
            opacity=1.0
        ))

        return keyframes
```

### 瞬きアルゴリズム

```python
import random

def generate_blink_keyframes(
    start_time: float,
    end_time: float,
    config: BlinkConfig,
    is_speaking: bool = False
) -> list[EyeKeyframe]:
    """瞬きキーフレームを生成"""

    keyframes = []
    current_time = start_time

    # 開始時は目を開く
    keyframes.append(EyeKeyframe(
        time=start_time,
        state=EyeState.OPEN,
        opacity=1.0
    ))

    while current_time < end_time:
        # 次の瞬きタイミングをランダムに決定
        interval = random.uniform(
            config.blink_interval_min,
            config.blink_interval_max
        )

        # 発話中は瞬き頻度を下げる
        if is_speaking and config.suppress_during_speech:
            interval *= 1.5

        next_blink = current_time + interval

        if next_blink >= end_time:
            break

        # 瞬き開始
        keyframes.append(EyeKeyframe(
            time=next_blink,
            state=EyeState.CLOSED,
            opacity=1.0
        ))

        # 瞬き終了(目を開ける)
        keyframes.append(EyeKeyframe(
            time=next_blink + config.blink_duration,
            state=EyeState.OPEN,
            opacity=1.0
        ))

        current_time = next_blink + config.blink_duration

    # 終了時は目を開く
    keyframes.append(EyeKeyframe(
        time=end_time,
        state=EyeState.OPEN,
        opacity=1.0
    ))

    return keyframes
```

---

## 実装計画

### Phase 1: データモデル実装

**ファイル**: `packages/core/teto_core/script/models.py`

#### タスク
1. ✅ `CharacterPartType`, `MouthShape`, `EyeState` Enum 追加
2. ✅ `CharacterPart`, `LayeredCharacterDefinition` モデル追加
3. ✅ `LipSyncMode`, `LipSyncConfig`, `BlinkConfig` モデル追加
4. ✅ `CharacterPartState`, `LayeredCharacterState` モデル追加
5. ✅ `NarrationSegment` に `layered_character_states` フィールド追加
6. ✅ `Script` に `layered_characters` フィールド追加

**ファイル**: `packages/core/teto_core/layer/models.py`

#### タスク
7. ✅ `MouthKeyframe`, `EyeKeyframe` モデル追加
8. ✅ `LayeredCharacterLayer` モデル追加
9. ✅ `Timeline` に `layered_character_layers` フィールド追加

**工数**: 2日

---

### Phase 2: リップシンクエンジン実装 (MVP)

**ファイル**: `packages/core/teto_core/animation/lip_sync.py` (新規)

#### タスク
1. ✅ `LipSyncEngine` 抽象基底クラス実装
2. ✅ `SimplePakuPakuEngine` 実装(MVP)
3. ✅ リップシンクエンジンファクトリー実装
4. 🔮 `PhonemeMappingEngine` スタブ実装(将来用)

**工数**: 2日

---

### Phase 3: 瞬きエンジン実装

**ファイル**: `packages/core/teto_core/animation/blink.py` (新規)

#### タスク
1. ✅ `generate_blink_keyframes()` 関数実装
2. ✅ ランダム瞬き生成
3. ✅ 発話中の瞬き抑制ロジック
4. ✅ シード値による再現性確保

**工数**: 2日

---

### Phase 4: コンパイラ拡張

**ファイル**: `packages/core/teto_core/script/compiler.py`

#### タスク
1. ✅ レイヤードキャラクター定義の解析
2. ✅ リップシンクエンジンの統合
3. ✅ 瞬きキーフレーム生成の統合
4. ✅ `LayeredCharacterLayer` の生成ロジック実装
5. ✅ 音声タイミング情報の取得(AudioLayer から)

**工数**: 3日

---

### Phase 5: レイヤープロセッサー実装

**ファイル**: `packages/core/teto_core/layer/processors/layered_character.py` (新規)

#### タスク
1. ✅ `LayeredCharacterProcessor` クラス実装
2. ✅ パーツ画像の読み込み
3. ✅ パーツの重ね合わせ(Z-index 順)
4. ✅ キーフレームに基づくパーツ切り替え
5. ✅ 位置・スケール・不透明度の適用
6. ✅ キーフレーム補間ロジック

**工数**: 3日

---

### Phase 6: レンダリングパイプライン統合

**ファイル**: `packages/core/teto_core/generator/steps/layered_character_layer.py` (新規)

#### タスク
1. ✅ `LayeredCharacterLayerProcessingStep` 実装
2. ✅ キーフレーム補間ロジック(フレーム単位)
3. ✅ moviepy との統合
4. ✅ パイプラインへの組み込み

**工数**: 2日

---

### Phase 7: テスト実装

**ファイル**: `packages/core/tests/`

#### タスク
1. ✅ SimplePakuPakuEngine のユニットテスト
2. ✅ 瞬きエンジンのユニットテスト
3. ✅ レイヤードキャラクター統合テスト
4. ✅ E2E テスト(JSON → 動画生成)

**工数**: 2日

---

### Phase 8: ドキュメント・サンプル作成

#### タスク
1. ✅ API ドキュメント更新
2. ✅ サンプルキャラクター素材の作成
   - ベース画像
   - 口パーツ(閉じ口、開き口)
   - 目パーツ(開き、閉じ、半目)
3. ✅ サンプル JSON スクリプト作成
4. ✅ チュートリアルドキュメント作成

**工数**: 2日

---

### 実装スケジュール(推定)

| Phase | 内容 | 工数(日) |
|-------|------|---------|
| Phase 1 | データモデル実装 | 2 |
| Phase 2 | リップシンクエンジン実装(MVP) | 2 |
| Phase 3 | 瞬きエンジン実装 | 2 |
| Phase 4 | コンパイラ拡張 | 3 |
| Phase 5 | レイヤープロセッサー実装 | 3 |
| Phase 6 | レンダリングパイプライン統合 | 2 |
| Phase 7 | テスト実装 | 2 |
| Phase 8 | ドキュメント・サンプル作成 | 2 |
| **合計** | | **18日** |

※ 音素解析を省略したため、27日 → 18日に短縮

---

## 使用例

### 1. レイヤードキャラクター定義 (MVP用)

```json
{
  "layered_characters": {
    "teto": {
      "id": "teto",
      "name": "テト",
      "parts": {
        "base": [
          {
            "type": "base",
            "name": "body",
            "path": "assets/teto/base.png",
            "z_index": 0
          }
        ],
        "eyes.open": [
          {
            "type": "eyes",
            "name": "eyes_open",
            "path": "assets/teto/eyes_open.png",
            "z_index": 2
          }
        ],
        "eyes.closed": [
          {
            "type": "eyes",
            "name": "eyes_closed",
            "path": "assets/teto/eyes_closed.png",
            "z_index": 2
          }
        ],
        "eyes.smile": [
          {
            "type": "eyes",
            "name": "eyes_smile",
            "path": "assets/teto/eyes_smile.png",
            "z_index": 2
          }
        ],
        "mouth.closed": [
          {
            "type": "mouth",
            "name": "mouth_closed",
            "path": "assets/teto/mouth_closed.png",
            "z_index": 3
          }
        ],
        "mouth.open": [
          {
            "type": "mouth",
            "name": "mouth_open",
            "path": "assets/teto/mouth_open.png",
            "z_index": 3
          }
        ],
        "hair": [
          {
            "type": "hair",
            "name": "hair_front",
            "path": "assets/teto/hair.png",
            "z_index": 4
          }
        ]
      },
      "default_parts": {
        "base": "base",
        "eyes": "eyes.open",
        "mouth": "mouth.closed",
        "hair": "hair"
      },
      "lip_sync": {
        "mode": "simple_paku_paku",
        "paku_interval": 0.15,
        "paku_open_shape": "open",
        "paku_closed_shape": "closed"
      },
      "blink": {
        "enabled": true,
        "blink_interval_min": 2.0,
        "blink_interval_max": 4.5,
        "blink_duration": 0.12,
        "suppress_during_speech": true
      }
    }
  }
}
```

### 2. シーンでの使用

```json
{
  "scenes": [
    {
      "visual": {
        "path": "background.jpg"
      },
      "narrations": [
        {
          "text": "こんにちは!今日はTetoの使い方を紹介します。",
          "layered_character_states": [
            {
              "character_id": "teto",
              "part_states": [
                {
                  "part_type": "eyes",
                  "state_name": "eyes.smile"
                }
              ],
              "lip_sync_enabled": true,
              "blink_enabled": true
            }
          ]
        },
        {
          "text": "実はすごい機能があるんです!",
          "layered_character_states": [
            {
              "character_id": "teto",
              "part_states": [
                {
                  "part_type": "eyes",
                  "state_name": "eyes.wide"
                }
              ],
              "lip_sync_enabled": true,
              "blink_enabled": false
            }
          ]
        }
      ]
    }
  ]
}
```

### 3. Python API

```python
from teto_core.script.models import (
    Script, Scene, NarrationSegment,
    LayeredCharacterDefinition, CharacterPart,
    LayeredCharacterState, CharacterPartState,
    LipSyncConfig, BlinkConfig, LipSyncMode,
    CharacterPartType, MouthShape, EyeState
)

# キャラクター定義
teto = LayeredCharacterDefinition(
    id="teto",
    name="テト",
    parts={
        "base": [
            CharacterPart(
                type=CharacterPartType.BASE,
                name="body",
                path="assets/teto/base.png",
                z_index=0
            )
        ],
        "eyes.open": [
            CharacterPart(
                type=CharacterPartType.EYES,
                name="eyes_open",
                path="assets/teto/eyes_open.png",
                z_index=2
            )
        ],
        "mouth.closed": [
            CharacterPart(
                type=CharacterPartType.MOUTH,
                name="mouth_closed",
                path="assets/teto/mouth_closed.png",
                z_index=3
            )
        ],
        "mouth.open": [
            CharacterPart(
                type=CharacterPartType.MOUTH,
                name="mouth_open",
                path="assets/teto/mouth_open.png",
                z_index=3
            )
        ],
    },
    default_parts={
        CharacterPartType.BASE: "base",
        CharacterPartType.EYES: "eyes.open",
        CharacterPartType.MOUTH: "mouth.closed",
    },
    lip_sync=LipSyncConfig(
        mode=LipSyncMode.SIMPLE_PAKU_PAKU,
        paku_interval=0.15,
        paku_open_shape=MouthShape.OPEN,
        paku_closed_shape=MouthShape.CLOSED
    ),
    blink=BlinkConfig(
        enabled=True,
        blink_interval_min=2.0,
        blink_interval_max=4.5
    )
)

# スクリプト作成
script = Script(
    title="リップシンクデモ",
    layered_characters={"teto": teto},
    scenes=[
        Scene(
            visual={"path": "bg.jpg"},
            narrations=[
                NarrationSegment(
                    text="こんにちは!",
                    layered_character_states=[
                        LayeredCharacterState(
                            character_id="teto",
                            part_states=[
                                CharacterPartState(
                                    part_type=CharacterPartType.EYES,
                                    state_name="eyes.smile"
                                )
                            ],
                            lip_sync_enabled=True,
                            blink_enabled=True
                        )
                    ]
                )
            ]
        )
    ]
)
```

---

## 将来の拡張

### 1. 音素解析ベースのリップシンク

**実装時の追加作業**:

#### Phase A: 音素抽出実装

**ファイル**: `packages/core/teto_core/tts/phoneme_extractor.py` (新規)

- Google Cloud TTS から音素情報を取得
- SSML マーク使用
- 音素抽出キャッシュ機能
- フォールバック: SimplePakuPakuEngine

#### Phase B: PhonemeMappingEngine 実装

**ファイル**: `packages/core/teto_core/animation/lip_sync.py`

- `PhonemeMappingEngine` クラス実装
- 音素→口の形状マッピングテーブル
- 母音抽出ロジック

#### Phase C: キャラクター素材拡張

- 5母音パーツ(あいうえお)の追加

**追加工数**: 約9日

### 2. Live2D / VRM 対応
- Live2D モデルのインポート(.moc3 ファイル)
- VRM モデルのインポート(3D キャラクター)
- 物理演算(髪・服の揺れ)

### 3. 表情の高度化
- 表情遷移のクロスフェード
- 微表情(眉の動き、頬の赤み)
- 視線制御(目の向き・視線追従)

### 4. プレビュー機能
- リアルタイムプレビュー(デスクトップアプリ)
- キーフレームエディタ(GUI)

---

## 技術的課題と対策

### 課題1: パーツ画像の位置合わせ

**問題**: パーツ画像のサイズ・位置がズレる

**対策**:
- パーツ画像作成ガイドライン整備
- offset_x, offset_y による微調整機能
- プレビュー機能での確認

### 課題2: レンダリングパフォーマンス

**問題**: パーツの重ね合わせ処理がフレーム毎に発生し、処理が重い

**対策**:
- キーフレーム間のパーツが変わらない場合はキャッシュ
- moviepy の最適化オプション活用
- 並列処理の活用

### 課題3: 口パクのタイミング

**問題**: 固定間隔のパクパクが不自然に見える場合がある

**対策**:
- paku_interval のデフォルト値を調整(0.15秒)
- ユーザーがカスタマイズ可能
- 将来的に音素解析へ移行

---

## 参考資料

- [Google Cloud Text-to-Speech - Timepoint](https://cloud.google.com/text-to-speech/docs/ssml)
- [日本語音韻論](https://ja.wikipedia.org/wiki/%E6%97%A5%E6%9C%AC%E8%AA%9E%E3%81%AE%E9%9F%B3%E9%9F%BB%E8%AB%96)
- [Live2D Cubism SDK](https://www.live2d.com/sdk/)
- [moviepy ドキュメント](https://zulko.github.io/moviepy/)

---

## まとめ

この設計書では、レイヤードキャラクターシステムとシンプルなリップシンク機能(MVP)を Teto に統合する詳細な計画を示しました。

### MVP の特徴:
- ✅ **パーツベースシステム**: 柔軟なキャラクター表現
- ✅ **シンプルなリップシンク**: 固定間隔パクパク、実装が容易
- ✅ **自動瞬き**: 自然な瞬きアニメーション
- ✅ **拡張性**: 音素解析、Live2D、VRM への将来的な対応可能
- ✅ **使いやすさ**: AI が生成しやすい JSON 構造

### 実装スケジュール:
- MVP: **18日**
- 音素解析対応(将来): **+9日**

この MVP により、Teto は早期にキャラクター動画機能を提供でき、ユーザーフィードバックを得ながら段階的に高度化できます。
