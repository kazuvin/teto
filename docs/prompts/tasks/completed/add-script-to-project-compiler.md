# Script → Project 変換機能

## 概要
AIが生成しやすい抽象的な「台本（Script）」データ構造と、それを動画生成用の「Project」に変換する仕組みを実装する。

## 背景
現状の `Project` データ構造は動画編集ツール向けで、AIが台本から直接生成するには詳細すぎる。中間層として `Script` モデルを導入し、AIの生成負担を軽減しつつ、柔軟な動画生成を可能にする。

## 目標
- AIが生成しやすい `Script` モデルの定義
- `Script` → `Project` への変換ロジック（`ScriptCompiler`）の実装
- レイヤー設定（エフェクト、フォント等）のプリセット化
- 拡張可能なアーキテクチャ

---

## アーキテクチャ

### 全体フロー

```
┌──────────────┐     ┌─────────────────┐     ┌─────────────┐     ┌─────────────┐
│  AI / User   │────▶│     Script      │────▶│  Compiler   │────▶│   Project   │
│  (台本生成)   │     │  (抽象データ)    │     │   (変換)     │     │ (具体データ) │
└──────────────┘     └─────────────────┘     └──────┬──────┘     └─────────────┘
                                                    │
                           ┌────────────────────────┼────────────────────────┐
                           │                        │                        │
                           ▼                        ▼                        ▼
                    ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
                    │ TTSProvider │          │AssetResolver│          │LayerPreset  │
                    │ (音声生成)   │          │ (素材解決)   │          │(レイヤー設定)│
                    └─────────────┘          └─────────────┘          └─────────────┘
```

### 採用するデザインパターン

#### 1. Strategy パターン（必須）
**用途**: TTSProvider, AssetResolver, LayerPreset の差し替え

```python
# 抽象インターフェース
class TTSProvider(ABC):
    @abstractmethod
    def generate(self, text: str, config: VoiceConfig) -> TTSResult: ...

class AssetResolver(ABC):
    @abstractmethod
    def resolve(self, visual: Visual) -> str: ...

class LayerPreset(ABC):
    @abstractmethod
    def get_output_config(self) -> OutputConfig: ...
    @abstractmethod
    def get_subtitle_style(self) -> SubtitleStyleConfig: ...
    @abstractmethod
    def get_video_effects(self) -> list[AnimationEffect]: ...
    @abstractmethod
    def get_transition(self) -> TransitionConfig | None: ...

# 具体実装を差し替え可能
compiler = ScriptCompiler(
    tts_provider=GoogleTTSProvider(),
    asset_resolver=LocalAssetResolver(),
    layer_preset=DefaultLayerPreset(),  # レイヤー設定のプリセット
)
```

**メリット**:
- TTS プロバイダーの切り替え（Google, OpenAI, VOICEVOX など）
- アセット解決方法の切り替え（ローカル検索, AI生成 など）
- レイヤー設定の切り替え（エフェクト、フォント、トランジション）

#### 2. Builder パターン（推奨）
**用途**: Script の構築、Project の組み立て

```python
script = (
    ScriptBuilder()
    .title("製品紹介動画")
    .add_scene(
        SceneBuilder()
        .add_narration("こんにちは")
        .add_narration("今日は新製品を紹介します")
        .visual_path("./assets/intro.png")
        .build()
    )
    .scene_gap(0.5)  # シーン間の間隔
    .build()
)
```

**メリット**: 複雑なオブジェクトを段階的に構築、バリデーション組み込み

#### 3. Template Method パターン（推奨）
**用途**: コンパイル処理の基本フロー定義

```python
class ScriptCompiler(ABC):
    def compile(self, script: Script) -> Project:
        """テンプレートメソッド: コンパイルの基本フロー"""
        self._prepare(script)
        narrations = self._generate_narrations(script)
        timings = self._calculate_timings(script, narrations)
        project = self._build_project(script, timings, narrations)
        return self._postprocess(project)

    @abstractmethod
    def _process_scene(self, scene: Scene) -> list[BaseLayer]: ...
```

