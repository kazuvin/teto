"""Script models tests"""

import pytest
from pydantic import ValidationError

from teto_core.script.models import (
    Script,
    Scene,
    NarrationSegment,
    Visual,
    AssetType,
    TimingConfig,
    BGMConfig,
    VoiceConfig,
)


class TestVisual:
    """Visual model tests"""

    def test_create_with_path(self):
        """パスで作成できること"""
        visual = Visual(path="./assets/image.png")
        assert visual.path == "./assets/image.png"
        assert visual.type == AssetType.IMAGE
        assert visual.description is None

    def test_create_with_description(self):
        """説明で作成できること"""
        visual = Visual(description="説明文")
        assert visual.description == "説明文"
        assert visual.path is None

    def test_create_with_video_type(self):
        """動画タイプで作成できること"""
        visual = Visual(type=AssetType.VIDEO, path="./video.mp4")
        assert visual.type == AssetType.VIDEO

    def test_requires_path_or_description(self):
        """pathまたはdescriptionが必須であること"""
        with pytest.raises(ValidationError) as exc_info:
            Visual()
        assert "path または description のいずれかは必須です" in str(exc_info.value)


class TestNarrationSegment:
    """NarrationSegment model tests"""

    def test_create_simple(self):
        """シンプルに作成できること"""
        segment = NarrationSegment(text="テスト")
        assert segment.text == "テスト"
        assert segment.pause_after == 0.0

    def test_create_with_pause(self):
        """pause_afterを指定できること"""
        segment = NarrationSegment(text="テスト", pause_after=0.5)
        assert segment.pause_after == 0.5

    def test_text_required(self):
        """textが必須であること"""
        with pytest.raises(ValidationError):
            NarrationSegment()  # type: ignore


class TestScene:
    """Scene model tests"""

    def test_create_with_narrations(self):
        """ナレーションありで作成できること"""
        scene = Scene(
            narrations=[NarrationSegment(text="テスト")],
            visual=Visual(path="./image.png"),
        )
        assert len(scene.narrations) == 1
        assert scene.duration is None

    def test_create_without_narrations(self):
        """ナレーションなしで作成できること（durationが必須）"""
        scene = Scene(
            narrations=[],
            visual=Visual(path="./image.png"),
            duration=3.0,
        )
        assert len(scene.narrations) == 0
        assert scene.duration == 3.0

    def test_requires_duration_when_no_narrations(self):
        """ナレーションなしの場合、durationが必須であること"""
        with pytest.raises(ValidationError) as exc_info:
            Scene(
                narrations=[],
                visual=Visual(path="./image.png"),
            )
        assert "ナレーションがないシーンには duration を指定してください" in str(
            exc_info.value
        )

    def test_note_is_optional(self):
        """noteはオプショナルであること"""
        scene = Scene(
            narrations=[NarrationSegment(text="テスト")],
            visual=Visual(path="./image.png"),
            note="演出メモ",
        )
        assert scene.note == "演出メモ"


class TestTimingConfig:
    """TimingConfig model tests"""

    def test_defaults(self):
        """デフォルト値で作成できること"""
        config = TimingConfig()
        assert config.default_segment_gap == 0.3
        assert config.default_scene_gap == 0.5
        assert config.subtitle_padding == 0.1

    def test_custom_values(self):
        """カスタム値を設定できること"""
        config = TimingConfig(
            default_segment_gap=0.5,
            default_scene_gap=1.0,
            subtitle_padding=0.2,
        )
        assert config.default_segment_gap == 0.5
        assert config.default_scene_gap == 1.0
        assert config.subtitle_padding == 0.2


class TestBGMConfig:
    """BGMConfig model tests"""

    def test_create(self):
        """作成できること"""
        config = BGMConfig(path="./bgm.mp3")
        assert config.path == "./bgm.mp3"
        assert config.volume == 0.3
        assert config.fade_in == 0.0
        assert config.fade_out == 0.0

    def test_custom_values(self):
        """カスタム値を設定できること"""
        config = BGMConfig(
            path="./bgm.mp3",
            volume=0.5,
            fade_in=1.0,
            fade_out=2.0,
        )
        assert config.volume == 0.5
        assert config.fade_in == 1.0
        assert config.fade_out == 2.0


