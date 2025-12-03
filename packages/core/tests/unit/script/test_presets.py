"""Scene presets tests"""

import pytest

from teto_core.script.presets import (
    ScenePresetRegistry,
    DefaultScenePreset,
    BoldSubtitleScenePreset,
    MinimalScenePreset,
    VerticalScenePreset,
    # 後方互換性のエイリアス
    LayerPresetRegistry,
    DefaultLayerPreset,
    BoldSubtitlePreset,
    MinimalPreset,
    VerticalPreset,
)


class TestDefaultScenePreset:
    """DefaultScenePreset tests"""

    def test_name(self):
        """プリセット名が正しいこと"""
        preset = DefaultScenePreset()
        assert preset.name == "default"

    def test_image_effects(self):
        """画像エフェクトが設定されていること"""
        preset = DefaultScenePreset()
        effects = preset.get_image_effects()
        assert len(effects) == 1
        assert effects[0].type == "kenBurns"

    def test_video_effects(self):
        """動画エフェクトが空であること"""
        preset = DefaultScenePreset()
        effects = preset.get_video_effects()
        assert len(effects) == 0

    def test_transition(self):
        """トランジションが設定されていること"""
        preset = DefaultScenePreset()
        transition = preset.get_transition()
        assert transition is not None
        assert transition.type == "crossfade"
        assert transition.duration == 0.5


class TestBoldSubtitleScenePreset:
    """BoldSubtitleScenePreset tests"""

    def test_name(self):
        """プリセット名が正しいこと"""
        preset = BoldSubtitleScenePreset()
        assert preset.name == "bold_subtitle"

    def test_image_effects(self):
        """画像エフェクト（zoom）が設定されていること"""
        preset = BoldSubtitleScenePreset()
        effects = preset.get_image_effects()
        assert len(effects) == 1
        assert effects[0].type == "zoom"

    def test_transition(self):
        """トランジションが設定されていること"""
        preset = BoldSubtitleScenePreset()
        transition = preset.get_transition()
        assert transition is not None
        assert transition.type == "crossfade"
        assert transition.duration == 0.3


class TestMinimalScenePreset:
    """MinimalScenePreset tests"""

    def test_name(self):
        """プリセット名が正しいこと"""
        preset = MinimalScenePreset()
        assert preset.name == "minimal"

    def test_no_effects(self):
        """エフェクトがないこと"""
        preset = MinimalScenePreset()
        assert len(preset.get_image_effects()) == 0
        assert len(preset.get_video_effects()) == 0

    def test_no_transition(self):
        """トランジションがないこと"""
        preset = MinimalScenePreset()
        assert preset.get_transition() is None


class TestVerticalScenePreset:
    """VerticalScenePreset tests"""

    def test_name(self):
        """プリセット名が正しいこと"""
        preset = VerticalScenePreset()
        assert preset.name == "vertical"

    def test_image_effects(self):
        """画像エフェクトが設定されていること"""
        preset = VerticalScenePreset()
        effects = preset.get_image_effects()
        assert len(effects) == 1
        assert effects[0].type == "kenBurns"

    def test_transition(self):
        """トランジションが設定されていること"""
        preset = VerticalScenePreset()
        transition = preset.get_transition()
        assert transition is not None
        assert transition.type == "crossfade"


class TestScenePresetRegistry:
    """ScenePresetRegistry tests"""

    def test_get_default(self):
        """デフォルトプリセットを取得できること"""
        preset = ScenePresetRegistry.get("default")
        assert preset.name == "default"

    def test_get_bold_subtitle(self):
        """bold_subtitleプリセットを取得できること"""
        preset = ScenePresetRegistry.get("bold_subtitle")
        assert preset.name == "bold_subtitle"

    def test_get_minimal(self):
        """minimalプリセットを取得できること"""
        preset = ScenePresetRegistry.get("minimal")
        assert preset.name == "minimal"

    def test_get_vertical(self):
        """verticalプリセットを取得できること"""
        preset = ScenePresetRegistry.get("vertical")
        assert preset.name == "vertical"

    def test_get_unknown_raises(self):
        """存在しないプリセットを取得するとエラーになること"""
        with pytest.raises(ValueError) as exc_info:
            ScenePresetRegistry.get("unknown")
        assert "Unknown preset" in str(exc_info.value)

    def test_list_names(self):
        """プリセット名のリストを取得できること"""
        names = ScenePresetRegistry.list_names()
        assert "default" in names
        assert "bold_subtitle" in names
        assert "minimal" in names
        assert "vertical" in names


class TestBackwardCompatibilityAliases:
    """後方互換性のためのエイリアスが動作すること"""

    def test_layer_preset_registry_alias(self):
        """LayerPresetRegistry エイリアスが動作すること"""
        preset = LayerPresetRegistry.get("default")
        assert preset.name == "default"

    def test_default_layer_preset_alias(self):
        """DefaultLayerPreset エイリアスが動作すること"""
        preset = DefaultLayerPreset()
        assert preset.name == "default"

    def test_bold_subtitle_preset_alias(self):
        """BoldSubtitlePreset エイリアスが動作すること"""
        preset = BoldSubtitlePreset()
        assert preset.name == "bold_subtitle"

    def test_minimal_preset_alias(self):
        """MinimalPreset エイリアスが動作すること"""
        preset = MinimalPreset()
        assert preset.name == "minimal"

    def test_vertical_preset_alias(self):
        """VerticalPreset エイリアスが動作すること"""
        preset = VerticalPreset()
        assert preset.name == "vertical"