**メリット**: 基本フローを固定しつつ、詳細をサブクラスで変更可能

#### 4. Factory パターン（オプション）
**用途**: レイヤーの生成

```python
class LayerFactory:
    def create_video_layer(self, path: str, duration: float, preset: LayerPreset) -> VideoLayer: ...
    def create_subtitle_layer(self, items: list[SubtitleItem], preset: LayerPreset) -> SubtitleLayer: ...
```

**メリット**: レイヤー生成ロジックの集約、プリセット適用の一元化

#### 5. Adapter パターン（オプション）
**用途**: 外部サービス（TTS, 画像生成API）の統一インターフェース化

```python
class VOICEVOXAdapter(TTSProvider):
    def __init__(self, voicevox_client: VOICEVOXClient):
        self._client = voicevox_client

    def generate(self, text: str, config: VoiceConfig) -> TTSResult:
        # VOICEVOX 固有の API を TTSProvider インターフェースに変換
        ...
```

---

## データモデル設計

### Script（台本）

```python
from pydantic import BaseModel, Field
from typing import Literal
from enum import Enum


class AssetType(str, Enum):
    """アセットの種類"""
    VIDEO = "video"
    IMAGE = "image"


class Visual(BaseModel):
    """映像指定

    NOTE: 将来的にはAI画像/動画生成と連携予定。
    現時点では path を直接指定するか、description を使った
    ローカルアセット検索のみサポート。

    将来対応予定:
    - description からの AI 画像生成（DALL-E, Stable Diffusion 等）
    - description からの AI 動画生成（Runway, Pika 等）
    - アセットライブラリからの自動選択
    """
    type: AssetType = Field(AssetType.IMAGE, description="アセットタイプ")
    description: str | None = Field(
        None,
        description="映像の説明（将来のAI生成/検索用）"
    )
    path: str | None = Field(None, description="直接パス指定")

    def model_post_init(self, __context) -> None:
        if self.path is None and self.description is None:
            raise ValueError("path または description のいずれかは必須です")


class NarrationSegment(BaseModel):
    """ナレーションセグメント（字幕1つ分）

    1シーン内で複数の字幕を切り替えて表示する場合、
    複数の NarrationSegment を使用する。
    画面に表示できる字幕の文字数制限に合わせて分割する。
    """
    text: str = Field(..., description="字幕テキスト（1画面分）")
    pause_after: float = Field(
        0.0,
        description="このセグメント後の間隔（秒）",
        ge=0
    )


class Scene(BaseModel):
    """シーン（台本の基本単位）

    ナレーションありのシーン:
        narrations にセグメントを指定。duration は自動計算。

    ナレーションなしのシーン（タイトル、見出し、チャンネル登録など）:
        narrations を空リストまたは省略し、duration を明示的に指定。
    """

    narrations: list[NarrationSegment] = Field(
        default_factory=list,
        description="ナレーションセグメントのリスト（空の場合はナレーションなし）"
    )
    visual: Visual = Field(..., description="映像指定")

    duration: float | None = Field(
        None,
        description="シーンの長さ（秒）。ナレーションがある場合は自動計算されるため省略可。ナレーションなしの場合は必須。",
        gt=0
    )
    pause_after: float = Field(
        0.0,
        description="このシーン後の間隔（秒）",
        ge=0
    )

    # オプション
    note: str | None = Field(None, description="演出メモ（人間向け、処理には使用しない）")

    def model_post_init(self, __context) -> None:
        # ナレーションなしの場合、duration は必須
        if len(self.narrations) == 0 and self.duration is None:
            raise ValueError(
                "ナレーションがないシーンには duration を指定してください"
            )


class TimingConfig(BaseModel):
    """タイミング設定"""
    default_segment_gap: float = Field(
        0.3,
        description="ナレーションセグメント間のデフォルト間隔（秒）",
        ge=0
    )
    default_scene_gap: float = Field(
        0.5,
        description="シーン間のデフォルト間隔（秒）",
        ge=0
    )
    subtitle_padding: float = Field(
        0.1,
        description="字幕の前後パディング（秒）",
        ge=0
    )


class BGMConfig(BaseModel):
    """BGM設定"""
    path: str = Field(..., description="BGMファイルパス")
    volume: float = Field(0.3, description="音量", ge=0, le=1)
    fade_in: float = Field(0.0, description="フェードイン時間（秒）", ge=0)
    fade_out: float = Field(0.0, description="フェードアウト時間（秒）", ge=0)


class VoiceConfig(BaseModel):
    """ナレーション音声設定"""
    provider: Literal["google", "openai", "voicevox"] = Field(
        "google", description="TTSプロバイダー"
    )
    voice_id: str | None = Field(None, description="声の指定（プロバイダー依存）")
    language_code: str = Field("ja-JP", description="言語コード")
    speed: float = Field(1.0, description="話速", ge=0.5, le=2.0)
    pitch: float = Field(0.0, description="ピッチ", ge=-20, le=20)


class Script(BaseModel):
    """台本（AI生成用の抽象データ構造）"""

    title: str = Field(..., description="動画タイトル")
    scenes: list[Scene] = Field(..., description="シーンのリスト", min_length=1)

    # グローバル設定
    voice: VoiceConfig = Field(
        default_factory=VoiceConfig, description="音声設定"
    )
    timing: TimingConfig = Field(
        default_factory=TimingConfig, description="タイミング設定"
    )
    bgm: BGMConfig | None = Field(None, description="BGM設定")

    # メタデータ
    description: str | None = Field(None, description="動画の説明")
```

