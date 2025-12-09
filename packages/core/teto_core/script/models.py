"""Script models - AIが生成しやすい抽象的な台本データ構造"""

from pydantic import BaseModel, Field, model_validator
from typing import Literal
from enum import Enum

from ..layer.models import PartialStyle
from ..output_config.models import OutputSettings
from ..effect.models import TransitionConfig
from .presets.base import SubtitleStyleConfig


# =============================================================================
# キャラクター関連モデル
# =============================================================================


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

    NONE = "none"  # アニメーションなし
    BOUNCE = "bounce"  # バウンド（上下に弾む）
    SHAKE = "shake"  # 揺れ（左右に小刻みに揺れる）
    NOD = "nod"  # 頷き（上下に小さく動く）
    SWAY = "sway"  # 揺らぎ（ゆっくり左右に揺れる）
    BREATHE = "breathe"  # 呼吸（拡大縮小）
    FLOAT = "float"  # 浮遊（上下にゆっくり動く）
    PULSE = "pulse"  # 脈動（リズミカルに拡大縮小）


class CharacterExpression(BaseModel):
    """キャラクターの表情定義"""

    name: str = Field(..., description="表情名（例: 'normal', 'smile', 'angry'）")
    path: str = Field(..., description="表情画像ファイルパス")


class CharacterAnimation(BaseModel):
    """キャラクターアニメーション設定"""

    type: CharacterAnimationType = Field(
        CharacterAnimationType.NONE, description="アニメーションタイプ"
    )
    intensity: float = Field(
        1.0, description="アニメーション強度（0.5〜2.0）", ge=0.5, le=2.0
    )
    speed: float = Field(
        1.0, description="アニメーション速度（0.5〜2.0）", ge=0.5, le=2.0
    )


class CharacterDefinition(BaseModel):
    """キャラクター定義（Script レベル）"""

    id: str = Field(..., description="キャラクター識別子（参照用）")
    name: str = Field(..., description="キャラクター名（表示・メタデータ用）")

    # 表情定義
    expressions: list[CharacterExpression] = Field(
        ..., description="表情リスト（最低1つの表情が必要）", min_length=1
    )
    default_expression: str = Field("normal", description="デフォルト表情名")

    # 配置設定
    position: CharacterPosition = Field(
        CharacterPosition.BOTTOM_RIGHT, description="デフォルト配置位置"
    )
    custom_position: tuple[int, int] | None = Field(
        None, description="カスタム位置（x, y）※position より優先"
    )

    # サイズ設定
    scale: float = Field(1.0, description="キャラクターサイズ倍率", gt=0, le=3.0)

    # デフォルトアニメーション
    default_animation: CharacterAnimation = Field(
        default_factory=CharacterAnimation, description="デフォルトアニメーション設定"
    )

    # 音声連携（オプショナル）
    voice_profile: str | None = Field(
        None,
        description="このキャラクターに紐づくボイスプロファイル名（Script.voice_profiles から参照）",
    )

    # 字幕スタイル（オプショナル）
    subtitle_style: SubtitleStyleConfig | None = Field(
        None,
        description="このキャラクター発話時の字幕スタイル（未指定時はグローバル設定を使用）",
    )

    @model_validator(mode="after")
    def validate_default_expression(self) -> "CharacterDefinition":
        """デフォルト表情が expressions に存在することを確認"""
        expression_names = {e.name for e in self.expressions}
        if self.default_expression not in expression_names:
            raise ValueError(
                f"default_expression '{self.default_expression}' が expressions に存在しません。"
                f"利用可能な表情: {expression_names}"
            )
        return self


class CharacterState(BaseModel):
    """セグメント内でのキャラクター状態"""

    character_id: str = Field(..., description="キャラクター ID")
    expression: str | None = Field(
        None, description="表情名（未指定時はデフォルト表情）"
    )
    animation: CharacterAnimation | None = Field(
        None, description="アニメーション設定（未指定時はデフォルトアニメーション）"
    )
    visible: bool = Field(True, description="表示/非表示")


class SceneCharacterConfig(BaseModel):
    """シーン単位のキャラクター設定"""

    character_id: str = Field(..., description="キャラクター ID")

    # シーン固有の上書き設定
    position: CharacterPosition | None = Field(
        None, description="このシーンでの配置位置（上書き）"
    )
    custom_position: tuple[int, int] | None = Field(
        None, description="このシーンでのカスタム位置（上書き）"
    )
    scale: float | None = Field(None, description="このシーンでのサイズ倍率（上書き）")
    visible: bool = Field(True, description="このシーンでの表示/非表示")


# =============================================================================
# アセット関連モデル
# =============================================================================


class AssetType(str, Enum):
    """アセットの種類"""

    VIDEO = "video"
    IMAGE = "image"


