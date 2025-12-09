"""Composite preset - combines multiple scene settings"""

from typing import TYPE_CHECKING
from pydantic import BaseModel, Field

from ...effect.models import AnimationEffect, TransitionConfig
from .base import SubtitleStyleConfig

if TYPE_CHECKING:
    from ..models import TimingConfig, BGMConfig, VoiceConfig


class PresetConfig(BaseModel):
    """複合プリセット設定（複数の設定を束ねる）

    フック・概要・本編・CTAといった粒度の粗いプリセットを定義するために使用。
    アニメーション・字幕スタイル・BGM・タイミングなどを一括で設定できる。
    """

    # エフェクト名（既存のScenePresetを参照）
    effect: str | None = Field(
        None,
        description="使用するエフェクト名（ScenePresetRegistryから取得）",
    )

    # または直接エフェクトを指定
    effects: list[AnimationEffect] = Field(
        default_factory=list,
        description="アニメーションエフェクトのリスト（effectより優先）",
    )
    transition: TransitionConfig | None = Field(None, description="トランジション設定")

    # 字幕スタイル
    subtitle_style: SubtitleStyleConfig | None = Field(
        None, description="字幕スタイル設定"
    )

    # BGM設定
    bgm: "BGMConfig | None" = Field(None, description="BGM設定")

    # タイミング
    timing_override: "TimingConfig | None" = Field(
        None, description="タイミング設定のオーバーライド"
    )

    # 音声設定
    voice: "VoiceConfig | None" = Field(None, description="音声設定")


class PresetRegistry:
    """複合プリセット管理"""

    _presets: dict[str, PresetConfig] = {}

    @classmethod
    def register(cls, name: str, preset: PresetConfig) -> None:
        """複合プリセットを登録する

        Args:
            name: プリセット名
            preset: 登録するプリセット
        """
        cls._presets[name] = preset

    @classmethod
    def get(cls, name: str) -> PresetConfig | None:
        """複合プリセットを取得する

        Args:
            name: プリセット名

        Returns:
            PresetConfig | None: プリセット（存在しない場合はNone）
        """
        return cls._presets.get(name)

    @classmethod
    def list_names(cls) -> list[str]:
        """登録されているプリセット名のリストを取得する

        Returns:
            list[str]: プリセット名のリスト
        """
        return list(cls._presets.keys())

    @classmethod
    def clear(cls) -> None:
        """全てのプリセット登録をクリアする（テスト用）"""
        cls._presets = {}