### AI生成例（こういうJSONをAIに出力させる）

```json
{
  "title": "Python入門講座 第1回",
  "description": "プログラミング初心者向けのPython入門",
  "scenes": [
    {
      "narrations": [],
      "visual": { "path": "./assets/title_card.png" },
      "duration": 3.0,
      "note": "タイトル画面（ナレーションなし）"
    },
    {
      "narrations": [
        { "text": "こんにちは！" },
        { "text": "今日からPythonを学んでいきましょう。", "pause_after": 0.5 }
      ],
      "visual": { "path": "./assets/intro.png" }
    },
    {
      "narrations": [
        { "text": "Pythonは、シンプルで読みやすい" },
        { "text": "文法が特徴のプログラミング言語です。" }
      ],
      "visual": {
        "type": "image",
        "path": "./assets/python_logo.png",
        "description": "Pythonのロゴと特徴を示す図"
      },
      "pause_after": 0.3
    },
    {
      "narrations": [],
      "visual": { "path": "./assets/chapter1_heading.png" },
      "duration": 2.0,
      "note": "Chapter 1 見出し"
    },
    {
      "narrations": [
        { "text": "まずは、Hello Worldを" },
        { "text": "表示するプログラムを書いてみましょう。" }
      ],
      "visual": { "path": "./assets/code_editor.png" }
    },
    {
      "narrations": [],
      "visual": { "path": "./assets/subscribe_animation.mp4" },
      "duration": 4.0,
      "note": "チャンネル登録・高評価のお願い（ナレーションなし）"
    }
  ],
  "voice": {
    "provider": "google",
    "language_code": "ja-JP",
    "speed": 1.0
  },
  "timing": {
    "default_segment_gap": 0.3,
    "default_scene_gap": 0.5
  },
  "bgm": {
    "path": "./assets/bgm/cheerful.mp3",
    "volume": 0.2,
    "fade_in": 1.0,
    "fade_out": 2.0
  }
}
```

---

## LayerPreset（レイヤー設定プリセット）

### 概要

