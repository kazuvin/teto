"""Layer presets tests"""

import pytest

from teto_core.script.presets import (
    LayerPresetRegistry,
    DefaultLayerPreset,
    BoldSubtitlePreset,
    MinimalPreset,
    VerticalPreset,
)


class TestDefaultLayerPreset:
    """DefaultLayerPreset tests"""

    def test_name(self):
        """プリセット名が正しいこと"""
        preset = DefaultLayerPreset()
        assert preset.name == "default"

    def test_output_config(self):
        """出力設定が正しいこと"""
        preset = DefaultLayerPreset()
        config = preset.get_output_config("output.mp4")
        assert config.path == "output.mp4"
        assert config.width == 1920
        assert config.height == 1080
        assert config.fps == 30

    def test_subtitle_style(self):
        """字幕スタイルが正しいこと"""
        preset = DefaultLayerPreset()
        style = preset.get_subtitle_style()
        assert style.font_size == "lg"
        assert style.appearance == "shadow"

    def test_image_effects(self):
        """画像エフェクトが設定されていること"""
        preset = DefaultLayerPreset()
        effects = preset.get_image_effects()
        assert len(effects) == 1
        assert effects[0].type == "kenBurns"

    def test_video_effects(self):
        """動画エフェクトが空であること"""
        preset = DefaultLayerPreset()
        effects = preset.get_video_effects()
        assert len(effects) == 0

    def test_transition(self):
        """トランジションが設定されていること"""
        preset = DefaultLayerPreset()
        transition = preset.get_transition()
        assert transition is not None
        assert transition.type == "crossfade"


class TestBoldSubtitlePreset:
    """BoldSubtitlePreset tests"""

    def test_name(self):
        """プリセット名が正しいこと"""
        preset = BoldSubtitlePreset()
        assert preset.name == "bold_subtitle"

    def test_subtitle_style(self):
        """字幕スタイルが正しいこと"""
        preset = BoldSubtitlePreset()
        style = preset.get_subtitle_style()
        assert style.font_size == "xl"
        assert style.font_color == "yellow"
        assert style.font_weight == "bold"
        assert style.appearance == "drop-shadow"
        assert style.position == "center"


class TestMinimalPreset:
    """MinimalPreset tests"""

    def test_name(self):
        """プリセット名が正しいこと"""
        preset = MinimalPreset()
        assert preset.name == "minimal"

    def test_no_effects(self):
        """エフェクトがないこと"""
        preset = MinimalPreset()
        assert len(preset.get_image_effects()) == 0
        assert len(preset.get_video_effects()) == 0

    def test_no_transition(self):
        """トランジションがないこと"""
        preset = MinimalPreset()
        assert preset.get_transition() is None


class TestVerticalPreset:
    """VerticalPreset tests"""

    def test_name(self):
        """プリセット名が正しいこと"""
        preset = VerticalPreset()
        assert preset.name == "vertical"

    def test_output_config(self):
        """縦型の出力設定であること"""
        preset = VerticalPreset()
        config = preset.get_output_config("output.mp4")
        assert config.width == 1080
        assert config.height == 1920


class TestLayerPresetRegistry:
    """LayerPresetRegistry tests"""

    def test_get_default(self):
        """デフォルトプリセットを取得できること"""
        preset = LayerPresetRegistry.get("default")
        assert preset.name == "default"

    def test_get_bold_subtitle(self):
        """bold_subtitleプリセットを取得できること"""
        preset = LayerPresetRegistry.get("bold_subtitle")
        assert preset.name == "bold_subtitle"

    def test_get_minimal(self):
        """minimalプリセットを取得できること"""
        preset = LayerPresetRegistry.get("minimal")
        assert preset.name == "minimal"

    def test_get_vertical(self):
        """verticalプリセットを取得できること"""
        preset = LayerPresetRegistry.get("vertical")
        assert preset.name == "vertical"

    def test_get_unknown_raises(self):
        """存在しないプリセットを取得するとエラーになること"""
        with pytest.raises(ValueError) as exc_info:
            LayerPresetRegistry.get("unknown")
        assert "Unknown preset" in str(exc_info.value)

    def test_list_names(self):
        """プリセット名のリストを取得できること"""
        names = LayerPresetRegistry.list_names()
        assert "default" in names
        assert "bold_subtitle" in names
        assert "minimal" in names
        assert "vertical" in names
