"""Effect preset base interface"""

from abc import ABC, abstractmethod

from ...effect.models import AnimationEffect


class EffectPreset(ABC):
    """エフェクトプリセット（Strategy）

    シーン毎のアニメーションエフェクト設定を定型化するインターフェース。

    Note:
        複合プリセット（字幕スタイル、タイミング等）は presets/ を使用する。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """プリセット名"""
        ...

    @abstractmethod
    def get_image_effects(self) -> list[AnimationEffect]:
        """画像レイヤーに適用するエフェクトを取得

        Returns:
            list[AnimationEffect]: エフェクトリスト
        """
        ...

    @abstractmethod
    def get_video_effects(self) -> list[AnimationEffect]:
        """動画レイヤーに適用するエフェクトを取得

        Returns:
            list[AnimationEffect]: エフェクトリスト
        """
        ...


# 後方互換性のためのエイリアス
ScenePreset = EffectPreset
LayerPreset = EffectPreset