`LayerPreset` は Project のレイヤー設定（エフェクト、フォント、トランジションなど）を定型化したもの。
プラットフォーム（YouTube, TikTok）ではなく、**見た目のスタイル**をカプセル化する。

### インターフェース

```python
from abc import ABC, abstractmethod


class SubtitleStyleConfig(BaseModel):
    """字幕スタイル設定"""
    font_size: int | str = "base"
    font_color: str = "white"
    google_font: str | None = "Noto Sans JP"
    font_weight: Literal["normal", "bold"] = "normal"
    stroke_width: int | str = 0
    stroke_color: str = "black"
    bg_color: str | None = "black@0.5"
    position: Literal["bottom", "top", "center"] = "bottom"
    appearance: Literal["plain", "background", "shadow", "drop-shadow"] = "background"


class LayerPreset(ABC):
    """レイヤー設定プリセット（Strategy）

    動画のレイヤー設定（エフェクト、フォント、トランジション）を
    定型化するインターフェース。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """プリセット名"""
        ...

    @abstractmethod
    def get_output_config(self) -> OutputConfig:
        """出力設定を取得"""
        ...

    @abstractmethod
    def get_subtitle_style(self) -> SubtitleStyleConfig:
        """字幕スタイル設定を取得"""
        ...

    @abstractmethod
    def get_image_effects(self) -> list[AnimationEffect]:
        """画像レイヤーに適用するエフェクトを取得"""
        ...

    @abstractmethod
    def get_video_effects(self) -> list[AnimationEffect]:
        """動画レイヤーに適用するエフェクトを取得"""
        ...

    @abstractmethod
    def get_transition(self) -> TransitionConfig | None:
        """トランジション設定を取得"""
        ...
```

### 実装例

```python
class DefaultLayerPreset(LayerPreset):
    """デフォルトプリセット（シンプルな設定）"""

    @property
    def name(self) -> str:
        return "default"

    def get_output_config(self) -> OutputConfig:
        return OutputConfig(
            width=1920,
            height=1080,
            fps=30,
            codec="libx264",
        )

    def get_subtitle_style(self) -> SubtitleStyleConfig:
        return SubtitleStyleConfig(
            font_size="lg",
            font_color="white",
            google_font="Noto Sans JP",
            stroke_width="sm",
            stroke_color="black",
            appearance="shadow",
            position="bottom",
        )

    def get_image_effects(self) -> list[AnimationEffect]:
        # 画像には軽い Ken Burns エフェクト
        return [AnimationEffect(type="kenBurns", config={"scale": 1.05})]

    def get_video_effects(self) -> list[AnimationEffect]:
        return []

    def get_transition(self) -> TransitionConfig | None:
        return TransitionConfig(type="crossfade", duration=0.5)


class BoldSubtitlePreset(LayerPreset):
    """太字字幕プリセット（目立つ字幕）"""

    @property
    def name(self) -> str:
        return "bold_subtitle"

    def get_output_config(self) -> OutputConfig:
        return OutputConfig(width=1920, height=1080, fps=30)

    def get_subtitle_style(self) -> SubtitleStyleConfig:
        return SubtitleStyleConfig(
            font_size="xl",
            font_color="yellow",
            google_font="Noto Sans JP",
            font_weight="bold",
            stroke_width="base",
            stroke_color="black",
            appearance="drop-shadow",
            position="center",
        )

    def get_image_effects(self) -> list[AnimationEffect]:
        return [AnimationEffect(type="zoom", config={"scale": 1.1})]

    def get_video_effects(self) -> list[AnimationEffect]:
        return []

    def get_transition(self) -> TransitionConfig | None:
        return TransitionConfig(type="slide_left", duration=0.3)


class MinimalPreset(LayerPreset):
    """ミニマルプリセット（シンプル、エフェクトなし）"""

    @property
    def name(self) -> str:
        return "minimal"

    def get_output_config(self) -> OutputConfig:
        return OutputConfig(width=1920, height=1080, fps=30)

    def get_subtitle_style(self) -> SubtitleStyleConfig:
        return SubtitleStyleConfig(
            font_size="base",
            font_color="white",
            google_font="Noto Sans JP",
            appearance="plain",
            position="bottom",
        )

    def get_image_effects(self) -> list[AnimationEffect]:
        return []  # エフェクトなし

    def get_video_effects(self) -> list[AnimationEffect]:
        return []

    def get_transition(self) -> TransitionConfig | None:
        return None  # カット（トランジションなし）


class VerticalPreset(LayerPreset):
    """縦型動画プリセット（9:16）"""

    @property
    def name(self) -> str:
        return "vertical"

    def get_output_config(self) -> OutputConfig:
        return OutputConfig(width=1080, height=1920, fps=30)

    def get_subtitle_style(self) -> SubtitleStyleConfig:
        return SubtitleStyleConfig(
            font_size="xl",
            font_color="white",
            google_font="Noto Sans JP",
            font_weight="bold",
            stroke_width="base",
            stroke_color="black",
            appearance="background",
            position="center",
        )

    def get_image_effects(self) -> list[AnimationEffect]:
        return [AnimationEffect(type="kenBurns", config={"scale": 1.1})]

    def get_video_effects(self) -> list[AnimationEffect]:
        return []

    def get_transition(self) -> TransitionConfig | None:
        return TransitionConfig(type="crossfade", duration=0.3)
```

