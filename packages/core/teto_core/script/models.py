"""Script models - AIが生成しやすい抽象的な台本データ構造"""

from pydantic import BaseModel, Field, model_validator
from typing import Literal
from enum import Enum

from ..layer.models import PartialStyle
from ..output_config.models import OutputSettings
from .presets.base import SubtitleStyleConfig


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

    type: AssetType | None = Field(
        None, description="アセットタイプ（省略時は拡張子から自動判定）"
    )
    description: str | None = Field(
        None, description="映像の説明（将来のAI生成/検索用）"
    )
    path: str | None = Field(None, description="直接パス指定")

    # 動画ファイルの拡張子
    _VIDEO_EXTENSIONS: set[str] = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}

    @model_validator(mode="after")
    def validate_and_infer_type(self) -> "Visual":
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


class NarrationSegment(BaseModel):
    """ナレーションセグメント（字幕1つ分）

    1シーン内で複数の字幕を切り替えて表示する場合、
    複数の NarrationSegment を使用する。
    画面に表示できる字幕の文字数制限に合わせて分割する。
    """

    text: str = Field(..., description="字幕テキスト（1画面分）")
    pause_after: float = Field(0.0, description="このセグメント後の間隔（秒）", ge=0)


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

    # オプション
    note: str | None = Field(
        None, description="演出メモ（人間向け、処理には使用しない）"
    )
    preset: str | None = Field(
        None,
        description="このシーンに適用するプリセット名（未指定時はデフォルトプリセットを使用）",
    )

    @model_validator(mode="after")
    def validate_duration_for_no_narration(self) -> "Scene":
        # ナレーションなしの場合、duration は必須
        if len(self.narrations) == 0 and self.duration is None:
            raise ValueError("ナレーションがないシーンには duration を指定してください")
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


class VoiceConfig(BaseModel):
    """ナレーション音声設定"""

    provider: Literal["google", "openai", "voicevox", "elevenlabs"] = Field(
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


class Script(BaseModel):
    """台本（AI生成用の抽象データ構造）"""

    title: str = Field(..., description="動画タイトル")
    scenes: list[Scene] = Field(..., description="シーンのリスト", min_length=1)

    # グローバル設定
    voice: VoiceConfig = Field(default_factory=VoiceConfig, description="音声設定")
    timing: TimingConfig = Field(
        default_factory=TimingConfig, description="タイミング設定"
    )
    bgm: BGMConfig | None = Field(None, description="BGM設定")

    # 出力設定（解像度、FPS など）
    output: OutputSettings = Field(
        default_factory=OutputSettings, description="出力設定（解像度、FPSなど）"
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
    default_preset: str = Field(
        "default",
        description="シーンにプリセット指定がない場合に使用するデフォルトプリセット名",
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
