"""Layer preset registry"""

from .base import LayerPreset


class LayerPresetRegistry:
    """プリセット管理"""

    _presets: dict[str, LayerPreset] = {}

    @classmethod
    def register(cls, preset: LayerPreset) -> None:
        """プリセットを登録する

        Args:
            preset: 登録するプリセット
        """
        cls._presets[preset.name] = preset

    @classmethod
    def get(cls, name: str) -> LayerPreset:
        """プリセットを取得する

        Args:
            name: プリセット名

        Returns:
            LayerPreset: プリセット

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


def _register_default_presets() -> None:
    """デフォルトプリセットを登録する"""
    from .default import DefaultLayerPreset
    from .bold_subtitle import BoldSubtitlePreset
    from .minimal import MinimalPreset
    from .vertical import VerticalPreset

    LayerPresetRegistry.register(DefaultLayerPreset())
    LayerPresetRegistry.register(BoldSubtitlePreset())
    LayerPresetRegistry.register(MinimalPreset())
    LayerPresetRegistry.register(VerticalPreset())


# モジュールロード時にデフォルトプリセットを登録
_register_default_presets()