### プリセットレジストリ

```python
class LayerPresetRegistry:
    """プリセット管理"""

    _presets: dict[str, LayerPreset] = {}

    @classmethod
    def register(cls, preset: LayerPreset) -> None:
        cls._presets[preset.name] = preset

    @classmethod
    def get(cls, name: str) -> LayerPreset:
        if name not in cls._presets:
            raise ValueError(f"Unknown preset: {name}")
        return cls._presets[name]

    @classmethod
    def list_names(cls) -> list[str]:
        return list(cls._presets.keys())


# 初期登録
LayerPresetRegistry.register(DefaultLayerPreset())
LayerPresetRegistry.register(BoldSubtitlePreset())
LayerPresetRegistry.register(MinimalPreset())
LayerPresetRegistry.register(VerticalPreset())
```

---

## ScriptCompiler 設計

### インターフェース

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SegmentTiming:
    """セグメントのタイミング情報"""
    segment_index: int
    start_time: float
    end_time: float
    narration_path: str
    text: str


@dataclass
class SceneTiming:
    """シーンのタイミング情報"""
    scene_index: int
    start_time: float
    end_time: float
    segments: list[SegmentTiming]


@dataclass
class CompileMetadata:
    """コンパイルメタデータ"""
    total_duration: float
    scene_timings: list[SceneTiming]
    generated_assets: list[str]


@dataclass
class CompileResult:
    """コンパイル結果"""
    project: Project
    metadata: CompileMetadata


class TTSProvider(ABC):
    """TTS プロバイダーインターフェース（Strategy）"""

    @abstractmethod
    def generate(self, text: str, config: VoiceConfig) -> TTSResult: ...

    @abstractmethod
    def estimate_duration(self, text: str, config: VoiceConfig) -> float: ...


class AssetResolver(ABC):
    """アセット解決インターフェース（Strategy）

    NOTE: 将来的にはAI画像/動画生成プロバイダーとの連携を想定。
    現時点では LocalAssetResolver（パス直接指定）のみ実装。

    将来対応予定:
    - AIImageGeneratorResolver: description から画像を生成
    - AIVideoGeneratorResolver: description から動画を生成
    - AssetLibraryResolver: アセットライブラリから検索・選択
    """

    @abstractmethod
    def resolve(self, visual: Visual) -> str:
        """Visual指定からファイルパスを解決"""
        ...


