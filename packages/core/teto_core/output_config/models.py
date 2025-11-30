"""Output configuration models"""

from pydantic import BaseModel, Field
from typing import Literal


class OutputConfig(BaseModel):
    """出力設定"""

    path: str = Field(..., description="出力ファイルパス")
    width: int = Field(1920, description="出力幅", gt=0)
    height: int = Field(1080, description="出力高さ", gt=0)
    fps: int = Field(30, description="フレームレート", gt=0)
    codec: str = Field("libx264", description="ビデオコーデック")
    audio_codec: str = Field("aac", description="オーディオコーデック")
    bitrate: str | None = Field(None, description="ビットレート")
    subtitle_mode: Literal["burn", "srt", "vtt", "none"] = Field(
        "burn", description="字幕モード"
    )
