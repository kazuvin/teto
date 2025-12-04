"""Output configuration models"""

from pydantic import BaseModel, Field
from typing import Literal


class OutputSettings(BaseModel):
    """出力設定（パスなし、Script用）"""

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


class OutputConfig(BaseModel):
    """出力設定（パスあり、Project用）"""

    path: str = Field(..., description="出力ファイルパス")
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

    @classmethod
    def from_settings(cls, settings: OutputSettings, path: str) -> "OutputConfig":
        """OutputSettingsとパスからOutputConfigを作成"""
        return cls(
            path=path,
            width=settings.width,
            height=settings.height,
            fps=settings.fps,
            codec=settings.codec,
            audio_codec=settings.audio_codec,
            bitrate=settings.bitrate,
            preset=settings.preset,
            subtitle_mode=settings.subtitle_mode,
        )
