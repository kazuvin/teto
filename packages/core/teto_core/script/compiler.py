"""Script Compiler - Script to Project conversion"""

from dataclasses import dataclass, field
from typing import Union

from ..project.models import Project, Timeline
from ..layer.models import (
    VideoLayer,
    ImageLayer,
    AudioLayer,
    SubtitleLayer,
    SubtitleItem,
)
from ..output_config.models import OutputConfig
from ..utils.markup_utils import strip_markup

from .models import Script, Scene, AssetType
from .providers.tts import TTSProvider, TTSResult
from .providers.assets import AssetResolver
from .presets.base import ScenePreset
from .presets.registry import ScenePresetRegistry
from .cache import TTSCacheManager, get_cache_manager


@dataclass
class SegmentTiming:
    """セグメントのタイミング情報"""

    segment_index: int
    start_time: float
    end_time: float
    narration_path: str
    text: str


@dataclass
class SceneTiming:
    """シーンのタイミング情報"""

    scene_index: int
    start_time: float
    end_time: float
    segments: list[SegmentTiming] = field(default_factory=list)


@dataclass
class CompileMetadata:
    """コンパイルメタデータ"""

    total_duration: float
    scene_timings: list[SceneTiming]
    generated_assets: list[str]


@dataclass
class CompileResult:
    """コンパイル結果"""

    project: Project
    metadata: CompileMetadata


