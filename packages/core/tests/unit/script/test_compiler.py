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
                output_dir=tmpdir,
            )

    def test_compile_simple_script(self, simple_script: Script):
        """シンプルなスクリプトをコンパイルできること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = ScriptCompiler(
                tts_provider=MockTTSProvider(),
                asset_resolver=LocalAssetResolver(),
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
            default_effect="default",
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
                output_dir=tmpdir,
            )

            result = compiler.compile(script)

            # シーン1: ナレーション1秒 + pause_after 1秒
            scene1 = result.metadata.scene_timings[0]
            # セグメントの開始時刻を取得
            seg1_start = scene1.segments[0].start_time
            seg1_end = scene1.segments[0].end_time
            # ナレーション時間は1秒 (5文字 / 5文字秒)
            assert seg1_end - seg1_start == pytest.approx(1.0, rel=0.01)

            # シーン2が開始されていること
            scene2 = result.metadata.scene_timings[1]
            assert scene2.start_time > scene1.start_time

    def test_preset_applied_to_layers(self, simple_script: Script):
        """プリセットがレイヤーに適用されること（default_effect="default"がデフォルト）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = ScriptCompiler(
                tts_provider=MockTTSProvider(),
                asset_resolver=LocalAssetResolver(),
                output_dir=tmpdir,
            )

            result = compiler.compile(simple_script)

            # トランジションはシーンに設定がないためNone
            for layer in result.project.timeline.video_layers:
                assert layer.transition is None

            # 字幕スタイルはScript.subtitle_styleから取得（デフォルト値）
            subtitle_layer = result.project.timeline.subtitle_layers[0]
            assert subtitle_layer.font_size == "base"
            assert subtitle_layer.appearance == "background"

    def test_scene_transition(self):
        """シーン毎にトランジションを設定できること"""
        from teto_core.effect.models import TransitionConfig

        script = Script(
            title="テスト動画",
            scenes=[
                Scene(
                    narrations=[
                        NarrationSegment(text="こんにちは"),
                        NarrationSegment(text="今日は良い天気ですね"),
                    ],
                    visual=Visual(path="./image1.png"),
                    transition=TransitionConfig(type="crossfade", duration=0.5),
                ),
                Scene(
                    narrations=[NarrationSegment(text="さようなら")],
                    visual=Visual(path="./image2.png"),
                    transition=TransitionConfig(type="crossfade", duration=0.15),
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = ScriptCompiler(
                tts_provider=MockTTSProvider(),
                asset_resolver=LocalAssetResolver(),
                output_dir=tmpdir,
            )

            result = compiler.compile(script)

            # シーン1: crossfade 0.5秒
            layer1 = result.project.timeline.video_layers[0]
            assert layer1.transition is not None
            assert layer1.transition.type == "crossfade"
            assert layer1.transition.duration == 0.5

            # シーン2: crossfade 0.15秒
            layer2 = result.project.timeline.video_layers[1]
            assert layer2.transition is not None
            assert layer2.transition.type == "crossfade"
            assert layer2.transition.duration == 0.15

    def test_output_config_from_preset(self, simple_script: Script):
        """出力設定がdefault_presetから取得されること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = ScriptCompiler(
                tts_provider=MockTTSProvider(),
                asset_resolver=LocalAssetResolver(),
                output_dir=tmpdir,
            )

            result = compiler.compile(simple_script, output_path="custom_output.mp4")

            # DefaultLayerPreset (default_effect="default") の設定
            assert result.project.output.path == "custom_output.mp4"
            assert result.project.output.width == 1920
            assert result.project.output.height == 1080
            assert result.project.output.fps == 30

    def test_scene_level_preset_with_transition(self):
        """シーン毎に異なるエフェクトプリセットとトランジションを適用できること"""
        from teto_core.effect.models import TransitionConfig

        script = Script(
            title="シーン毎エフェクトプリセットテスト",
            default_effect="default",
            scenes=[
                Scene(
                    narrations=[NarrationSegment(text="デフォルト")],
                    visual=Visual(path="./image1.png"),
                    transition=TransitionConfig(type="crossfade", duration=0.5),
                    # effect未指定 → default_effect ("default") を使用
                ),
                Scene(
                    narrations=[NarrationSegment(text="ドラマティック")],
                    visual=Visual(path="./image2.png"),
                    effect="dramatic",  # dramatic エフェクトプリセットを使用
                    transition=TransitionConfig(type="crossfade", duration=0.15),
                ),
                Scene(
                    narrations=[NarrationSegment(text="またデフォルト")],
                    visual=Visual(path="./image3.png"),
                    transition=TransitionConfig(type="crossfade", duration=0.5),
                    # effect未指定 → default_effect を使用
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = ScriptCompiler(
                tts_provider=MockTTSProvider(),
                asset_resolver=LocalAssetResolver(),
                output_dir=tmpdir,
            )

            result = compiler.compile(script)

            # 3つのビデオレイヤーが生成されること
            assert len(result.project.timeline.video_layers) == 3

            # シーン1: crossfade トランジション (0.5秒)
            layer1 = result.project.timeline.video_layers[0]
            assert layer1.transition is not None
            assert layer1.transition.type == "crossfade"
            assert layer1.transition.duration == 0.5

            # シーン2: crossfade トランジション (0.15秒)
            layer2 = result.project.timeline.video_layers[1]
            assert layer2.transition is not None
            assert layer2.transition.type == "crossfade"
            assert layer2.transition.duration == 0.15

            # シーン3: crossfade トランジション (0.5秒)
            layer3 = result.project.timeline.video_layers[2]
            assert layer3.transition is not None
            assert layer3.transition.type == "crossfade"
            assert layer3.transition.duration == 0.5

    def test_scene_level_preset_with_different_effects(self):
        """シーン毎のエフェクトプリセットでエフェクトが正しく適用されること"""
        script = Script(
            title="エフェクトテスト",
            default_effect="default",  # デフォルトはdefault（エフェクトなし）
            scenes=[
                Scene(
                    narrations=[NarrationSegment(text="シーン1")],
                    visual=Visual(path="./image1.png"),
                    effect="dramatic",  # dramatic エフェクトプリセット（glitch + colorGrade）
                ),
                Scene(
                    narrations=[NarrationSegment(text="シーン2")],
                    visual=Visual(path="./image2.png"),
                    # effect未指定 → default（エフェクトなし）
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = ScriptCompiler(
                tts_provider=MockTTSProvider(),
                asset_resolver=LocalAssetResolver(),
                output_dir=tmpdir,
            )

            result = compiler.compile(script)

            # シーン1: dramatic プリセット → glitch + colorGrade エフェクト
            layer1 = result.project.timeline.video_layers[0]
            assert len(layer1.effects) == 2
            assert layer1.effects[0].type == "glitch"
            assert layer1.effects[1].type == "colorGrade"

            # シーン2: default プリセット → エフェクトなし
            layer2 = result.project.timeline.video_layers[1]
            assert len(layer2.effects) == 0

    def test_subtitle_style_from_script(self):
        """字幕スタイルはScript.subtitle_styleから取得されること（プリセットに関係なく）"""
        from teto_core.script.presets.base import SubtitleStyleConfig

        script = Script(
            title="字幕スタイルテスト",
            default_effect="default",
            subtitle_style=SubtitleStyleConfig(
                font_size="xl",
                appearance="shadow",
                font_weight="bold",
            ),
            scenes=[
                Scene(
                    narrations=[NarrationSegment(text="シーン1")],
                    visual=Visual(path="./image1.png"),
                    preset="dramatic",
                ),
                Scene(
                    narrations=[NarrationSegment(text="シーン2")],
                    visual=Visual(path="./image2.png"),
                    preset="slideshow",
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = ScriptCompiler(
                tts_provider=MockTTSProvider(),
                asset_resolver=LocalAssetResolver(),
                output_dir=tmpdir,
            )

            result = compiler.compile(script)

            # 字幕スタイルはScript.subtitle_styleから取得される
            subtitle_layer = result.project.timeline.subtitle_layers[0]
            assert subtitle_layer.font_size == "xl"
            assert subtitle_layer.appearance == "shadow"
            assert subtitle_layer.font_weight == "bold"

    def test_output_config_from_script(self):
        """出力設定はScript.outputから取得されること（プリセットに関係なく）"""
        from teto_core.output_config.models import OutputSettings

        script = Script(
            title="出力設定テスト",
            default_effect="default",
            output=OutputSettings(
                width=1080,
                height=1920,
                fps=60,
            ),
            scenes=[
                Scene(
                    narrations=[NarrationSegment(text="シーン1")],
                    visual=Visual(path="./image1.png"),
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = ScriptCompiler(
                tts_provider=MockTTSProvider(),
                asset_resolver=LocalAssetResolver(),
                output_dir=tmpdir,
            )

            result = compiler.compile(script)

            # 出力設定はScript.outputから取得される
            assert result.project.output.width == 1080
            assert result.project.output.height == 1920
            assert result.project.output.fps == 60

    def test_mute_video_option(self):
        """mute_video オプションで動画の音声をミュートできること"""
        script = Script(
            title="ミュートテスト",
            default_effect="default",
            scenes=[
                Scene(
                    narrations=[NarrationSegment(text="シーン1")],
                    visual=Visual(path="./video1.mp4"),
                    mute_video=True,  # 動画の音声をミュート
                ),
                Scene(
                    narrations=[NarrationSegment(text="シーン2")],
                    visual=Visual(path="./video2.mp4"),
                    # mute_video=False がデフォルト
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = ScriptCompiler(
                tts_provider=MockTTSProvider(),
                asset_resolver=LocalAssetResolver(),
                output_dir=tmpdir,
            )

            result = compiler.compile(script)

            # シーン1: mute_video=True → volume=0.0
            layer1 = result.project.timeline.video_layers[0]
            assert layer1.volume == 0.0

            # シーン2: mute_video=False（デフォルト） → volume=1.0
            layer2 = result.project.timeline.video_layers[1]
            assert layer2.volume == 1.0


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
