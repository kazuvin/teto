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
from ..utils.markup_utils import strip_markup

from .models import Script, AssetType
from .providers.tts import TTSProvider, TTSResult
from .providers.assets import AssetResolver
from .presets.base import LayerPreset


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
        layer_preset: LayerPreset,
        output_dir: str = "./output",
    ):
        """ScriptCompilerを初期化する

        Args:
            tts_provider: TTSプロバイダー
            asset_resolver: アセット解決プロバイダー
            layer_preset: レイヤー設定プリセット
            output_dir: 出力ディレクトリ
        """
        self._tts = tts_provider
        self._assets = asset_resolver
        self._preset = layer_preset
        self._output_dir = output_dir

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
            video_layers, audio_layers, subtitle_layers, output_path
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

        for scene_idx, scene in enumerate(script.scenes):
            scene_narrations: list[TTSResult] = []
            for seg_idx, segment in enumerate(scene.narrations):
                # マークアップを除去したテキストをTTSに渡す
                plain_text = strip_markup(segment.text)
                result = self._tts.generate(
                    text=plain_text,
                    config=script.voice,
                )
                # 音声ファイルを保存
                output_path = (
                    f"{self._output_dir}/narrations/"
                    f"scene_{scene_idx:03d}_seg_{seg_idx:03d}.mp3"
                )
                result.save(output_path)
                scene_narrations.append(result)
            all_narrations.append(scene_narrations)

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
                    seg_start = current_time
                    seg_end = current_time + narration.duration

                    segment_timings.append(
                        SegmentTiming(
                            segment_index=seg_idx,
                            start_time=seg_start,
                            end_time=seg_end,
                            narration_path=narration.path or "",
                            text=segment.text,
                        )
                    )

                    current_time = seg_end

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

        for scene, timing in zip(script.scenes, scene_timings):
            asset_path = self._assets.resolve(scene.visual)
            duration = timing.end_time - timing.start_time

            if scene.visual.type == AssetType.VIDEO:
                effects = self._preset.get_video_effects()
                layer: Union[VideoLayer, ImageLayer] = VideoLayer(
                    path=asset_path,
                    duration=duration,
                    effects=effects,
                    transition=self._preset.get_transition(),
                )
            else:
                effects = self._preset.get_image_effects()
                layer = ImageLayer(
                    path=asset_path,
                    duration=duration,
                    effects=effects,
                    transition=self._preset.get_transition(),
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

        # ナレーション音声
        for scene_timing in scene_timings:
            for segment in scene_timing.segments:
                layers.append(
                    AudioLayer(
                        path=segment.narration_path,
                        start_time=segment.start_time,
                        volume=1.0,
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
        padding = script.timing.subtitle_padding

        for scene_timing in scene_timings:
            for segment in scene_timing.segments:
                items.append(
                    SubtitleItem(
                        text=segment.text,
                        start_time=segment.start_time + padding,
                        end_time=segment.end_time - padding,
                    )
                )

        # 字幕がない場合は空リストを返す
        if not items:
            return []

        style = self._preset.get_subtitle_style()

        # styles の優先順位: Script > プリセット
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
        video_layers: list[Union[VideoLayer, ImageLayer]],
        audio_layers: list[AudioLayer],
        subtitle_layers: list[SubtitleLayer],
        output_path: str,
    ) -> Project:
        """Project を組み立て"""
        return Project(
            output=self._preset.get_output_config(output_path),
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
