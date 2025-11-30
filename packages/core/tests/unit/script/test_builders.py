"""Script builders tests"""

import pytest

from teto_core.script import (
    AssetType,
)
from teto_core.script.builders import (
    ScriptBuilder,
    SceneBuilder,
    NarrationSegmentBuilder,
)


class TestNarrationSegmentBuilder:
    """NarrationSegmentBuilder tests"""

    def test_build_simple(self):
        """シンプルに構築できること"""
        segment = NarrationSegmentBuilder("テスト").build()
        assert segment.text == "テスト"
        assert segment.pause_after == 0.0

    def test_build_with_pause(self):
        """pause_afterを設定できること"""
        segment = NarrationSegmentBuilder("テスト").pause_after(0.5).build()
        assert segment.pause_after == 0.5

    def test_chaining(self):
        """メソッドチェーンが動作すること"""
        builder = NarrationSegmentBuilder("テスト")
        result = builder.pause_after(0.5)
        assert result is builder


class TestSceneBuilder:
    """SceneBuilder tests"""

    def test_build_with_narrations(self):
        """ナレーションありで構築できること"""
        scene = (
            SceneBuilder()
            .add_narration("こんにちは")
            .add_narration("さようなら", pause_after=0.5)
            .visual_path("./image.png")
            .build()
        )
        assert len(scene.narrations) == 2
        assert scene.narrations[0].text == "こんにちは"
        assert scene.narrations[1].pause_after == 0.5
        assert scene.visual.path == "./image.png"

    def test_build_without_narrations(self):
        """ナレーションなしで構築できること（durationが必須）"""
        scene = SceneBuilder().visual_path("./title.png").duration(3.0).build()
        assert len(scene.narrations) == 0
        assert scene.duration == 3.0

    def test_visual_path_with_video_type(self):
        """動画タイプでvisualを設定できること"""
        scene = (
            SceneBuilder()
            .add_narration("テスト")
            .visual_path("./video.mp4", AssetType.VIDEO)
            .build()
        )
        assert scene.visual.type == AssetType.VIDEO

    def test_visual_description(self):
        """説明でvisualを設定できること"""
        scene = (
            SceneBuilder()
            .add_narration("テスト")
            .visual_description("青空の画像")
            .build()
        )
        assert scene.visual.description == "青空の画像"
        assert scene.visual.path is None

    def test_pause_after(self):
        """シーン後の間隔を設定できること"""
        scene = (
            SceneBuilder()
            .add_narration("テスト")
            .visual_path("./image.png")
            .pause_after(1.0)
            .build()
        )
        assert scene.pause_after == 1.0

    def test_note(self):
        """演出メモを設定できること"""
        scene = (
            SceneBuilder()
            .add_narration("テスト")
            .visual_path("./image.png")
            .note("演出メモ")
            .build()
        )
        assert scene.note == "演出メモ"

    def test_build_without_visual_raises(self):
        """visualなしで構築するとエラーになること"""
        with pytest.raises(ValueError) as exc_info:
            SceneBuilder().add_narration("テスト").build()
        assert "Visual is required" in str(exc_info.value)


class TestScriptBuilder:
    """ScriptBuilder tests"""

    def test_build_minimal(self):
        """最小構成で構築できること"""
        script = (
            ScriptBuilder("テスト動画")
            .add_scene(
                SceneBuilder()
                .add_narration("テスト")
                .visual_path("./image.png")
                .build()
            )
            .build()
        )
        assert script.title == "テスト動画"
        assert len(script.scenes) == 1

    def test_add_scene_builder(self):
        """SceneBuilderから直接追加できること"""
        script = (
            ScriptBuilder("テスト動画")
            .add_scene_builder(
                SceneBuilder().add_narration("テスト").visual_path("./image.png")
            )
            .build()
        )
        assert len(script.scenes) == 1

    def test_voice_settings(self):
        """音声設定を設定できること"""
        script = (
            ScriptBuilder("テスト動画")
            .add_scene_builder(
                SceneBuilder().add_narration("テスト").visual_path("./image.png")
            )
            .voice(provider="google", speed=1.2, pitch=2.0)
            .build()
        )
        assert script.voice.provider == "google"
        assert script.voice.speed == 1.2
        assert script.voice.pitch == 2.0

    def test_timing_settings(self):
        """タイミング設定を設定できること"""
        script = (
            ScriptBuilder("テスト動画")
            .add_scene_builder(
                SceneBuilder().add_narration("テスト").visual_path("./image.png")
            )
            .timing(segment_gap=0.5, scene_gap=1.0, subtitle_padding=0.2)
            .build()
        )
        assert script.timing.default_segment_gap == 0.5
        assert script.timing.default_scene_gap == 1.0
        assert script.timing.subtitle_padding == 0.2

    def test_bgm_settings(self):
        """BGM設定を設定できること"""
        script = (
            ScriptBuilder("テスト動画")
            .add_scene_builder(
                SceneBuilder().add_narration("テスト").visual_path("./image.png")
            )
            .bgm(path="./bgm.mp3", volume=0.5, fade_in=1.0, fade_out=2.0)
            .build()
        )
        assert script.bgm is not None
        assert script.bgm.path == "./bgm.mp3"
        assert script.bgm.volume == 0.5
        assert script.bgm.fade_in == 1.0
        assert script.bgm.fade_out == 2.0

    def test_description(self):
        """説明を設定できること"""
        script = (
            ScriptBuilder("テスト動画")
            .add_scene_builder(
                SceneBuilder().add_narration("テスト").visual_path("./image.png")
            )
            .description("動画の説明")
            .build()
        )
        assert script.description == "動画の説明"

    def test_build_without_scenes_raises(self):
        """シーンなしで構築するとエラーになること"""
        with pytest.raises(ValueError) as exc_info:
            ScriptBuilder("テスト動画").build()
        assert "At least one scene is required" in str(exc_info.value)

    def test_full_example(self):
        """完全な例で構築できること"""
        script = (
            ScriptBuilder("Python入門講座 第1回")
            .description("プログラミング初心者向けのPython入門")
            .add_scene_builder(
                SceneBuilder()
                .visual_path("./assets/title.png")
                .duration(3.0)
                .note("タイトル画面")
            )
            .add_scene_builder(
                SceneBuilder()
                .add_narration("こんにちは！")
                .add_narration("今日からPythonを学んでいきましょう。", pause_after=0.5)
                .visual_path("./assets/intro.png")
            )
            .add_scene_builder(
                SceneBuilder()
                .visual_path("./assets/subscribe.mp4", AssetType.VIDEO)
                .duration(4.0)
                .note("チャンネル登録のお願い")
            )
            .voice(provider="google", language_code="ja-JP", speed=1.0)
            .timing(segment_gap=0.3, scene_gap=0.5)
            .bgm(path="./assets/bgm.mp3", volume=0.2, fade_in=1.0, fade_out=2.0)
            .build()
        )

        assert script.title == "Python入門講座 第1回"
        assert script.description == "プログラミング初心者向けのPython入門"
        assert len(script.scenes) == 3
        assert script.scenes[0].duration == 3.0
        assert len(script.scenes[1].narrations) == 2
        assert script.scenes[2].visual.type == AssetType.VIDEO
        assert script.bgm is not None