class ScriptCompiler:
    """Script → Project 変換（Template Method + Strategy）"""

    def __init__(
        self,
        tts_provider: TTSProvider,
        asset_resolver: AssetResolver,
        output_dir: str = "./output",
        cache_manager: TTSCacheManager | None = None,
        use_cache: bool = True,
    ):
        """ScriptCompilerを初期化する

        Args:
            tts_provider: TTSプロバイダー
            asset_resolver: アセット解決プロバイダー
            output_dir: 出力ディレクトリ
            cache_manager: TTSキャッシュマネージャー（Noneの場合はデフォルト）
            use_cache: キャッシュを使用するか

        Note:
            - 出力設定と字幕スタイルは Script から直接取得
            - シーン毎のエフェクト・トランジションは Scene.preset または Script.default_preset から取得
        """
        self._tts = tts_provider
        self._assets = asset_resolver
        self._output_dir = output_dir
        self._cache = cache_manager or get_cache_manager()
        self._use_cache = use_cache

    def _get_preset_for_scene(self, script: Script, scene: Scene) -> ScenePreset:
        """シーンに適用するプリセットを取得

        Args:
            script: 台本（デフォルトプリセット情報を含む）
            scene: シーン

        Returns:
            ScenePreset: 適用するプリセット
        """
        preset_name = scene.preset or script.default_preset
        return ScenePresetRegistry.get(preset_name)

    def _resolve_scene_voice(self, script: Script, scene: Scene):
        """シーンに適用する音声設定を解決

        優先順位:
        1. scene.voice（直接指定）
        2. scene.voice_profile（名前付きプロファイル参照）
        3. script.voice（グローバルデフォルト）

        Args:
            script: 台本
            scene: シーン

        Returns:
            VoiceConfig: 適用する音声設定

        Raises:
            ValueError: voice_profile が見つからない場合
        """

        # 1. 直接指定
        if scene.voice is not None:
            return scene.voice

        # 2. プロファイル参照
        if scene.voice_profile is not None:
            if (
                script.voice_profiles is None
                or scene.voice_profile not in script.voice_profiles
            ):
                raise ValueError(
                    f"ボイスプロファイル '{scene.voice_profile}' が見つかりません。"
                    f"Script.voice_profiles に定義してください。"
                )
            return script.voice_profiles[scene.voice_profile]

        # 3. グローバルデフォルト
        return script.voice

    def compile(self, script: Script, output_path: str = "output.mp4") -> CompileResult:
        """Script を Project に変換する（Template Method）

        Args:
            script: 変換する台本
            output_path: 出力ファイルパス

        Returns:
            CompileResult: 変換結果（Projectとメタデータ）
        """
        # 1. 準備
        self._prepare(script)

        # 2. 全セグメントのナレーション音声を生成
        narrations = self._generate_all_narrations(script)

        # 3. タイムラインを計算（間隔を考慮）
        scene_timings = self._calculate_timings(script, narrations)

        # 4. 各レイヤーを生成
        video_layers = self._build_video_layers(script, scene_timings)
        audio_layers = self._build_audio_layers(script, scene_timings, narrations)
        subtitle_layers = self._build_subtitle_layers(script, scene_timings)

        # 5. Project を組み立て
        project = self._assemble_project(
            script, video_layers, audio_layers, subtitle_layers, output_path
        )

        # 6. メタデータ作成
        metadata = self._create_metadata(scene_timings, narrations)

        return CompileResult(project=project, metadata=metadata)

    def _prepare(self, script: Script) -> None:
        """前処理"""
        import os

        os.makedirs(self._output_dir, exist_ok=True)
        os.makedirs(f"{self._output_dir}/narrations", exist_ok=True)

    def _generate_all_narrations(self, script: Script) -> list[list[TTSResult]]:
        """全シーン・全セグメントのナレーションを生成"""
        all_narrations: list[list[TTSResult]] = []

        cache_hits = 0
        cache_misses = 0

        for scene_idx, scene in enumerate(script.scenes):
            scene_narrations: list[TTSResult] = []

            # シーン固有のvoice設定を解決
            effective_voice = self._resolve_scene_voice(script, scene)

            # プロバイダーに応じて拡張子を決定
            audio_ext = ".wav" if effective_voice.provider == "gemini" else ".mp3"

            for seg_idx, segment in enumerate(scene.narrations):
                # マークアップを除去したテキストをTTSに渡す
                plain_text = strip_markup(segment.text)

                # キャッシュをチェック
                cached_audio = None
                if self._use_cache:
                    cached_audio = self._cache.get(
                        plain_text, effective_voice, audio_ext
                    )

                if cached_audio is not None:
                    # キャッシュヒット
                    cache_hits += 1
                    duration = self._tts.estimate_duration(plain_text, effective_voice)
                    result = TTSResult(
                        audio_content=cached_audio,
                        duration=duration,
                        text=plain_text,
                    )
                else:
                    # キャッシュミス - TTS生成
                    cache_misses += 1
                    result = self._tts.generate(
                        text=plain_text,
                        config=effective_voice,
                    )
                    # キャッシュに保存
                    if self._use_cache:
                        self._cache.put(
                            plain_text, effective_voice, audio_ext, result.audio_content
                        )

                # 音声ファイルを保存
                output_path = (
                    f"{self._output_dir}/narrations/"
                    f"scene_{scene_idx:03d}_seg_{seg_idx:03d}{audio_ext}"
                )
                result.save(output_path)
                scene_narrations.append(result)
            all_narrations.append(scene_narrations)

        # キャッシュ統計を表示
        total = cache_hits + cache_misses
        if total > 0:
            print(
                f"  TTS キャッシュ: {cache_hits}/{total} ヒット "
                f"({cache_hits * 100 // total}%)"
            )

        return all_narrations

    def _calculate_timings(
        self,
        script: Script,
        all_narrations: list[list[TTSResult]],
    ) -> list[SceneTiming]:
        """タイミングを計算（間隔を考慮）"""
        scene_timings: list[SceneTiming] = []
        current_time = 0.0
        timing_config = script.timing
        padding = timing_config.subtitle_padding

        for scene_idx, scene in enumerate(script.scenes):
            scene_narrations = all_narrations[scene_idx]
            scene_start = current_time
            segment_timings: list[SegmentTiming] = []

            if len(scene.narrations) == 0:
                # ナレーションなしのシーン（タイトル、見出し等）
                # duration は Scene のバリデーションで必須チェック済み
                assert scene.duration is not None
                scene_end = current_time + scene.duration
                current_time = scene_end
            else:
                # ナレーションありのシーン
                for seg_idx, (segment, narration) in enumerate(
                    zip(scene.narrations, scene_narrations)
                ):
                    # padding 分遅らせて開始
                    seg_start = current_time + padding
                    seg_end = seg_start + narration.duration

                    segment_timings.append(
                        SegmentTiming(
                            segment_index=seg_idx,
                            start_time=seg_start,
                            end_time=seg_end,
                            narration_path=narration.path or "",
                            text=segment.text,
                        )
                    )

                    # 音声終了後に padding を追加
                    current_time = seg_end + padding

                    # セグメント後の間隔を追加
                    gap = segment.pause_after
                    if gap == 0 and seg_idx < len(scene.narrations) - 1:
                        # 明示的な指定がなければデフォルト間隔を使用
                        gap = timing_config.default_segment_gap
                    current_time += gap

                scene_end = current_time

            scene_timings.append(
                SceneTiming(
                    scene_index=scene_idx,
                    start_time=scene_start,
                    end_time=scene_end,
                    segments=segment_timings,
                )
            )

            # シーン後の間隔を追加
            scene_gap = scene.pause_after
            if scene_gap == 0 and scene_idx < len(script.scenes) - 1:
                scene_gap = timing_config.default_scene_gap
            current_time += scene_gap

        return scene_timings

    def _build_video_layers(
        self,
        script: Script,
        scene_timings: list[SceneTiming],
    ) -> list[Union[VideoLayer, ImageLayer]]:
        """映像レイヤーを構築"""
        layers: list[Union[VideoLayer, ImageLayer]] = []

        for i, (scene, timing) in enumerate(zip(script.scenes, scene_timings)):
            # シーン毎にプリセットを取得
            preset = self._get_preset_for_scene(script, scene)

            asset_path = self._assets.resolve(scene.visual)
            # トランジションはシーンから直接取得
            transition = scene.transition

            # 次のシーンの開始時刻までを duration とする（gap を含める）
            # トランジションの overlap 分も追加（VideoProcessor で引かれるため）
            # 最後のシーンはそのままの duration を使用
            if i < len(scene_timings) - 1:
                next_timing = scene_timings[i + 1]
                base_duration = next_timing.start_time - timing.start_time
                # トランジションがある場合、overlap 分を追加
                overlap = transition.duration if transition else 0
                duration = base_duration + overlap
            else:
                duration = timing.end_time - timing.start_time

            if scene.visual.type == AssetType.VIDEO:
                effects = preset.get_video_effects()
                # mute_video が True の場合は音量を 0 に設定
                volume = 0.0 if scene.mute_video else 1.0
                layer: Union[VideoLayer, ImageLayer] = VideoLayer(
                    path=asset_path,
                    duration=duration,
                    effects=effects,
                    transition=transition,
                    volume=volume,
                )
            else:
                effects = preset.get_image_effects()
                layer = ImageLayer(
                    path=asset_path,
                    duration=duration,
                    effects=effects,
                    transition=transition,
                )

            layers.append(layer)

        return layers

    def _build_audio_layers(
        self,
        script: Script,
        scene_timings: list[SceneTiming],
        all_narrations: list[list[TTSResult]],
    ) -> list[AudioLayer]:
        """音声レイヤーを構築"""
        layers: list[AudioLayer] = []

        # ナレーション音声（padding は _calculate_timings で考慮済み）
        for scene_timing in scene_timings:
            for segment in scene_timing.segments:
                layers.append(
                    AudioLayer(
                        path=segment.narration_path,
                        start_time=segment.start_time,
                        volume=1.0,
                    )
                )

        # 効果音（シーン毎に処理）
        for scene, scene_timing in zip(script.scenes, scene_timings):
            for se in scene.sound_effects:
                # シーン開始時刻 + オフセット で再生タイミングを計算
                start_time = scene_timing.start_time + se.offset
                layers.append(
                    AudioLayer(
                        path=se.path,
                        start_time=start_time,
                        volume=se.volume,
                    )
                )

        # BGM
        if script.bgm:
            total_duration = scene_timings[-1].end_time
            layers.append(
                AudioLayer(
                    path=script.bgm.path,
                    start_time=0.0,
                    duration=total_duration,
                    volume=script.bgm.volume,
                    # NOTE: fade_in/fade_out は AudioLayer 拡張後に対応
                )
            )

        return layers

    def _build_subtitle_layers(
        self,
        script: Script,
        scene_timings: list[SceneTiming],
    ) -> list[SubtitleLayer]:
        """字幕レイヤーを構築"""
        items: list[SubtitleItem] = []

        # padding は _calculate_timings で考慮済み
        for scene_timing in scene_timings:
            for segment in scene_timing.segments:
                items.append(
                    SubtitleItem(
                        text=segment.text,
                        start_time=segment.start_time,
                        end_time=segment.end_time,
                    )
                )

        # 字幕がない場合は空リストを返す
        if not items:
            return []

        # 字幕スタイルは Script から直接取得
        style = script.subtitle_style

        # styles の優先順位: Script.subtitle_styles > Script.subtitle_style.styles
        styles = script.subtitle_styles if script.subtitle_styles else style.styles

        return [
            SubtitleLayer(
                items=items,
                styles=styles,
                font_size=style.font_size,
                font_color=style.font_color,
                google_font=style.google_font,
                font_weight=style.font_weight,
                stroke_width=style.stroke_width,
                stroke_color=style.stroke_color,
                outer_stroke_width=style.outer_stroke_width,
                outer_stroke_color=style.outer_stroke_color,
                bg_color=style.bg_color,
                position=style.position,
                appearance=style.appearance,
            )
        ]

    def _assemble_project(
        self,
        script: Script,
        video_layers: list[Union[VideoLayer, ImageLayer]],
        audio_layers: list[AudioLayer],
        subtitle_layers: list[SubtitleLayer],
        output_path: str,
    ) -> Project:
        """Project を組み立て"""
        # 出力設定は Script から直接取得
        # 配列の場合は最初の要素を使用（複数出力は generate_multi で処理）
        if isinstance(script.output, list):
            output_settings = script.output[0] if script.output else None
            if output_settings is None:
                raise ValueError("output が空の配列です")
        else:
            output_settings = script.output

        output_config = OutputConfig.from_settings(output_settings, output_path)

        return Project(
            output=output_config,
            timeline=Timeline(
                video_layers=video_layers,
                audio_layers=audio_layers,
                subtitle_layers=subtitle_layers,
            ),
        )

    def _create_metadata(
        self,
        scene_timings: list[SceneTiming],
        all_narrations: list[list[TTSResult]],
    ) -> CompileMetadata:
        """メタデータを作成"""
        generated: list[str] = []
        for scene_narrations in all_narrations:
            for narration in scene_narrations:
                if narration.path:
                    generated.append(narration.path)

        total_duration = scene_timings[-1].end_time if scene_timings else 0.0

        return CompileMetadata(
            total_duration=total_duration,
            scene_timings=scene_timings,
            generated_assets=generated,
        )
