from pydantic import BaseModel, Field
from typing import Union
from .layers import VideoLayer, ImageLayer, AudioLayer, SubtitleLayer
from .output import OutputConfig


class Timeline(BaseModel):
    """タイムライン"""

    video_layers: list[Union[VideoLayer, ImageLayer]] = Field(
        default_factory=list, description="動画・画像レイヤー"
    )
    audio_layers: list[AudioLayer] = Field(default_factory=list, description="音声レイヤー")
    subtitle_layers: list[SubtitleLayer] = Field(
        default_factory=list, description="字幕レイヤー"
    )


class Project(BaseModel):
    """プロジェクト全体の定義"""

    version: str = Field("1.0", description="プロジェクトファイルのバージョン")
    output: OutputConfig = Field(..., description="出力設定")
    timeline: Timeline = Field(default_factory=Timeline, description="タイムライン")

    @classmethod
    def from_json_file(cls, path: str) -> "Project":
        """JSONファイルから読み込み"""
        import json
        from pathlib import Path

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    def to_json_file(self, path: str) -> None:
        """JSONファイルに保存"""
        import json
        from pathlib import Path

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2, ensure_ascii=False)
