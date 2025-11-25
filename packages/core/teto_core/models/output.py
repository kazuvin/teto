from pydantic import BaseModel, Field
from typing import Literal


class OutputConfig(BaseModel):
    """出力設定"""

    path: str = Field(..., description="出力ファイルパス")
    width: int = Field(1920, description="動画の幅", gt=0)
    height: int = Field(1080, description="動画の高さ", gt=0)
    fps: int = Field(30, description="フレームレート", gt=0)
    codec: str = Field("libx264", description="動画コーデック")
    audio_codec: str = Field("aac", description="音声コーデック")
    bitrate: str | None = Field(None, description="ビットレート (例: '5000k')")
    subtitle_mode: Literal["burn", "srt", "vtt", "none"] = Field(
        "burn", description="字幕モード: burn=焼き込み, srt/vtt=ファイル出力, none=なし"
    )
