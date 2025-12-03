"""Scene preset registry"""

from .base import ScenePreset


class ScenePresetRegistry:
    """プリセット管理"""

    _presets: dict[str, ScenePreset] = {}

    @classmethod
    def register(cls, preset: ScenePreset) -> None:
        """プリセットを登録する

        Args:
            preset: 登録するプリセット
        """
        cls._presets[preset.name] = preset

    @classmethod
    def get(cls, name: str) -> ScenePreset:
        """プリセットを取得する

        Args:
            name: プリセット名

        Returns:
            ScenePreset: プリセット

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
LayerPresetRegistry = ScenePresetRegistry


def _register_default_presets() -> None:
    """デフォルトプリセットを登録する"""
    from .default import DefaultScenePreset
    from .bold_subtitle import BoldSubtitleScenePreset
    from .minimal import MinimalScenePreset
    from .vertical import VerticalScenePreset

    ScenePresetRegistry.register(DefaultScenePreset())
    ScenePresetRegistry.register(BoldSubtitleScenePreset())
    ScenePresetRegistry.register(MinimalScenePreset())
    ScenePresetRegistry.register(VerticalScenePreset())


# モジュールロード時にデフォルトプリセットを登録
_register_default_presets()