class LocalAssetResolver(AssetResolver):
    """ローカルアセット解決（パス直接使用）"""

    def resolve(self, visual: Visual) -> str:
        if visual.path:
            return visual.path
        raise ValueError(
            f"LocalAssetResolver requires path. "
            f"description='{visual.description}' からの解決は未対応です。"
        )
```

### ScriptCompiler 実装

```python
class ScriptCompiler:
    """Script → Project 変換（Template Method + Strategy）"""

    def __init__(
        self,
        tts_provider: TTSProvider,
        asset_resolver: AssetResolver,
        layer_preset: LayerPreset,
        output_dir: str = "./output",
    ):
        self._tts = tts_provider
        self._assets = asset_resolver
        self._preset = layer_preset
        self._output_dir = output_dir

    def compile(self, script: Script) -> CompileResult:
        """メインのコンパイル処理（Template Method）"""

        # 1. 準備
        self._prepare(script)

        # 2. 全セグメントのナレーション音声を生成
        narrations = self._generate_all_narrations(script)

        # 3. タイムラインを計算（間隔を考慮）
        scene_timings = self._calculate_timings(script, narrations)

        # 4. 各レイヤーを生成
        video_layers = self._build_video_layers(script, scene_timings)
        audio_layers = self._build_audio_layers(script, scene_timings)
        subtitle_layers = self._build_subtitle_layers(script, scene_timings)

        # 5. Project を組み立て
        project = self._assemble_project(
            video_layers, audio_layers, subtitle_layers
        )

        # 6. メタデータ作成
        metadata = self._create_metadata(scene_timings, narrations)

        return CompileResult(project=project, metadata=metadata)

    def _prepare(self, script: Script) -> None:
        """前処理"""
        import os
        os.makedirs(self._output_dir, exist_ok=True)
        os.makedirs(f"{self._output_dir}/narrations", exist_ok=True)

    def _generate_all_narrations(
        self, script: Script
    ) -> list[list[TTSResult]]:
        """全シーン・全セグメントのナレーションを生成"""
        all_narrations = []

        for scene_idx, scene in enumerate(script.scenes):
            scene_narrations = []
            for seg_idx, segment in enumerate(scene.narrations):
                result = self._tts.generate(
                    text=segment.text,
                    config=script.voice,
                )
                # 音声ファイルを保存
                output_path = (
                    f"{self._output_dir}/narrations/"
                    f"scene_{scene_idx:03d}_seg_{seg_idx:03d}.mp3"
                )
                result.save(output_path)
                result.path = output_path
                scene_narrations.append(result)
            all_narrations.append(scene_narrations)

        return all_narrations

    def _calculate_timings(
        self,
        script: Script,
        all_narrations: list[list[TTSResult]],
    ) -> list[SceneTiming]:
        """タイミングを計算（間隔を考慮）"""
        scene_timings = []
        current_time = 0.0
        timing_config = script.timing

        for scene_idx, (scene, scene_narrations) in enumerate(
            zip(script.scenes, all_narrations)
        ):
            scene_start = current_time
            segment_timings = []

            if len(scene.narrations) == 0:
                # ナレーションなしのシーン（タイトル、見出し等）
                # duration は Scene のバリデーションで必須チェック済み
                scene_end = current_time + scene.duration
                current_time = scene_end
            else:
                # ナレーションありのシーン
                for seg_idx, (segment, narration) in enumerate(
                    zip(scene.narrations, scene_narrations)
                ):
                    seg_start = current_time
                    seg_end = current_time + narration.duration

                    segment_timings.append(SegmentTiming(
                        segment_index=seg_idx,
                        start_time=seg_start,
                        end_time=seg_end,
                        narration_path=narration.path,
                        text=segment.text,
                    ))

                    current_time = seg_end

                    # セグメント後の間隔を追加
                    gap = segment.pause_after
                    if gap == 0 and seg_idx < len(scene.narrations) - 1:
                        # 明示的な指定がなければデフォルト間隔を使用
                        gap = timing_config.default_segment_gap
                    current_time += gap

                scene_end = current_time

            scene_timings.append(SceneTiming(
                scene_index=scene_idx,
                start_time=scene_start,
                end_time=scene_end,
                segments=segment_timings,  # ナレーションなしの場合は空リスト
            ))

            # シーン後の間隔を追加
            scene_gap = scene.pause_after
            if scene_gap == 0 and scene_idx < len(script.scenes) - 1:
                scene_gap = timing_config.default_scene_gap
            current_time += scene_gap

        return scene_timings

    def _build_video_layers(
        self,
        script: Script,
        scene_timings: list[SceneTiming],
    ) -> list[VideoLayer | ImageLayer]:
        """映像レイヤーを構築"""
        layers = []

        for scene, timing in zip(script.scenes, scene_timings):
            asset_path = self._assets.resolve(scene.visual)
            duration = timing.end_time - timing.start_time

            if scene.visual.type == AssetType.VIDEO:
                effects = self._preset.get_video_effects()
                layer = VideoLayer(
                    path=asset_path,
                    duration=duration,
                    effects=effects,
                    transition=self._preset.get_transition(),
                )
            else:
                effects = self._preset.get_image_effects()
                layer = ImageLayer(
                    path=asset_path,
                    duration=duration,
                    effects=effects,
                    transition=self._preset.get_transition(),
                )

            layers.append(layer)

        return layers

    def _build_audio_layers(
        self,
        script: Script,
        scene_timings: list[SceneTiming],
    ) -> list[AudioLayer]:
        """音声レイヤーを構築"""
        layers = []

        # ナレーション音声
        for scene_timing in scene_timings:
            for segment in scene_timing.segments:
                layers.append(AudioLayer(
                    path=segment.narration_path,
                    start_time=segment.start_time,
                    volume=1.0,
                ))

        # BGM
        if script.bgm:
            total_duration = scene_timings[-1].end_time
            layers.append(AudioLayer(
                path=script.bgm.path,
                start_time=0.0,
                duration=total_duration,
                volume=script.bgm.volume,
                # NOTE: fade_in/fade_out は AudioLayer 拡張後に対応
            ))

        return layers

    def _build_subtitle_layers(
        self,
        script: Script,
        scene_timings: list[SceneTiming],
    ) -> list[SubtitleLayer]:
        """字幕レイヤーを構築"""
        items = []
        padding = script.timing.subtitle_padding

        for scene_timing in scene_timings:
            for segment in scene_timing.segments:
                items.append(SubtitleItem(
                    text=segment.text,
                    start_time=segment.start_time + padding,
                    end_time=segment.end_time - padding,
                ))

        style = self._preset.get_subtitle_style()

        return [SubtitleLayer(
            items=items,
            font_size=style.font_size,
            font_color=style.font_color,
            google_font=style.google_font,
            font_weight=style.font_weight,
            stroke_width=style.stroke_width,
            stroke_color=style.stroke_color,
            bg_color=style.bg_color,
            position=style.position,
            appearance=style.appearance,
        )]

    def _assemble_project(
        self,
        video_layers: list,
        audio_layers: list,
        subtitle_layers: list,
    ) -> Project:
        """Project を組み立て"""
        return Project(
            output=self._preset.get_output_config(),
            timeline=Timeline(
                video_layers=video_layers,
                audio_layers=audio_layers,
                subtitle_layers=subtitle_layers,
            ),
        )

    def _create_metadata(
        self,
        scene_timings: list[SceneTiming],
        all_narrations: list[list[TTSResult]],
    ) -> CompileMetadata:
        """メタデータを作成"""
        generated = []
        for scene_narrations in all_narrations:
            for narration in scene_narrations:
                generated.append(narration.path)

        return CompileMetadata(
            total_duration=scene_timings[-1].end_time,
            scene_timings=scene_timings,
            generated_assets=generated,
        )