class ImageStylePreset(str, Enum):
    """Stability AI スタイルプリセット"""

    PHOTOGRAPHIC = "photographic"
    CINEMATIC = "cinematic"
    ANIME = "anime"
    DIGITAL_ART = "digital-art"
    COMIC_BOOK = "comic-book"
    FANTASY_ART = "fantasy-art"
    NEON_PUNK = "neon-punk"
    NONE = "none"


class ImageAspectRatio(str, Enum):
    """画像アスペクト比（SDXL 推奨サイズ）"""

    SQUARE = "1:1"  # 1024x1024
    LANDSCAPE = "16:9"  # 1344x768
    PORTRAIT = "9:16"  # 768x1344
    WIDE = "21:9"  # 1536x640
    STANDARD = "4:3"  # 1152x896


class StabilityImageConfig(BaseModel):
    """Stability AI 画像生成設定

    Discriminated Union パターンで他プロバイダーと区別。
    将来的に OpenAIImageConfig, GeminiImageConfig などを追加可能。
    """

    provider: Literal["stability"] = Field(
        "stability", description="プロバイダー識別子"
    )
    style_preset: ImageStylePreset = Field(
        ImageStylePreset.PHOTOGRAPHIC, description="スタイルプリセット"
    )
    aspect_ratio: ImageAspectRatio = Field(
        ImageAspectRatio.LANDSCAPE, description="アスペクト比"
    )
    negative_prompt: str | None = Field(None, description="除外したい要素")
    seed: int | None = Field(None, description="再現性のためのシード値")


# 将来的に他プロバイダーを追加する場合:
# ImageGenerationConfig = StabilityImageConfig | OpenAIImageConfig | GeminiImageConfig
ImageGenerationConfig = StabilityImageConfig


class Visual(BaseModel):
    """映像指定

    ローカルファイル指定:
        path を指定して既存のファイルを使用。

    AI画像生成:
        description（プロンプト）と generate（生成設定）を指定。
        generate が指定されている場合、description から画像を生成。

    将来対応予定:
    - AI 動画生成（Runway, Pika 等）
    - アセットライブラリからの自動選択
    """

    type: AssetType | None = Field(
        None, description="アセットタイプ（省略時は拡張子から自動判定）"
    )
    description: str | None = Field(
        None, description="映像の説明（AI生成時はプロンプトとして使用）"
    )
    path: str | None = Field(None, description="直接パス指定")
    generate: ImageGenerationConfig | None = Field(
        None, description="AI画像生成設定（指定時は description から画像生成）"
    )

    # 動画ファイルの拡張子
    _VIDEO_EXTENSIONS: set[str] = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}

    @model_validator(mode="after")
    def validate_and_infer_type(self) -> "Visual":
        # AI生成の場合は description が必須
        if self.generate is not None and self.description is None:
            raise ValueError("AI画像生成には description（プロンプト）が必須です")

        # path も description もない場合はエラー
        if self.path is None and self.description is None:
            raise ValueError("path または description のいずれかは必須です")

        # type が指定されていない場合、拡張子から自動判定
        if self.type is None and self.path:
            from pathlib import Path

            ext = Path(self.path).suffix.lower()
            if ext in self._VIDEO_EXTENSIONS:
                object.__setattr__(self, "type", AssetType.VIDEO)
            else:
                object.__setattr__(self, "type", AssetType.IMAGE)
        elif self.type is None:
            # path がなく description のみの場合はデフォルトで IMAGE
            object.__setattr__(self, "type", AssetType.IMAGE)

        return self


class SoundEffect(BaseModel):
    """効果音設定

    シーン内で再生する効果音を定義。
    複数の効果音を同時または連続で再生可能。
    """

    path: str = Field(..., description="効果音ファイルパス")
    offset: float = Field(0.0, description="シーン開始からのオフセット（秒）", ge=0)
    volume: float = Field(1.0, description="音量 (0.0〜1.0)", ge=0, le=1.0)


class NarrationSegment(BaseModel):
    """ナレーションセグメント（字幕1つ分）

    1シーン内で複数の字幕を切り替えて表示する場合、
    複数の NarrationSegment を使用する。
    画面に表示できる字幕の文字数制限に合わせて分割する。
    """

    text: str = Field(..., description="字幕テキスト（1画面分）")
    pause_after: float = Field(0.0, description="このセグメント後の間隔（秒）", ge=0)

    # 音声設定（セグメント固有）
    voice: "VoiceConfig | None" = Field(
        None,
        description="このセグメント専用のナレーション音声設定（指定時はグローバル設定を上書き）",
    )
    voice_profile: str | None = Field(
        None,
        description="使用するボイスプロファイル名（Script.voice_profiles から参照）",
    )

    # キャラクター状態
    character_states: list[CharacterState] = Field(
        default_factory=list,
        description="このセグメント中のキャラクター状態リスト",
    )

    @model_validator(mode="after")
    def validate_voice_config(self) -> "NarrationSegment":
        # voice と voice_profile の両方が指定されている場合はエラー
        if self.voice is not None and self.voice_profile is not None:
            raise ValueError("voice と voice_profile は同時に指定できません")
        return self


