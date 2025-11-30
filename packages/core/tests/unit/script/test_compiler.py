"""Script compiler tests"""

import pytest
import tempfile
import os

from teto_core.script import (
    Script,
    Scene,
    NarrationSegment,
    Visual,
    ScriptCompiler,
    VoiceConfig,
)
from teto_core.script.providers import MockTTSProvider, LocalAssetResolver
from teto_core.script.presets import DefaultLayerPreset, MinimalPreset


class TestScriptCompiler:
    """ScriptCompiler tests"""

    @pytest.fixture
    def simple_script(self) -> Script:
        """シンプルなテスト用Script"""
        return Script(
            title="テスト動画",
            scenes=[
                Scene(
                    narrations=[
                        NarrationSegment(text="こんにちは"),
                        NarrationSegment(text="今日は良い天気ですね"),
                    ],
                    visual=Visual(path="./image1.png"),
                ),
                Scene(
                    narrations=[NarrationSegment(text="さようなら")],
                    visual=Visual(path="./image2.png"),
                ),
            ],
        )

    @pytest.fixture
    def script_with_title_scene(self) -> Script:
        """タイトルシーンを含むテスト用Script"""
        return Script(
            title="テスト動画",
            scenes=[
                Scene(
                    narrations=[],
                    visual=Visual(path="./title.png"),
                    duration=3.0,
                    note="タイトル画面",
                ),
                Scene(
                    narrations=[NarrationSegment(text="本編開始")],
                    visual=Visual(path="./image1.png"),
                ),
            ],
        )

    @pytest.fixture
    def compiler(self) -> ScriptCompiler:
        """テスト用Compiler"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ScriptCompiler(
                tts_provider=MockTTSProvider(),
                asset_resolver=LocalAssetResolver(),
                layer_preset=DefaultLayerPreset(),
                output_dir=tmpdir,
            )

    def test_compile_simple_script(self, simple_script: Script):
        """シンプルなスクリプトをコンパイルできること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = ScriptCompiler(
                tts_provider=MockTTSProvider(),
                asset_resolver=LocalAssetResolver(),
                layer_preset=DefaultLayerPreset(),
                output_dir=tmpdir,
            )

            result = compiler.compile(simple_script)

            # Projectが生成されること
            assert result.project is not None
            assert len(result.project.timeline.video_layers) == 2
            assert len(result.project.timeline.subtitle_layers) == 1

            # 字幕アイテムが正しい数生成されること
            subtitle_layer = result.project.timeline.subtitle_layers[0]
            assert len(subtitle_layer.items) == 3

            # メタデータが正しく生成されること
            assert result.metadata.total_duration > 0
            assert len(result.metadata.scene_timings) == 2
            assert len(result.metadata.generated_assets) == 3

    def test_compile_with_title_scene(self, script_with_title_scene: Script):
        """タイトルシーン（ナレーションなし）を含むスクリプトをコンパイルできること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = ScriptCompiler(
                tts_provider=MockTTSProvider(),
                asset_resolver=LocalAssetResolver(),
                layer_preset=DefaultLayerPreset(),
                output_dir=tmpdir,
            )

            result = compiler.compile(script_with_title_scene)

            # 2つのビデオレイヤーが生成されること
            assert len(result.project.timeline.video_layers) == 2

            # タイトルシーンのセグメントは空
            assert len(result.metadata.scene_timings[0].segments) == 0

            # 本編シーンのセグメントは1つ
            assert len(result.metadata.scene_timings[1].segments) == 1

    def test_narration_audio_files_created(self, simple_script: Script):
        """ナレーション音声ファイルが作成されること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = ScriptCompiler(
                tts_provider=MockTTSProvider(),
                asset_resolver=LocalAssetResolver(),
                layer_preset=DefaultLayerPreset(),
                output_dir=tmpdir,
            )

            result = compiler.compile(simple_script)

            # 音声ファイルが生成されていること
            for asset_path in result.metadata.generated_assets:
                assert os.path.exists(asset_path)

    def test_timing_calculation(self):
        """タイミング計算が正しいこと"""
        script = Script(
            title="テスト",
            scenes=[
                Scene(
                    narrations=[
                        NarrationSegment(text="12345", pause_after=1.0),  # 5文字 = 1秒
                    ],
                    visual=Visual(path="./image.png"),
                    pause_after=0.5,
                ),
                Scene(
                    narrations=[
                        NarrationSegment(text="1234567890"),  # 10文字 = 2秒
                    ],
                    visual=Visual(path="./image2.png"),
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = ScriptCompiler(
                tts_provider=MockTTSProvider(chars_per_second=5.0),
                asset_resolver=LocalAssetResolver(),
                layer_preset=MinimalPreset(),
                output_dir=tmpdir,
            )

            result = compiler.compile(script)

            # シーン1: 1秒 (ナレーション) + 1秒 (pause_after)
            scene1 = result.metadata.scene_timings[0]
            assert scene1.start_time == 0.0
            assert scene1.segments[0].start_time == 0.0
            assert scene1.segments[0].end_time == 1.0

            # シーン2: シーン1終了 + シーン間隔(0.5) から開始
            scene2 = result.metadata.scene_timings[1]
            assert scene2.start_time == pytest.approx(2.5, rel=0.01)

    def test_preset_applied_to_layers(self, simple_script: Script):
        """プリセットがレイヤーに適用されること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = ScriptCompiler(
                tts_provider=MockTTSProvider(),
                asset_resolver=LocalAssetResolver(),
                layer_preset=DefaultLayerPreset(),
                output_dir=tmpdir,
            )

            result = compiler.compile(simple_script)

            # トランジションが適用されていること
            for layer in result.project.timeline.video_layers:
                assert layer.transition is not None
                assert layer.transition.type == "crossfade"

            # 字幕スタイルが適用されていること
            subtitle_layer = result.project.timeline.subtitle_layers[0]
            assert subtitle_layer.font_size == "lg"
            assert subtitle_layer.appearance == "shadow"

    def test_minimal_preset_no_transition(self, simple_script: Script):
        """MinimalPresetではトランジションがないこと"""
        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = ScriptCompiler(
                tts_provider=MockTTSProvider(),
                asset_resolver=LocalAssetResolver(),
                layer_preset=MinimalPreset(),
                output_dir=tmpdir,
            )

            result = compiler.compile(simple_script)

            # トランジションがないこと
            for layer in result.project.timeline.video_layers:
                assert layer.transition is None

    def test_output_config_from_preset(self, simple_script: Script):
        """出力設定がプリセットから取得されること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = ScriptCompiler(
                tts_provider=MockTTSProvider(),
                asset_resolver=LocalAssetResolver(),
                layer_preset=DefaultLayerPreset(),
                output_dir=tmpdir,
            )

            result = compiler.compile(simple_script, output_path="custom_output.mp4")

            assert result.project.output.path == "custom_output.mp4"
            assert result.project.output.width == 1920
            assert result.project.output.height == 1080
            assert result.project.output.fps == 30


class TestLocalAssetResolver:
    """LocalAssetResolver tests"""

    def test_resolve_with_path(self):
        """パスが指定されている場合、そのパスを返すこと"""
        resolver = LocalAssetResolver()
        visual = Visual(path="./image.png")
        assert resolver.resolve(visual) == "./image.png"

    def test_resolve_without_path_raises(self):
        """パスが指定されていない場合、エラーを発生すること"""
        resolver = LocalAssetResolver()
        visual = Visual(description="説明のみ")
        with pytest.raises(ValueError) as exc_info:
            resolver.resolve(visual)
        assert "requires path" in str(exc_info.value)


class TestMockTTSProvider:
    """MockTTSProvider tests"""

    def test_generate(self):
        """ダミーの音声データを生成できること"""
        provider = MockTTSProvider()
        config = VoiceConfig()
        result = provider.generate("テスト", config)

        assert result.audio_content is not None
        assert result.text == "テスト"
        assert result.duration > 0

    def test_estimate_duration(self):
        """音声の長さを推定できること"""
        provider = MockTTSProvider(chars_per_second=5.0)
        config = VoiceConfig(speed=1.0)

        # 10文字 / 5文字/秒 = 2秒
        duration = provider.estimate_duration("1234567890", config)
        assert duration == pytest.approx(2.0, rel=0.01)

    def test_estimate_duration_with_speed(self):
        """話速を考慮して音声の長さを推定できること"""
        provider = MockTTSProvider(chars_per_second=5.0)
        config = VoiceConfig(speed=2.0)

        # 10文字 / 5文字/秒 / 2倍速 = 1秒
        duration = provider.estimate_duration("1234567890", config)
        assert duration == pytest.approx(1.0, rel=0.01)
