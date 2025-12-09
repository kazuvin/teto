# データモデル詳細

このドキュメントでは、Teto のコアとなるデータモデルの詳細を説明します。

---

## 目次

1. [Script モデル（高レベル API）](#script-モデル高レベル-api)
2. [Project モデル（実行モデル）](#project-モデル実行モデル)
3. [Layer モデル](#layer-モデル)
4. [Effect モデル](#effect-モデル)
5. [Output Configuration](#output-configuration)

---

## Script モデル（高レベル API）

**場所**: `packages/core/teto_core/script/models.py`

Script モデルは AI や人間が簡単に記述できる高レベルな動画の台本表現です。

### Script

トップレベルモデル。動画全体の設定を含みます。

```python
class Script(BaseModel):
    """台本（AI 生成用の抽象データ構造）"""

    title: str                                              # 動画タイトル
    scenes: list[Scene]                                     # シーンのリスト（最低1つ）

    # グローバル設定
    voice: VoiceConfig                                      # デフォルト音声設定
    voice_profiles: dict[str, VoiceConfig] | None           # 名前付き音声プロファイル
    timing: TimingConfig                                    # タイミング設定
    bgm: BGMConfig | None                                   # BGM 設定
    image_generation: ImageGenerationConfig                 # AI 画像生成設定

    # 出力設定
    output: OutputSettings | list[OutputSettings]           # 単一または複数出力
    output_dir: str | None                                  # 出力ディレクトリ

    # 字幕設定
    subtitle_style: SubtitleStyleConfig                     # 字幕スタイル
    subtitle_styles: dict[str, PartialStyle]                # 部分スタイル定義

    # プリセット設定
    default_preset: str | None                              # デフォルト複合プリセット名
    default_effect: str                                     # デフォルトエフェクト名
    description: str | None                                 # 動画の説明
```

**主な機能**:
- マルチ出力対応: `output` に配列を指定することで、複数のアスペクト比の動画を同時生成
- 名前付き音声プロファイル: 複数キャラクターの対話に対応
- 複合プリセット: フック・概要・本編・CTAといった粒度の粗いプリセットで複数の設定を一括管理
- エフェクトプリセット: 全シーンに適用されるアニメーションエフェクト設定

### Scene

動画の1シーン（基本単位）。

```python
class Scene(BaseModel):
    """シーン（台本の基本単位）"""

    narrations: list[NarrationSegment]                      # ナレーションリスト
    visual: Visual                                          # 映像指定

    # タイミング
    duration: float | None                                  # シーン長さ（秒）※ナレーションありなら自動計算
    pause_after: float                                      # このシーン後の間隔（秒）

    # エフェクト
    transition: TransitionConfig | None                     # トランジション設定
    sound_effects: list[SoundEffect]                        # 効果音リスト

    # オプション
    note: str | None                                        # 演出メモ
    preset: str | None                                      # 複合プリセット名
    effect: str | None                                      # エフェクト名
    mute_video: bool                                        # 動画の音声ミュート

    # 音声設定（シーン固有）
    voice: VoiceConfig | None                               # このシーン専用の音声設定
    voice_profile: str | None                               # ボイスプロファイル名

    @model_validator(mode="after")
    def validate_duration_for_no_narration(self):
        # ナレーションなしの場合、duration は必須
        if len(self.narrations) == 0 and self.duration is None:
            raise ValueError("ナレーションがないシーンには duration を指定してください")
        return self

    @model_validator(mode="after")
    def validate_voice_config(self):
        # voice と voice_profile の両方が指定されている場合はエラー
        if self.voice is not None and self.voice_profile is not None:
            raise ValueError("voice と voice_profile は同時に指定できません")
        return self
```

**ユースケース**:

1. **ナレーションありのシーン**:
   ```json
   {
     "narrations": [{"text": "こんにちは"}],
     "visual": {"path": "image.jpg"}
   }
   ```
   → duration は自動計算

2. **ナレーションなしのシーン**（タイトル画面など）:
   ```json
   {
     "narrations": [],
     "visual": {"path": "title.jpg"},
     "duration": 3.0
   }
   ```
   → duration は必須

3. **シーン固有の音声**:
   ```json
   {
     "narrations": [{"text": "生徒のセリフ"}],
     "visual": {"path": "student.jpg"},
     "voice_profile": "student"
   }
   ```

### NarrationSegment

1つの字幕セグメント。

```python
class NarrationSegment(BaseModel):
    """ナレーションセグメント（字幕1つ分）"""

    text: str                                               # 字幕テキスト
    pause_after: float = 0.0                                # このセグメント後の間隔（秒）
```

**用途**:
- 画面に表示できる文字数に合わせて分割
- セグメント間に pause_after で間隔を挿入可能

### Visual

映像の指定（ローカルファイルまたは AI 生成）。

```python
class Visual(BaseModel):
    """映像指定"""

    type: AssetType | None                                  # アセットタイプ（自動判定可）
    description: str | None                                 # 映像の説明（AI 生成時はプロンプト）
    path: str | None                                        # 直接パス指定
    generate: ImageGenerationConfig | None                  # AI 画像生成設定
```

**使用パターン**:

1. **ローカルファイル指定**:
   ```json
   {"path": "examples/assets/images/sample1.jpg"}
   ```

2. **AI 画像生成**:
   ```json
   {
     "description": "A serene mountain landscape at sunset",
     "generate": {
       "provider": "stability",
       "style_preset": "photographic",
       "aspect_ratio": "16:9"
     }
   }
   ```

### VoiceConfig

TTS 音声設定。

```python
class VoiceConfig(BaseModel):
    """ナレーション音声設定"""

    # 共通設定
    provider: Literal["google", "openai", "voicevox", "elevenlabs", "gemini"]
    voice_id: str | None                                    # 声の指定（プロバイダー依存）
    language_code: str = "ja-JP"                            # 言語コード
    speed: float = 1.0                                      # 話速（0.5〜2.0）
    pitch: float = 0.0                                      # ピッチ（-20〜20）

    # ElevenLabs 固有設定
    model_id: str = "eleven_multilingual_v2"                # ElevenLabs モデル ID
    output_format: str = "mp3_44100_128"                    # 出力フォーマット

    # Gemini 固有設定
    voice_name: str = "Kore"                                # Gemini 音声名
    gemini_model_id: str = "gemini-2.5-flash-preview-tts"  # Gemini モデル ID
    style_prompt: str | None = None                         # 音声スタイルの指示プロンプト
```

**プロバイダー別の特徴**:

| プロバイダー | 特徴 | voice_id の例 |
|------------|------|--------------|
| google | WaveNet/Neural2、SSML 対応 | `ja-JP-Wavenet-A` |
| elevenlabs | 高品質、ボイスクローニング | カスタム voice ID |
| gemini | 表現力、スタイルプロンプト | 音声名を使用 |

### TimingConfig

タイミング設定。

```python
class TimingConfig(BaseModel):
    """タイミング設定"""

    default_segment_gap: float = 0.3                        # セグメント間のデフォルト間隔（秒）
    default_scene_gap: float = 0.5                          # シーン間のデフォルト間隔（秒）
    subtitle_padding: float = 0.1                           # 字幕の前後パディング（秒）
```

### BGMConfig

BGM 設定。

```python
class BGMConfig(BaseModel):
    """BGM 設定"""

    path: str                                               # BGM ファイルパス
    volume: float = 0.3                                     # 音量（0.0〜1.0）
    fade_in: float = 0.0                                    # フェードイン時間（秒）
    fade_out: float = 0.0                                   # フェードアウト時間（秒）
```

### SoundEffect

効果音設定。

```python
class SoundEffect(BaseModel):
    """効果音設定"""

    path: str                                               # 効果音ファイルパス
    offset: float = 0.0                                     # シーン開始からのオフセット（秒）
    volume: float = 1.0                                     # 音量（0.0〜1.0）
```

### PresetConfig

複合プリセット設定。フック・概要・本編・CTAといった粒度の粗いプリセットを定義。

```python
class PresetConfig(BaseModel):
    """複合プリセット設定"""

    # エフェクト参照
    effect: str | None                                      # エフェクト名

    # または直接エフェクトを指定
    effects: list[AnimationEffect]                          # アニメーションエフェクト
    transition: TransitionConfig | None                     # トランジション設定

    # 字幕スタイル
    subtitle_style: SubtitleStyleConfig | None              # 字幕スタイル設定

    # BGM設定
    bgm: BGMConfig | None                                   # BGM設定

    # タイミング
    timing_override: TimingConfig | None                    # タイミング設定の上書き

    # 音声設定
    voice: VoiceConfig | None                               # 音声設定
```

**デフォルトプリセット**:

| プリセット名 | 用途 | 特徴 |
|------------|------|------|
| `hook` | 動画の冒頭 | dramaticエフェクト、大きめの字幕、速いテンポ |
| `overview` | 概要説明 | Ken Burnsエフェクト、標準的な字幕 |
| `main_content` | メインコンテンツ | シンプル、読みやすい字幕 |
| `cta` | 行動喚起 | dramaticエフェクト、目立つ黄色の字幕 |

**使用例**:

```json
{
  "title": "商品紹介動画",
  "default_preset": "main_content",
  "scenes": [
    {
      "preset": "hook",
      "narrations": [{"text": "今日は特別なお知らせがあります！"}],
      "visual": {"path": "hook.jpg"}
    },
    {
      "preset": "overview",
      "narrations": [{"text": "この商品の3つの特徴をご紹介します"}],
      "visual": {"path": "overview.jpg"}
    },
    {
      "narrations": [{"text": "特徴1: 高品質"}],
      "visual": {"path": "feature1.jpg"}
    },
    {
      "preset": "cta",
      "narrations": [{"text": "今すぐチャンネル登録！"}],
      "visual": {"path": "cta.jpg"}
    }
  ]
}
```

---

## Project モデル（実行モデル）

**場所**: `packages/core/teto_core/project/models.py`

Project モデルは動画レンダリングエンジンが実行する低レベルな表現です。

### Project

```python
class Project(BaseModel):
    """プロジェクト（実行用の具体的なデータ構造）"""

    output: OutputConfig                                    # 出力設定（パス含む）
    timeline: Timeline                                      # タイムライン
```

**Script との違い**:
- Script: 抽象的、AI フレンドリー、タイミング自動計算
- Project: 具体的、実行に必要な全情報、タイミング明示

### Timeline

```python
class Timeline(BaseModel):
    """タイムライン（全レイヤーの集合）"""

    video_layers: list[VideoLayer | ImageLayer] = []        # 映像レイヤー
    audio_layers: list[AudioLayer] = []                     # 音声レイヤー
    subtitle_layers: list[SubtitleLayer] = []               # 字幕レイヤー
    stamp_layers: list[StampLayer] = []                     # スタンプレイヤー
```

---

## Layer モデル

**場所**: `packages/core/teto_core/layer/models.py`

### VideoLayer

動画ファイルレイヤー。

```python
class VideoLayer(BaseModel):
    """動画レイヤー"""

    path: str                                               # 動画ファイルパス
    start_time: float                                       # 開始時刻（秒）
    end_time: float                                         # 終了時刻（秒）
    duration: float | None = None                           # 再生時間（Noneなら元の長さ）

    # オーディオ
    volume: float = 1.0                                     # 音量（0.0〜1.0）

    # ループ
    loop: bool = False                                      # ループ再生

    # エフェクト・トランジション
    effects: list[AnimationEffect] = []                     # アニメーションエフェクト
    transition: TransitionConfig | None = None              # トランジション
```

### ImageLayer

画像ファイルレイヤー。

```python
class ImageLayer(BaseModel):
    """画像レイヤー"""

    path: str                                               # 画像ファイルパス
    start_time: float                                       # 開始時刻（秒）
    end_time: float                                         # 終了時刻（秒）
    duration: float                                         # 表示時間（秒）

    # エフェクト・トランジション
    effects: list[AnimationEffect] = []                     # アニメーションエフェクト
    transition: TransitionConfig | None = None              # トランジション
```

### AudioLayer

音声レイヤー。

```python
class AudioLayer(BaseModel):
    """音声レイヤー"""

    path: str                                               # 音声ファイルパス
    start_time: float = 0.0                                 # 開始時刻（秒）
    volume: float = 1.0                                     # 音量（0.0〜1.0）
    duration: float | None = None                           # 再生時間（Noneなら元の長さ）
```

**用途**:
- ナレーション音声
- 効果音
- BGM

### SubtitleLayer

字幕レイヤー。

```python
class SubtitleLayer(BaseModel):
    """字幕レイヤー"""

    items: list[SubtitleItem]                               # 字幕アイテムリスト

    # スタイル設定
    font_family: str = "Noto Sans JP"                       # フォントファミリー
    font_size: int | FontSize = 48                          # フォントサイズ
    font_color: str = "white"                               # フォントカラー
    font_weight: FontWeight | None = None                   # フォント太さ

    # 背景設定
    background_color: str | None = "black"                  # 背景色
    background_opacity: float = 0.7                         # 背景不透明度
    background_padding: int = 20                            # 背景パディング

    # 配置
    position: Position = Position.BOTTOM                    # 配置位置
    margin_x: int = 50                                      # 左右マージン
    margin_y: int = 50                                      # 上下マージン

    # アピアランス
    appearance: Appearance = Appearance.BACKGROUND          # 見た目（背景/影/ドロップシャドウ）

    # 部分スタイル
    partial_styles: dict[str, PartialStyle] = {}            # マークアップ用部分スタイル
```

### SubtitleItem

個別の字幕アイテム。

```python
class SubtitleItem(BaseModel):
    """字幕アイテム"""

    text: str                                               # 字幕テキスト
    start_time: float                                       # 開始時刻（秒）
    end_time: float                                         # 終了時刻（秒）
```

**マークアップサポート**:
```json
{
  "text": "これは<emphasis>重要</emphasis>です",
  "start_time": 0.0,
  "end_time": 3.0
}
```

### StampLayer

スタンプ（オーバーレイ画像）レイヤー。

```python
class StampLayer(BaseModel):
    """スタンプレイヤー"""

    path: str                                               # 画像ファイルパス
    start_time: float = 0.0                                 # 開始時刻（秒）
    duration: float | None = None                           # 表示時間（Noneなら最後まで）

    # 配置
    position: StampPosition | None = None                   # 位置プリセット
    custom_position: tuple[int, int] | None = None          # カスタム位置

    # スタイル
    opacity: float = 1.0                                    # 不透明度（0.0〜1.0）
    scale: float = 1.0                                      # スケール

    # エフェクト
    effects: list[AnimationEffect] = []                     # アニメーションエフェクト
```

**位置プリセット**:
```python
class StampPosition(str, Enum):
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
    CENTER = "center"
```

---

## Effect モデル

**場所**: `packages/core/teto_core/effect/models.py`

### AnimationEffect

アニメーションエフェクト。

```python
class AnimationEffect(BaseModel):
    """アニメーションエフェクト"""

    type: str                                               # エフェクトタイプ
    duration: float | None = None                           # エフェクト時間（秒）
    params: dict[str, Any] = {}                             # エフェクト固有パラメータ
```

**エフェクトタイプ例**:

| タイプ | 説明 | パラメータ例 |
|--------|------|------------|
| `fadeIn` | フェードイン | `{"duration": 1.0}` |
| `fadeOut` | フェードアウト | `{"duration": 1.0}` |
| `slideIn` | スライドイン | `{"direction": "left", "duration": 1.0}` |
| `zoom` | ズーム | `{"scale": 1.5, "duration": 3.0}` |
| `kenburns` | Ken Burns | `{"start_zoom": 1.0, "end_zoom": 1.2, "direction": "right"}` |
| `blur` | ブラー | `{"sigma": 5.0}` |
| `colorGrade` | カラーグレーディング | `{"temperature": 10, "saturation": 1.2}` |

### TransitionConfig

トランジション設定。

```python
class TransitionConfig(BaseModel):
    """トランジション設定"""

    type: TransitionType                                    # トランジションタイプ
    duration: float = 1.0                                   # トランジション時間（秒）

class TransitionType(str, Enum):
    CROSSFADE = "crossfade"                                 # クロスフェード
    # 将来: WIPE, SLIDE, etc.
```

---

## Output Configuration

**場所**: `packages/core/teto_core/output_config/models.py`

### OutputSettings

出力設定（パスなし、Script 用）。

```python
class OutputSettings(BaseModel):
    """出力設定（パスなし）"""

    name: str | None = None                                 # 出力名（マルチ出力時）
    aspect_ratio: AspectRatio | str = AspectRatio.LANDSCAPE # アスペクト比
    width: int | None = None                                # 幅（ピクセル）
    height: int | None = None                               # 高さ（ピクセル）
    fps: int = 30                                           # フレームレート
    codec: str = "libx264"                                  # コーデック
    preset: str = "medium"                                  # エンコードプリセット
    subtitle_mode: SubtitleMode = SubtitleMode.BURN         # 字幕モード
    object_fit: ObjectFit = ObjectFit.CONTAIN               # オブジェクトフィット
```

### OutputConfig

出力設定（パスあり、Project 用）。

```python
class OutputConfig(BaseModel):
    """出力設定（パスあり）"""

    path: str                                               # 出力ファイルパス
    aspect_ratio: AspectRatio | str = AspectRatio.LANDSCAPE
    width: int | None = None
    height: int | None = None
    fps: int = 30
    codec: str = "libx264"
    preset: str = "medium"
    subtitle_mode: SubtitleMode = SubtitleMode.BURN
    object_fit: ObjectFit = ObjectFit.CONTAIN
```

### AspectRatio

アスペクト比プリセット。

```python
class AspectRatio(str, Enum):
    LANDSCAPE = "16:9"                                      # YouTube 標準
    PORTRAIT = "9:16"                                       # TikTok, Instagram Reels
    SQUARE = "1:1"                                          # Instagram 投稿
    WIDE = "21:9"                                           # 映画的
    STANDARD = "4:3"                                        # 従来型
```

### SubtitleMode

字幕モード。

```python
class SubtitleMode(str, Enum):
    BURN = "burn"                                           # 字幕を動画に焼き込み
    SRT = "srt"                                             # SRT ファイルとして出力
    VTT = "vtt"                                             # VTT ファイルとして出力
    NONE = "none"                                           # 字幕なし
```

### ObjectFit

オブジェクトフィット（画像・動画の配置方法）。

```python
class ObjectFit(str, Enum):
    CONTAIN = "contain"                                     # アスペクト比維持、全体表示
    COVER = "cover"                                         # アスペクト比維持、画面いっぱい
    FILL = "fill"                                           # 引き伸ばし
```

**動作例**:

- **contain**: 黒帯を付けて全体を表示（デフォルト）
- **cover**: 余白なし、はみ出た部分は切り取り
- **fill**: アスペクト比を無視して引き伸ばし

---

## データモデルの関係図

```
Script
├── scenes: list[Scene]
│   ├── narrations: list[NarrationSegment]
│   ├── visual: Visual
│   ├── voice: VoiceConfig (optional)
│   └── sound_effects: list[SoundEffect]
├── voice: VoiceConfig (global)
├── voice_profiles: dict[str, VoiceConfig]
├── timing: TimingConfig
├── bgm: BGMConfig
└── output: OutputSettings | list[OutputSettings]

                    ↓ (ScriptCompiler)

Project
├── output: OutputConfig
└── timeline: Timeline
    ├── video_layers: list[VideoLayer | ImageLayer]
    │   ├── effects: list[AnimationEffect]
    │   └── transition: TransitionConfig
    ├── audio_layers: list[AudioLayer]
    ├── subtitle_layers: list[SubtitleLayer]
    │   ├── items: list[SubtitleItem]
    │   └── partial_styles: dict[str, PartialStyle]
    └── stamp_layers: list[StampLayer]
        └── effects: list[AnimationEffect]
```

---

## まとめ

Teto のデータモデルは以下の特徴を持ちます：

- ✅ **階層構造**: Script（抽象）→ Project（具体）の明確な分離
- ✅ **Pydantic ベース**: 型安全性とバリデーション
- ✅ **拡張性**: 新しいエフェクト、レイヤータイプを追加可能
- ✅ **柔軟性**: オプショナルフィールドでシンプルにも複雑にも対応
- ✅ **マルチ出力**: 複数のアスペクト比の動画を同時生成

これらのモデルにより、JSON での簡単な記述から Python API による詳細な制御まで、幅広いユースケースに対応できます。