class Scene(BaseModel):
    """シーン（台本の基本単位）

    ナレーションありのシーン:
        narrations にセグメントを指定。duration は自動計算。

    ナレーションなしのシーン（タイトル、見出し、チャンネル登録など）:
        narrations を空リストまたは省略し、duration を明示的に指定。
    """

    narrations: list[NarrationSegment] = Field(
        default_factory=list,
        description="ナレーションセグメントのリスト（空の場合はナレーションなし）",
    )
    visual: Visual = Field(..., description="映像指定")

    duration: float | None = Field(
        None,
        description="シーンの長さ（秒）。ナレーションがある場合は自動計算されるため省略可。ナレーションなしの場合は必須。",
        gt=0,
    )
    pause_after: float = Field(0.0, description="このシーン後の間隔（秒）", ge=0)

    # トランジション設定
    transition: TransitionConfig | None = Field(
        None,
        description="このシーンへのトランジション設定（Noneの場合はカット）",
    )

    # 効果音
    sound_effects: list[SoundEffect] = Field(
        default_factory=list,
        description="効果音のリスト（シーン開始からのオフセットで再生タイミングを指定）",
    )

    # オプション
    note: str | None = Field(
        None, description="演出メモ（人間向け、処理には使用しない）"
    )
    preset: str | None = Field(
        None,
        description="このシーンに適用する複合プリセット名（未指定時はデフォルトプリセットを使用）",
    )
    effect: str | None = Field(
        None,
        description="このシーンに適用するエフェクト名（未指定時はデフォルトエフェクトを使用）",
    )
    mute_video: bool = Field(
        False,
        description="動画の音声をミュートにするか（True の場合、動画ファイルの音声を無音にする）",
    )

    # 音声設定（シーン固有）
    voice: "VoiceConfig | None" = Field(
        None,
        description="このシーン専用のナレーション音声設定（指定時はグローバル設定を上書き）",
    )
    voice_profile: str | None = Field(
        None,
        description="使用するボイスプロファイル名（Script.voice_profiles から参照）",
    )

    # キャラクター設定（リスト順が Z オーダー：後のキャラクターが前面）
    characters: list[SceneCharacterConfig] = Field(
        default_factory=list,
        description="このシーンで表示するキャラクターの設定",
    )

    @model_validator(mode="after")
    def validate_duration_for_no_narration(self) -> "Scene":
        # ナレーションなしの場合、duration は必須
        if len(self.narrations) == 0 and self.duration is None:
            raise ValueError("ナレーションがないシーンには duration を指定してください")
        return self

    @model_validator(mode="after")
    def validate_voice_config(self) -> "Scene":
        # voice と voice_profile の両方が指定されている場合はエラー
        if self.voice is not None and self.voice_profile is not None:
            raise ValueError("voice と voice_profile は同時に指定できません")
        return self


class TimingConfig(BaseModel):
    """タイミング設定"""

    default_segment_gap: float = Field(
        0.3, description="ナレーションセグメント間のデフォルト間隔（秒）", ge=0
    )
    default_scene_gap: float = Field(
        0.5, description="シーン間のデフォルト間隔（秒）", ge=0
    )
    subtitle_padding: float = Field(0.1, description="字幕の前後パディング（秒）", ge=0)


class BGMConfig(BaseModel):
    """BGM設定"""

    path: str = Field(..., description="BGMファイルパス")
    volume: float = Field(0.3, description="音量", ge=0, le=1)
    fade_in: float = Field(0.0, description="フェードイン時間（秒）", ge=0)
    fade_out: float = Field(0.0, description="フェードアウト時間（秒）", ge=0)


class BGMSceneRange(BaseModel):
    """シーン範囲"""

    model_config = {"populate_by_name": True}

    from_: int = Field(
        ..., alias="from", description="開始シーンインデックス（0始まり）", ge=0
    )
    to: int = Field(..., description="終了シーンインデックス（含む）", ge=0)

    @model_validator(mode="after")
    def validate_range(self) -> "BGMSceneRange":
        if self.to < self.from_:
            raise ValueError(
                f"'to' ({self.to}) は 'from' ({self.from_}) 以上である必要があります"
            )
        return self


