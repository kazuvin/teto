"""Effect preset registry"""

from .base import EffectPreset


class EffectPresetRegistry:
    """エフェクトプリセット管理"""

    _presets: dict[str, EffectPreset] = {}

    @classmethod
    def register(cls, preset: EffectPreset) -> None:
        """プリセットを登録する

        Args:
            preset: 登録するプリセット
        """
        cls._presets[preset.name] = preset

    @classmethod
    def get(cls, name: str) -> EffectPreset:
        """プリセットを取得する

        Args:
            name: プリセット名

        Returns:
            EffectPreset: プリセット

        Raises:
            ValueError: 指定された名前のプリセットが存在しない場合
        """
        if name not in cls._presets:
            raise ValueError(f"Unknown preset: {name}. Available: {cls.list_names()}")
        return cls._presets[name]

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


# 後方互換性のためのエイリアス
ScenePresetRegistry = EffectPresetRegistry
LayerPresetRegistry = EffectPresetRegistry


def _register_default_presets() -> None:
    """デフォルトプリセットを登録する"""
    from .default import DefaultEffectPreset
    from .dramatic import DramaticEffectPreset
    from .slideshow import SlideshowEffectPreset
    from .kenburns import (
        KenBurnsLeftToRightPreset,
        KenBurnsRightToLeftPreset,
        KenBurnsTopToBottomPreset,
        KenBurnsBottomToTopPreset,
        KenBurnsZoomInPreset,
        KenBurnsZoomOutPreset,
        KenBurnsDiagonalLeftTopPreset,
        KenBurnsDiagonalRightTopPreset,
    )

    EffectPresetRegistry.register(DefaultEffectPreset())
    EffectPresetRegistry.register(DramaticEffectPreset())
    EffectPresetRegistry.register(SlideshowEffectPreset())
    # Ken Burns プリセット
    EffectPresetRegistry.register(KenBurnsLeftToRightPreset())
    EffectPresetRegistry.register(KenBurnsRightToLeftPreset())
    EffectPresetRegistry.register(KenBurnsTopToBottomPreset())
    EffectPresetRegistry.register(KenBurnsBottomToTopPreset())
    EffectPresetRegistry.register(KenBurnsZoomInPreset())
    EffectPresetRegistry.register(KenBurnsZoomOutPreset())
    EffectPresetRegistry.register(KenBurnsDiagonalLeftTopPreset())
    EffectPresetRegistry.register(KenBurnsDiagonalRightTopPreset())


# モジュールロード時にデフォルトプリセットを登録
_register_default_presets()