```

---

## ディレクトリ構成

```
packages/core/teto_core/
├── script/                      # 新規: Script ドメイン
│   ├── __init__.py
│   ├── models.py               # Script, Scene, NarrationSegment, Visual など
│   ├── compiler.py             # ScriptCompiler
│   ├── builders.py             # ScriptBuilder, SceneBuilder（オプション）
│   │
│   ├── providers/              # Strategy 実装
│   │   ├── __init__.py
│   │   ├── tts.py              # TTSProvider ABC + 実装
│   │   └── assets.py           # AssetResolver ABC + 実装
│   │
│   └── presets/                # LayerPreset 実装
│       ├── __init__.py
│       ├── base.py             # LayerPreset ABC, SubtitleStyleConfig
│       ├── registry.py         # LayerPresetRegistry
│       ├── default.py          # DefaultLayerPreset
│       ├── bold_subtitle.py    # BoldSubtitlePreset
│       ├── minimal.py          # MinimalPreset
│       └── vertical.py         # VerticalPreset
```

---

## タスク詳細

### Phase 1: 基盤モデルの実装
- [ ] `script/models.py` - Script, Scene, NarrationSegment, Visual, TimingConfig などのモデル定義
- [ ] `script/__init__.py` - 公開API設定

### Phase 2: インターフェースの定義
- [ ] `script/providers/tts.py` - TTSProvider ABC
- [ ] `script/providers/assets.py` - AssetResolver ABC + LocalAssetResolver
- [ ] `script/presets/base.py` - LayerPreset ABC, SubtitleStyleConfig

### Phase 3: ScriptCompiler の実装
- [ ] `script/compiler.py` - ScriptCompiler クラス
- [ ] ナレーション生成ロジック（セグメント単位）
- [ ] タイミング計算ロジック（間隔考慮）
- [ ] レイヤー構築ロジック

### Phase 4: Strategy 実装
- [ ] `script/providers/tts.py` - GoogleTTSProvider（既存TTSを活用）
- [ ] `script/presets/default.py` - DefaultLayerPreset
- [ ] `script/presets/registry.py` - LayerPresetRegistry

### Phase 5: 追加プリセット（オプション）
- [ ] `script/presets/bold_subtitle.py`
- [ ] `script/presets/minimal.py`
- [ ] `script/presets/vertical.py`

### Phase 6: Builder の実装（オプション）
- [ ] `script/builders.py` - ScriptBuilder, SceneBuilder

### Phase 7: テストと動作確認
- [ ] ユニットテスト作成
- [ ] サンプル Script での動作確認

---

## 確認事項
- [ ] 既存の Project, VideoGenerator との互換性
- [ ] 既存の TTS 機能との統合
- [ ] Script の JSON シリアライズ/デシリアライズ
- [ ] エラーハンドリング（アセット未発見、TTS失敗など）
- [ ] 字幕の文字数が多すぎる場合の警告/エラー

---

## 使用例

```python
from teto_core.script import Script, ScriptCompiler
from teto_core.script.providers import GoogleTTSProvider, LocalAssetResolver
from teto_core.script.presets import DefaultLayerPreset, LayerPresetRegistry
from teto_core import VideoGenerator

# 1. Script を作成（AIが生成 or 手動）
script = Script.from_json_file("script.json")

# 2. Compiler を設定
compiler = ScriptCompiler(
    tts_provider=GoogleTTSProvider(),
    asset_resolver=LocalAssetResolver(),
    layer_preset=DefaultLayerPreset(),  # または LayerPresetRegistry.get("bold_subtitle")
)

# 3. Script → Project に変換
result = compiler.compile(script)
print(f"Total duration: {result.metadata.total_duration}s")

# 4. 動画生成
generator = VideoGenerator(result.project)
generator.generate()
```

---

> **Note**: すべてのタスクが完了したら、このファイルを `tasks/completed/` ディレクトリに移動してください。