class BGMSection(BaseModel):
    """シーン範囲BGMセクション

    複数のシーンにまたがってBGMを再生する設定。
    シーンA,B,Cで同じBGMを流し続けたい場合などに使用。
    """

    path: str = Field(..., description="BGMファイルパス")
    scene_range: BGMSceneRange = Field(..., description="適用するシーン範囲")
    volume: float = Field(0.3, description="音量 (0.0〜1.0)", ge=0, le=1.0)
    fade_in: float = Field(0.0, description="フェードイン時間（秒）", ge=0)
    fade_out: float = Field(0.0, description="フェードアウト時間（秒）", ge=0)
    loop: bool = Field(True, description="BGMをループ再生するか")


class VoiceConfig(BaseModel):
    """ナレーション音声設定"""

    provider: Literal["google", "openai", "voicevox", "elevenlabs", "gemini"] = Field(
        "google", description="TTSプロバイダー"
    )
    voice_id: str | None = Field(None, description="声の指定（プロバイダー依存）")
    language_code: str = Field("ja-JP", description="言語コード")
    speed: float = Field(1.0, description="話速", ge=0.5, le=2.0)
    pitch: float = Field(0.0, description="ピッチ", ge=-20, le=20)

    # ElevenLabs 固有設定
    model_id: str = Field("eleven_multilingual_v2", description="ElevenLabsモデルID")
    output_format: str = Field(
        "mp3_44100_128", description="ElevenLabs出力フォーマット"
    )

    # Gemini 固有設定
    voice_name: str = Field("Kore", description="Gemini音声名")
    gemini_model_id: str = Field(
        "gemini-2.5-flash-preview-tts", description="GeminiモデルID"
    )
    style_prompt: str | None = Field(
        None, description="Gemini音声スタイルの指示プロンプト"
    )


class Script(BaseModel):
    """台本（AI生成用の抽象データ構造）"""

    title: str = Field(..., description="動画タイトル")
    scenes: list[Scene] = Field(..., description="シーンのリスト", min_length=1)

    # グローバル設定
    voice: VoiceConfig = Field(default_factory=VoiceConfig, description="音声設定")
    voice_profiles: dict[str, VoiceConfig] | None = Field(
        None,
        description="名前付きボイスプロファイル（シーンから名前で参照可能）",
    )
    timing: TimingConfig = Field(
        default_factory=TimingConfig, description="タイミング設定"
    )
    bgm: BGMConfig | None = Field(
        None, description="グローバルBGM設定（全体で1つ、後方互換性のため維持）"
    )
    bgm_sections: list[BGMSection] = Field(
        default_factory=list,
        description="シーン範囲BGM（複数のBGMをシーン範囲で切り替え）",
    )
    image_generation: ImageGenerationConfig = Field(
        default_factory=StabilityImageConfig,
        description="AI画像生成のデフォルト設定",
    )

    # キャラクター定義
    characters: dict[str, CharacterDefinition] | None = Field(
        None,
        description="キャラクター定義（ID をキーとした辞書）",
    )

    # 出力設定（解像度、FPS など）
    # 単一出力: OutputSettings オブジェクト
    # 複数出力: OutputSettings のリスト（各要素に name フィールドを指定）
    output: OutputSettings | list[OutputSettings] = Field(
        default_factory=OutputSettings,
        description="出力設定（単一出力: オブジェクト、複数出力: 配列）",
    )

    # 出力ディレクトリ
    output_dir: str | None = Field(
        None,
        description="出力ディレクトリ（指定時は全ての出力をこのディレクトリに配置、未指定時はデフォルトまたはCLIの設定を使用）",
    )

    # 字幕スタイル設定
    subtitle_style: SubtitleStyleConfig = Field(
        default_factory=SubtitleStyleConfig, description="字幕スタイル設定"
    )

    # 部分スタイル（マークアップ）設定
    subtitle_styles: dict[str, PartialStyle] = Field(
        default_factory=dict,
        description="部分スタイル定義（マークアップタグ名とスタイルのマッピング）",
    )

    # プリセット設定
    default_preset: str | None = Field(
        None,
        description="シーンに複合プリセット指定がない場合に使用するデフォルト複合プリセット名",
    )
    default_effect: str = Field(
        "default",
        description="シーンにエフェクト指定がない場合に使用するデフォルトエフェクト名",
    )

    # メタデータ
    description: str | None = Field(None, description="動画の説明")

    @classmethod
    def from_json_file(cls, path: str) -> "Script":
        """JSONファイルからScriptを読み込む"""
        import json
        from pathlib import Path

        with Path(path).open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.model_validate(data)

    def to_json_file(self, path: str) -> None:
        """ScriptをJSONファイルに保存する"""
        import json
        from pathlib import Path

        with Path(path).open("w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, ensure_ascii=False, indent=2)
