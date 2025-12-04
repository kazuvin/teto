"""Scene presets tests"""

import pytest

from teto_core.script.presets import (
    ScenePresetRegistry,
    DefaultScenePreset,
    DramaticScenePreset,
    SlideshowScenePreset,
    # 後方互換性のエイリアス
    LayerPresetRegistry,
    DefaultLayerPreset,
    DramaticPreset,
    SlideshowPreset,
)


class TestDefaultScenePreset:
    """DefaultScenePreset tests"""

    def test_name(self):
        """プリセット名が正しいこと"""
        preset = DefaultScenePreset()
        assert preset.name == "default"

    def test_image_effects(self):
        """画像エフェクトが空であること"""
        preset = DefaultScenePreset()
        effects = preset.get_image_effects()
        assert len(effects) == 0

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


class TestDramaticScenePreset:
    """DramaticScenePreset tests"""

    def test_name(self):
        """プリセット名が正しいこと"""
        preset = DramaticScenePreset()
        assert preset.name == "dramatic"

    def test_image_effects(self):
        """画像エフェクト（glitch + colorGrade）が設定されていること"""
        preset = DramaticScenePreset()
        effects = preset.get_image_effects()
        assert len(effects) == 2
        assert effects[0].type == "glitch"
        assert effects[1].type == "colorGrade"

    def test_video_effects(self):
        """動画エフェクト（glitch + colorGrade）が設定されていること"""
        preset = DramaticScenePreset()
        effects = preset.get_video_effects()
        assert len(effects) == 2
        assert effects[0].type == "glitch"
        assert effects[1].type == "colorGrade"

    def test_transition(self):
        """トランジションが設定されていること"""
        preset = DramaticScenePreset()
        transition = preset.get_transition()
        assert transition is not None
        assert transition.type == "crossfade"
        assert transition.duration == 0.15


class TestSlideshowScenePreset:
    """SlideshowScenePreset tests"""

    def test_name(self):
        """プリセット名が正しいこと"""
        preset = SlideshowScenePreset()
        assert preset.name == "slideshow"

    def test_image_effects(self):
        """画像エフェクト（slideIn）が設定されていること"""
        preset = SlideshowScenePreset()
        effects = preset.get_image_effects()
        assert len(effects) == 1
        assert effects[0].type == "slideIn"

    def test_video_effects(self):
        """動画エフェクト（slideIn）が設定されていること"""
        preset = SlideshowScenePreset()
        effects = preset.get_video_effects()
        assert len(effects) == 1
        assert effects[0].type == "slideIn"

    def test_transition(self):
        """トランジションが設定されていること"""
        preset = SlideshowScenePreset()
        transition = preset.get_transition()
        assert transition is not None
        assert transition.type == "crossfade"
        assert transition.duration == 0.4


class TestScenePresetRegistry:
    """ScenePresetRegistry tests"""

    def test_get_default(self):
        """デフォルトプリセットを取得できること"""
        preset = ScenePresetRegistry.get("default")
        assert preset.name == "default"

    def test_get_dramatic(self):
        """dramaticプリセットを取得できること"""
        preset = ScenePresetRegistry.get("dramatic")
        assert preset.name == "dramatic"

    def test_get_slideshow(self):
        """slideshowプリセットを取得できること"""
        preset = ScenePresetRegistry.get("slideshow")
        assert preset.name == "slideshow"

    def test_get_unknown_raises(self):
        """存在しないプリセットを取得するとエラーになること"""
        with pytest.raises(ValueError) as exc_info:
            ScenePresetRegistry.get("unknown")
        assert "Unknown preset" in str(exc_info.value)

    def test_list_names(self):
        """プリセット名のリストを取得できること"""
        names = ScenePresetRegistry.list_names()
        assert "default" in names
        assert "dramatic" in names
        assert "slideshow" in names


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

    def test_dramatic_preset_alias(self):
        """DramaticPreset エイリアスが動作すること"""
        preset = DramaticPreset()
        assert preset.name == "dramatic"

    def test_slideshow_preset_alias(self):
        """SlideshowPreset エイリアスが動作すること"""
        preset = SlideshowPreset()
        assert preset.name == "slideshow"
