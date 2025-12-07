"""Output configuration tests"""

from teto_core.output_config.models import (
    VideoAspectRatio,
    ASPECT_RATIO_RESOLUTIONS,
    OutputSettings,
    OutputConfig,
)


class TestVideoAspectRatio:
    """VideoAspectRatio tests"""

    def test_landscape_16_9(self):
        """16:9 アスペクト比が定義されていること"""
        assert VideoAspectRatio.LANDSCAPE_16_9 == "16:9"

    def test_portrait_9_16(self):
        """9:16 アスペクト比が定義されていること"""
        assert VideoAspectRatio.PORTRAIT_9_16 == "9:16"

    def test_square_1_1(self):
        """1:1 アスペクト比が定義されていること"""
        assert VideoAspectRatio.SQUARE_1_1 == "1:1"

    def test_standard_4_3(self):
        """4:3 アスペクト比が定義されていること"""
        assert VideoAspectRatio.STANDARD_4_3 == "4:3"

    def test_wide_21_9(self):
        """21:9 アスペクト比が定義されていること"""
        assert VideoAspectRatio.WIDE_21_9 == "21:9"


class TestAspectRatioResolutions:
    """ASPECT_RATIO_RESOLUTIONS tests"""

    def test_landscape_16_9_resolution(self):
        """16:9 の解像度が正しいこと"""
        assert ASPECT_RATIO_RESOLUTIONS[VideoAspectRatio.LANDSCAPE_16_9] == (1920, 1080)

    def test_portrait_9_16_resolution(self):
        """9:16 の解像度が正しいこと（縦長）"""
        assert ASPECT_RATIO_RESOLUTIONS[VideoAspectRatio.PORTRAIT_9_16] == (1080, 1920)

    def test_square_1_1_resolution(self):
        """1:1 の解像度が正しいこと（正方形）"""
        assert ASPECT_RATIO_RESOLUTIONS[VideoAspectRatio.SQUARE_1_1] == (1080, 1080)

    def test_standard_4_3_resolution(self):
        """4:3 の解像度が正しいこと"""
        assert ASPECT_RATIO_RESOLUTIONS[VideoAspectRatio.STANDARD_4_3] == (1440, 1080)

    def test_wide_21_9_resolution(self):
        """21:9 の解像度が正しいこと（ウルトラワイド）"""
        assert ASPECT_RATIO_RESOLUTIONS[VideoAspectRatio.WIDE_21_9] == (2560, 1080)


class TestOutputSettings:
    """OutputSettings tests"""

    def test_default_values(self):
        """デフォルト値が正しいこと"""
        settings = OutputSettings()
        assert settings.aspect_ratio is None
        assert settings.width == 1920
        assert settings.height == 1080
        assert settings.fps == 30

    def test_with_aspect_ratio_16_9(self):
        """aspect_ratio=16:9 で解像度が設定されること"""
        settings = OutputSettings(aspect_ratio=VideoAspectRatio.LANDSCAPE_16_9)
        assert settings.width == 1920
        assert settings.height == 1080

    def test_with_aspect_ratio_9_16(self):
        """aspect_ratio=9:16 で解像度が設定されること（縦長）"""
        settings = OutputSettings(aspect_ratio=VideoAspectRatio.PORTRAIT_9_16)
        assert settings.width == 1080
        assert settings.height == 1920

    def test_with_aspect_ratio_1_1(self):
        """aspect_ratio=1:1 で解像度が設定されること（正方形）"""
        settings = OutputSettings(aspect_ratio=VideoAspectRatio.SQUARE_1_1)
        assert settings.width == 1080
        assert settings.height == 1080

    def test_aspect_ratio_overrides_width_height(self):
        """aspect_ratio が width/height を上書きすること"""
        settings = OutputSettings(
            aspect_ratio=VideoAspectRatio.PORTRAIT_9_16, width=9999, height=9999
        )
        # aspect_ratioが優先される
        assert settings.width == 1080
        assert settings.height == 1920

    def test_without_aspect_ratio_uses_width_height(self):
        """aspect_ratio がない場合は width/height が使われること"""
        settings = OutputSettings(width=1440, height=2560)
        assert settings.width == 1440
        assert settings.height == 2560

    def test_aspect_ratio_with_string(self):
        """文字列でアスペクト比を指定できること"""
        settings = OutputSettings(aspect_ratio="9:16")
        assert settings.width == 1080
        assert settings.height == 1920


class TestOutputConfig:
    """OutputConfig tests"""

    def test_with_aspect_ratio(self):
        """aspect_ratio で解像度が設定されること"""
        config = OutputConfig(
            path="output.mp4", aspect_ratio=VideoAspectRatio.PORTRAIT_9_16
        )
        assert config.width == 1080
        assert config.height == 1920

    def test_from_settings_with_aspect_ratio(self):
        """OutputSettings.aspect_ratio が引き継がれること"""
        settings = OutputSettings(aspect_ratio=VideoAspectRatio.PORTRAIT_9_16)
        config = OutputConfig.from_settings(settings, "output.mp4")
        assert config.aspect_ratio == VideoAspectRatio.PORTRAIT_9_16
        assert config.width == 1080
        assert config.height == 1920

    def test_from_settings_without_aspect_ratio(self):
        """aspect_ratio がない場合も正しく動作すること"""
        settings = OutputSettings(width=1440, height=2560)
        config = OutputConfig.from_settings(settings, "output.mp4")
        assert config.aspect_ratio is None
        assert config.width == 1440
        assert config.height == 2560

    def test_from_settings_preserves_all_fields(self):
        """from_settings が全フィールドを保持すること"""
        settings = OutputSettings(
            aspect_ratio=VideoAspectRatio.PORTRAIT_9_16,
            fps=60,
            codec="libx265",
            preset="slow",
        )
        config = OutputConfig.from_settings(settings, "test.mp4")
        assert config.path == "test.mp4"
        assert config.fps == 60
        assert config.codec == "libx265"
        assert config.preset == "slow"
