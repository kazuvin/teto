from pydantic import BaseModel, Field
from typing import Union
from ..layer.models import (
    VideoLayer,
    ImageLayer,
    AudioLayer,
    SubtitleLayer,
    StampLayer,
    CharacterLayer,
    LayeredCharacterLayer,
)
from ..output_config.models import OutputConfig


class Timeline(BaseModel):
    """タイムライン"""

    video_layers: list[Union[VideoLayer, ImageLayer]] = Field(
        default_factory=list, description="動画・画像レイヤー"
    )
    audio_layers: list[AudioLayer] = Field(
        default_factory=list, description="音声レイヤー"
    )
    subtitle_layers: list[SubtitleLayer] = Field(
        default_factory=list, description="字幕レイヤー"
    )
    stamp_layers: list[StampLayer] = Field(
        default_factory=list, description="スタンプレイヤー"
    )
    character_layers: list[CharacterLayer] = Field(
        default_factory=list, description="キャラクターレイヤー"
    )
    layered_character_layers: list[LayeredCharacterLayer] = Field(
        default_factory=list, description="レイヤードキャラクターレイヤー"
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

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    def to_json_file(self, path: str) -> None:
        """JSONファイルに保存"""
        import json

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2, ensure_ascii=False)
