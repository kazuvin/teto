"""Ken Burns effect presets - Gentle pan and zoom effects"""

from ...effect.models import AnimationEffect
from .base import EffectPreset


class KenBurnsLeftToRightPreset(EffectPreset):
    """Ken Burns 左から右プリセット

    ゆっくりと左から右へパンする穏やかなKen Burns効果。
    """

    @property
    def name(self) -> str:
        return "kenburns-left-to-right"

    def get_image_effects(self) -> list[AnimationEffect]:
        return [
            AnimationEffect(
                type="kenBurns",
                pan_start=(-0.1, 0.0),
                pan_end=(0.1, 0.0),
                start_scale=1.05,
                end_scale=1.12,
                easing="linear",
            ),
        ]

    def get_video_effects(self) -> list[AnimationEffect]:
        return []


class KenBurnsRightToLeftPreset(EffectPreset):
    """Ken Burns 右から左プリセット

    ゆっくりと右から左へパンする穏やかなKen Burns効果。
    """

    @property
    def name(self) -> str:
        return "kenburns-right-to-left"

    def get_image_effects(self) -> list[AnimationEffect]:
        return [
            AnimationEffect(
                type="kenBurns",
                pan_start=(0.1, 0.0),
                pan_end=(-0.1, 0.0),
                start_scale=1.05,
                end_scale=1.12,
                easing="linear",
            ),
        ]

    def get_video_effects(self) -> list[AnimationEffect]:
        return []


class KenBurnsTopToBottomPreset(EffectPreset):
    """Ken Burns 上から下プリセット

    ゆっくりと上から下へパンする穏やかなKen Burns効果。
    """

    @property
    def name(self) -> str:
        return "kenburns-top-to-bottom"

    def get_image_effects(self) -> list[AnimationEffect]:
        return [
            AnimationEffect(
                type="kenBurns",
                pan_start=(0.0, -0.1),
                pan_end=(0.0, 0.1),
                start_scale=1.05,
                end_scale=1.12,
                easing="linear",
            ),
        ]

    def get_video_effects(self) -> list[AnimationEffect]:
        return []


class KenBurnsBottomToTopPreset(EffectPreset):
    """Ken Burns 下から上プリセット

    ゆっくりと下から上へパンする穏やかなKen Burns効果。
    """

    @property
    def name(self) -> str:
        return "kenburns-bottom-to-top"

    def get_image_effects(self) -> list[AnimationEffect]:
        return [
            AnimationEffect(
                type="kenBurns",
                pan_start=(0.0, 0.1),
                pan_end=(0.0, -0.1),
                start_scale=1.05,
                end_scale=1.12,
                easing="linear",
            ),
        ]

    def get_video_effects(self) -> list[AnimationEffect]:
        return []


class KenBurnsZoomInPreset(EffectPreset):
    """Ken Burns ズームインプリセット

    中央に向かってゆっくりズームインする穏やかなKen Burns効果。
    パンなしで、静かにズームのみを行います。
    """

    @property
    def name(self) -> str:
        return "kenburns-zoom-in"

    def get_image_effects(self) -> list[AnimationEffect]:
        return [
            AnimationEffect(
                type="kenBurns",
                pan_start=(0.0, 0.0),
                pan_end=(0.0, 0.0),
                start_scale=1.0,
                end_scale=1.15,
                easing="linear",
            ),
        ]

    def get_video_effects(self) -> list[AnimationEffect]:
        return []


class KenBurnsZoomOutPreset(EffectPreset):
    """Ken Burns ズームアウトプリセット

    中央からゆっくりズームアウトする穏やかなKen Burns効果。
    パンなしで、静かにズームのみを行います。
    """

    @property
    def name(self) -> str:
        return "kenburns-zoom-out"

    def get_image_effects(self) -> list[AnimationEffect]:
        return [
            AnimationEffect(
                type="kenBurns",
                pan_start=(0.0, 0.0),
                pan_end=(0.0, 0.0),
                start_scale=1.15,
                end_scale=1.0,
                easing="linear",
            ),
        ]

    def get_video_effects(self) -> list[AnimationEffect]:
        return []


class KenBurnsDiagonalLeftTopPreset(EffectPreset):
    """Ken Burns 左上から右下プリセット

    ゆっくりと左上から右下へパンする穏やかなKen Burns効果。
    対角線方向の動きで、自然な視線誘導を行います。
    """

    @property
    def name(self) -> str:
        return "kenburns-diagonal-lt-rb"

    def get_image_effects(self) -> list[AnimationEffect]:
        return [
            AnimationEffect(
                type="kenBurns",
                pan_start=(-0.08, -0.08),
                pan_end=(0.08, 0.08),
                start_scale=1.05,
                end_scale=1.12,
                easing="linear",
            ),
        ]

    def get_video_effects(self) -> list[AnimationEffect]:
        return []


class KenBurnsDiagonalRightTopPreset(EffectPreset):
    """Ken Burns 右上から左下プリセット

    ゆっくりと右上から左下へパンする穏やかなKen Burns効果。
    対角線方向の動きで、自然な視線誘導を行います。
    """

    @property
    def name(self) -> str:
        return "kenburns-diagonal-rt-lb"

    def get_image_effects(self) -> list[AnimationEffect]:
        return [
            AnimationEffect(
                type="kenBurns",
                pan_start=(0.08, -0.08),
                pan_end=(-0.08, 0.08),
                start_scale=1.05,
                end_scale=1.12,
                easing="linear",
            ),
        ]

    def get_video_effects(self) -> list[AnimationEffect]:
        return []
