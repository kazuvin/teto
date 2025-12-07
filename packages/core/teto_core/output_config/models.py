"""Output configuration models"""

from pydantic import BaseModel, Field, model_validator
from typing import Literal
from enum import Enum


class VideoAspectRatio(str, Enum):
    """動画アスペクト比プリセット"""

    LANDSCAPE_16_9 = "16:9"  # YouTube横長（1920x1080）
    PORTRAIT_9_16 = "9:16"  # TikTok/Shorts縦長（1080x1920）
    SQUARE_1_1 = "1:1"  # Instagram正方形（1080x1080）
    STANDARD_4_3 = "4:3"  # 標準（1440x1080）
    WIDE_21_9 = "21:9"  # ウルトラワイド（2560x1080）


# アスペクト比から解像度へのマッピング
ASPECT_RATIO_RESOLUTIONS: dict[VideoAspectRatio, tuple[int, int]] = {
    VideoAspectRatio.LANDSCAPE_16_9: (1920, 1080),
    VideoAspectRatio.PORTRAIT_9_16: (1080, 1920),
    VideoAspectRatio.SQUARE_1_1: (1080, 1080),
    VideoAspectRatio.STANDARD_4_3: (1440, 1080),
    VideoAspectRatio.WIDE_21_9: (2560, 1080),
}


class OutputSettings(BaseModel):
    """出力設定（パスなし、Script用）"""

    name: str | None = Field(
        None,
        description="出力名（複数出力時のファイル名として使用、単一出力時は無視される）",
    )
    aspect_ratio: VideoAspectRatio | None = Field(
        None,
        description="アスペクト比プリセット（指定時はwidth/heightを上書き）",
    )
    width: int = Field(1920, description="出力幅", gt=0)
    height: int = Field(1080, description="出力高さ", gt=0)
    fps: int = Field(30, description="フレームレート", gt=0)
    codec: str = Field("libx264", description="ビデオコーデック")
    audio_codec: str = Field("aac", description="オーディオコーデック")
    bitrate: str | None = Field(None, description="ビットレート")
    preset: str = Field(
        "fast",
        description="エンコード速度プリセット（ultrafast/veryfast/fast/medium/slow）",
    )
    subtitle_mode: Literal["burn", "srt", "vtt", "none"] = Field(
        "burn", description="字幕モード"
    )

    @model_validator(mode="after")
    def apply_aspect_ratio(self) -> "OutputSettings":
        """aspect_ratioが指定されている場合、解像度を設定"""
        if self.aspect_ratio:
            w, h = ASPECT_RATIO_RESOLUTIONS[self.aspect_ratio]
            object.__setattr__(self, "width", w)
            object.__setattr__(self, "height", h)
        return self


class OutputConfig(BaseModel):
    """出力設定（パスあり、Project用）"""

    path: str = Field(..., description="出力ファイルパス")
    aspect_ratio: VideoAspectRatio | None = Field(
        None,
        description="アスペクト比プリセット（指定時はwidth/heightを上書き）",
    )
    width: int = Field(1920, description="出力幅", gt=0)
    height: int = Field(1080, description="出力高さ", gt=0)
    fps: int = Field(30, description="フレームレート", gt=0)
    codec: str = Field("libx264", description="ビデオコーデック")
    audio_codec: str = Field("aac", description="オーディオコーデック")
    bitrate: str | None = Field(None, description="ビットレート")
    preset: str = Field(
        "fast",
        description="エンコード速度プリセット（ultrafast/veryfast/fast/medium/slow）",
    )
    subtitle_mode: Literal["burn", "srt", "vtt", "none"] = Field(
        "burn", description="字幕モード"
    )

    @model_validator(mode="after")
    def apply_aspect_ratio(self) -> "OutputConfig":
        """aspect_ratioが指定されている場合、解像度を設定"""
        if self.aspect_ratio:
            w, h = ASPECT_RATIO_RESOLUTIONS[self.aspect_ratio]
            object.__setattr__(self, "width", w)
            object.__setattr__(self, "height", h)
        return self

    @classmethod
    def from_settings(cls, settings: OutputSettings, path: str) -> "OutputConfig":
        """OutputSettingsとパスからOutputConfigを作成"""
        return cls(
            path=path,
            aspect_ratio=settings.aspect_ratio,
            width=settings.width,
            height=settings.height,
            fps=settings.fps,
            codec=settings.codec,
            audio_codec=settings.audio_codec,
            bitrate=settings.bitrate,
            preset=settings.preset,
            subtitle_mode=settings.subtitle_mode,
        )