class TestVoiceConfig:
    """VoiceConfig model tests"""

    def test_defaults(self):
        """デフォルト値で作成できること"""
        config = VoiceConfig()
        assert config.provider == "google"
        assert config.language_code == "ja-JP"
        assert config.speed == 1.0
        assert config.pitch == 0.0

    def test_custom_values(self):
        """カスタム値を設定できること"""
        config = VoiceConfig(
            provider="openai",
            voice_id="voice-1",
            language_code="en-US",
            speed=1.5,
            pitch=2.0,
        )
        assert config.provider == "openai"
        assert config.voice_id == "voice-1"
        assert config.language_code == "en-US"


class TestScript:
    """Script model tests"""

    def test_create_minimal(self):
        """最小構成で作成できること"""
        script = Script(
            title="テスト動画",
            scenes=[
                Scene(
                    narrations=[NarrationSegment(text="テスト")],
                    visual=Visual(path="./image.png"),
                )
            ],
        )
        assert script.title == "テスト動画"
        assert len(script.scenes) == 1

    def test_create_full(self):
        """全設定で作成できること"""
        script = Script(
            title="テスト動画",
            description="説明文",
            scenes=[
                Scene(
                    narrations=[NarrationSegment(text="テスト")],
                    visual=Visual(path="./image.png"),
                )
            ],
            voice=VoiceConfig(provider="google", speed=1.2),
            timing=TimingConfig(default_scene_gap=1.0),
            bgm=BGMConfig(path="./bgm.mp3", volume=0.2),
        )
        assert script.description == "説明文"
        assert script.voice.speed == 1.2
        assert script.timing.default_scene_gap == 1.0
        assert script.bgm is not None
        assert script.bgm.volume == 0.2

    def test_requires_at_least_one_scene(self):
        """少なくとも1つのシーンが必要であること"""
        with pytest.raises(ValidationError):
            Script(title="テスト", scenes=[])

    def test_output_as_list(self):
        """output を配列で指定できること（複数フォーマット出力）"""
        from teto_core.output_config.models import OutputSettings

        script = Script(
            title="マルチ出力テスト",
            scenes=[
                Scene(
                    narrations=[NarrationSegment(text="テスト")],
                    visual=Visual(path="./image.png"),
                )
            ],
            output=[
                OutputSettings(name="youtube", aspect_ratio="16:9"),
                OutputSettings(name="tiktok", aspect_ratio="9:16"),
            ],
        )
        assert isinstance(script.output, list)
        assert len(script.output) == 2
        assert script.output[0].name == "youtube"
        assert script.output[0].width == 1920
        assert script.output[0].height == 1080
        assert script.output[1].name == "tiktok"
        assert script.output[1].width == 1080
        assert script.output[1].height == 1920

    def test_output_as_single_object(self):
        """output を単一オブジェクトで指定できること（単一出力）"""
        from teto_core.output_config.models import OutputSettings

        script = Script(
            title="通常出力テスト",
            scenes=[
                Scene(
                    narrations=[NarrationSegment(text="テスト")],
                    visual=Visual(path="./image.png"),
                )
            ],
            output=OutputSettings(aspect_ratio="16:9"),
        )
        assert isinstance(script.output, OutputSettings)
        assert script.output.width == 1920
        assert script.output.height == 1080

    def test_output_dir_default(self):
        """output_dir はデフォルトで None であること"""
        script = Script(
            title="テスト動画",
            scenes=[
                Scene(
                    narrations=[NarrationSegment(text="テスト")],
                    visual=Visual(path="./image.png"),
                )
            ],
        )
        assert script.output_dir is None

    def test_output_dir_can_be_set(self):
        """output_dir を指定できること"""
        script = Script(
            title="テスト動画",
            scenes=[
                Scene(
                    narrations=[NarrationSegment(text="テスト")],
                    visual=Visual(path="./image.png"),
                )
            ],
            output_dir="./lp/2025/03/01",
        )
        assert script.output_dir == "./lp/2025/03/01"

    def test_output_dir_with_multi_output(self):
        """output_dir を複数出力設定と組み合わせて使用できること"""
        from teto_core.output_config.models import OutputSettings

        script = Script(
            title="マルチ出力テスト",
            scenes=[
                Scene(
                    narrations=[NarrationSegment(text="テスト")],
                    visual=Visual(path="./image.png"),
                )
            ],
            output=[
                OutputSettings(name="youtube", aspect_ratio="16:9"),
                OutputSettings(name="tiktok", aspect_ratio="9:16"),
            ],
            output_dir="output/multi_platform",
        )
        assert script.output_dir == "output/multi_platform"
        assert isinstance(script.output, list)
        assert len(script.output) == 2
