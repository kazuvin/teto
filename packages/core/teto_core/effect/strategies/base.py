"""エフェクト戦略の基底クラス"""

from abc import ABC, abstractmethod
from moviepy import VideoClip, ImageClip
from ..models import AnimationEffect


class EffectStrategy(ABC):
    """エフェクト適用戦略の基底クラス"""

    @abstractmethod
    def apply(
        self,
        clip: VideoClip | ImageClip,
        effect: AnimationEffect,
        video_size: tuple[int, int],
    ) -> VideoClip | ImageClip:
        """エフェクトを適用する

        Args:
            clip: 元のクリップ
            effect: エフェクト設定
            video_size: 動画サイズ

        Returns:
            エフェクトを適用したクリップ
        """
        pass
