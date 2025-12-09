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
    CharacterLayer,
    CharacterPositionPreset,
    CharacterAnimationConfig,
    CharacterAnimationType,
)
from ..output_config.models import OutputConfig
from ..utils.markup_utils import strip_markup

from .models import Script, Scene, AssetType
from .providers.tts import TTSProvider, TTSResult
from .providers.assets import AssetResolver
from .effects.base import EffectPreset
from .effects.registry import EffectPresetRegistry
from .presets.composite import PresetRegistry
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

        # デフォルト複合プリセットを登録
        self._register_default_presets()

    def _register_default_presets(self) -> None:
        """デフォルト複合プリセットを登録"""
        from .presets.library import register_default_composite_presets

        register_default_composite_presets()

    def _get_effect_preset_for_scene(
        self, script: Script, scene: Scene
    ) -> EffectPreset:
        """シーンに適用するエフェクトプリセットを取得

        Args:
            script: 台本（デフォルトエフェクト情報を含む）
            scene: シーン

        Returns:
            EffectPreset: 適用するエフェクトプリセット
        """
        preset_name = scene.effect or script.default_effect
        return EffectPresetRegistry.get(preset_name)

    def _get_composite_preset_for_scene(self, script: Script, scene: Scene):
        """シーンに適用する複合プリセットを取得

        Args:
            script: 台本（デフォルト複合プリセット情報を含む）
            scene: シーン

        Returns:
            PresetConfig | None: 適用する複合プリセット（なければNone）
        """
        preset_name = scene.preset or script.default_preset
        if preset_name is None:
            return None
        return PresetRegistry.get(preset_name)

    def _apply_composite_presets(self, script: Script) -> Script:
        """複合プリセットを全シーンとスクリプトに適用

        各シーンの複合プリセット設定を展開し、シーン固有設定を上書きする。
        優先順位:
        - effect: scene.effect > preset.effect > script.default_effect
        - transition: scene.transition > preset.transition

        Note:
            subtitle_style と timing_override はシーン毎に異なる可能性があるため、
            グローバル設定には適用しない。これらはシーン毎のプリセットから
            _build_subtitle_layers と _calculate_timings で個別に適用される。

        Args:
            script: 台本

        Returns:
            Script: 複合プリセットが適用された新しい台本
        """
        script_dict = script.model_dump()
        updated_scenes = []

        for scene in script.scenes:
            # 複合プリセット名を取得（優先順位: scene.preset > script.default_preset）
            preset_name = scene.preset or script.default_preset

            if preset_name is None:
                # 複合プリセット指定なし - そのまま追加
                updated_scenes.append(scene)
                continue

            # 複合プリセットを取得
            preset = PresetRegistry.get(preset_name)
            if preset is None:
                # プリセットが見つからない - そのまま追加
                updated_scenes.append(scene)
                continue

            # シーンのコピーを作成
            scene_dict = scene.model_dump()

            # 1. エフェクトを適用（シーンに指定がない場合のみ）
            if scene.effect is None and preset.effect is not None:
                scene_dict["effect"] = preset.effect

            # 2. トランジション設定を適用（シーンに指定がない場合のみ）
            if scene.transition is None and preset.transition is not None:
                scene_dict["transition"] = preset.transition

            updated_scenes.append(Scene.model_validate(scene_dict))

        script_dict["scenes"] = updated_scenes
        return Script.model_validate(script_dict)

    def _resolve_segment_voice(self, script: Script, segment):
        """ナレーションセグメントに適用する音声設定を解決

        優先順位:
        1. segment.voice（直接指定）
        2. segment.voice_profile（名前付きプロファイル参照）
        3. キャラクターの voice_profile（character_states から取得）
        4. script.voice（グローバルデフォルト）

        Args:
            script: 台本
            segment: ナレーションセグメント

        Returns:
            VoiceConfig: 適用する音声設定

        Raises:
            ValueError: voice_profile が見つからない場合
        """

        # 1. 直接指定
        if segment.voice is not None:
            return segment.voice

        # 2. プロファイル参照
        if segment.voice_profile is not None:
            if (
                script.voice_profiles is None
                or segment.voice_profile not in script.voice_profiles
            ):
                raise ValueError(
                    f"ボイスプロファイル '{segment.voice_profile}' が見つかりません。"
                    f"Script.voice_profiles に定義してください。"
                )
            return script.voice_profiles[segment.voice_profile]

        # 3. キャラクターの voice_profile（最初の visible なキャラクターから取得）
        if script.characters and segment.character_states:
            for char_state in segment.character_states:
                # 非表示のキャラクターはスキップ
                if not char_state.visible:
                    continue

                char_id = char_state.character_id
                if char_id in script.characters:
                    char_def = script.characters[char_id]
                    if char_def.voice_profile is not None:
                        if (
                            script.voice_profiles is None
                            or char_def.voice_profile not in script.voice_profiles
                        ):
                            raise ValueError(
                                f"キャラクター '{char_id}' の voice_profile "
                                f"'{char_def.voice_profile}' が見つかりません。"
                                f"Script.voice_profiles に定義してください。"
                            )
                        return script.voice_profiles[char_def.voice_profile]

        # 4. グローバルデフォルト
        return script.voice

    def compile(self, script: Script, output_path: str = "output.mp4") -> CompileResult:
        """Script を Project に変換する（Template Method）

        Args:
            script: 変換する台本
            output_path: 出力ファイルパス

        Returns:
            CompileResult: 変換結果（Projectとメタデータ）
        """
        # 0. 複合プリセットを適用
        script = self._apply_composite_presets(script)

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
        character_layers = self._build_character_layers(script, scene_timings)

        # 5. Project を組み立て
        project = self._assemble_project(
            script,
            video_layers,
            audio_layers,
            subtitle_layers,
            character_layers,
            output_path,
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

            for seg_idx, segment in enumerate(scene.narrations):
                # セグメント固有のvoice設定を解決
                effective_voice = self._resolve_segment_voice(script, segment)

                # プロバイダーに応じて拡張子を決定
                audio_ext = ".wav" if effective_voice.provider == "gemini" else ".mp3"

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
        """タイミングを計算（間隔を考慮）

        シーン毎の複合プリセットで timing_override が指定されている場合、
        そのシーンではオーバーライドされたタイミング設定を使用する。
        """
        scene_timings: list[SceneTiming] = []
        current_time = 0.0
        default_timing = script.timing

        for scene_idx, scene in enumerate(script.scenes):
            scene_narrations = all_narrations[scene_idx]
            scene_start = current_time
            segment_timings: list[SegmentTiming] = []

            # シーン毎のプリセットからタイミング設定を取得
            composite_preset = self._get_composite_preset_for_scene(script, scene)
            if composite_preset and composite_preset.timing_override:
                timing_config = composite_preset.timing_override
            else:
                timing_config = default_timing

            padding = timing_config.subtitle_padding

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
            # シーン毎にエフェクトプリセットを取得
            preset = self._get_effect_preset_for_scene(script, scene)

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

        # BGM（優先順位: bgm_sections > bgm）
        if script.bgm_sections:
            # シーン範囲BGM（複数BGMの切り替え）
            for section in script.bgm_sections:
                # シーン範囲の検証
                start_scene_idx = section.scene_range.from_
                end_scene_idx = section.scene_range.to

                if start_scene_idx >= len(scene_timings):
                    # 開始シーンが範囲外の場合はスキップ
                    continue

                # 終了シーンが範囲外の場合は最後のシーンに調整
                if end_scene_idx >= len(scene_timings):
                    end_scene_idx = len(scene_timings) - 1

                # シーン範囲から開始・終了時刻を計算
                start_time = scene_timings[start_scene_idx].start_time
                end_time = scene_timings[end_scene_idx].end_time
                duration = end_time - start_time

                layers.append(
                    AudioLayer(
                        path=section.path,
                        start_time=start_time,
                        duration=duration,
                        volume=section.volume,
                        # NOTE: fade_in/fade_out, loop は AudioLayer 拡張後に対応
                    )
                )
        elif script.bgm:
            # グローバルBGM（後方互換性）
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
        """字幕レイヤーを構築

        字幕スタイルの優先順位:
        1. セグメントの character_states で指定されたキャラクターの subtitle_style
        2. シーンの複合プリセットで指定された subtitle_style
        3. Script のグローバル subtitle_style

        同じスタイルを持つ連続したセグメントは1つの SubtitleLayer にまとめる。
        """
        default_style = script.subtitle_style
        # styles の優先順位: Script.subtitle_styles > Script.subtitle_style.styles
        default_styles = (
            script.subtitle_styles if script.subtitle_styles else default_style.styles
        )

        # セグメント毎にスタイルを決定し、グループ化
        layers: list[SubtitleLayer] = []
        current_style_key = None
        current_style = None
        current_items: list[SubtitleItem] = []

        for scene_idx, (scene, scene_timing) in enumerate(
            zip(script.scenes, scene_timings)
        ):
            # シーン毎のプリセットから字幕スタイルを取得
            composite_preset = self._get_composite_preset_for_scene(script, scene)
            scene_style = (
                composite_preset.subtitle_style
                if composite_preset and composite_preset.subtitle_style
                else default_style
            )

            # このシーンの字幕アイテムを追加（セグメント単位でスタイルを決定）
            for seg_idx, segment_timing in enumerate(scene_timing.segments):
                segment = scene.narrations[seg_idx]

                # セグメントのスタイルを決定（キャラクター > シーン > グローバル）
                style = self._resolve_segment_subtitle_style(
                    script, segment, scene_style
                )

                # スタイルの識別キーを作成
                style_key = self._get_style_key(style)

                # スタイルが変わった場合、現在のグループを保存して新しいグループを開始
                if current_style_key is not None and style_key != current_style_key:
                    if current_items:
                        layers.append(
                            self._create_subtitle_layer(
                                current_items, current_style, default_styles
                            )
                        )
                    current_items = []

                current_style_key = style_key
                current_style = style

                current_items.append(
                    SubtitleItem(
                        text=segment_timing.text,
                        start_time=segment_timing.start_time,
                        end_time=segment_timing.end_time,
                    )
                )

        # 最後のグループを保存
        if current_items and current_style is not None:
            layers.append(
                self._create_subtitle_layer(
                    current_items, current_style, default_styles
                )
            )

        return layers

    def _resolve_segment_subtitle_style(self, script: Script, segment, scene_style):
        """セグメントに適用する字幕スタイルを解決

        優先順位:
        1. キャラクターの subtitle_style（最初の visible なキャラクターから取得）
        2. シーンのスタイル（プリセット or グローバル）

        Args:
            script: 台本
            segment: ナレーションセグメント
            scene_style: シーンレベルのスタイル

        Returns:
            SubtitleStyleConfig: 適用する字幕スタイル
        """
        # キャラクターの subtitle_style を探す
        if script.characters and segment.character_states:
            for char_state in segment.character_states:
                if not char_state.visible:
                    continue
                char_id = char_state.character_id
                if char_id in script.characters:
                    char_def = script.characters[char_id]
                    if char_def.subtitle_style is not None:
                        return char_def.subtitle_style

        # キャラクター指定がない場合はシーンスタイル
        return scene_style

    def _get_style_key(self, style) -> tuple:
        """スタイルの識別キーを作成"""
        return (
            style.font_size,
            style.font_color,
            style.google_font,
            style.font_weight,
            style.stroke_width,
            style.stroke_color,
            style.outer_stroke_width,
            style.outer_stroke_color,
            style.bg_color,
            style.position,
            style.appearance,
            style.margin_horizontal,
        )

    def _create_subtitle_layer(
        self, items: list[SubtitleItem], style, styles: dict
    ) -> SubtitleLayer:
        """字幕スタイルから SubtitleLayer を作成（ヘルパーメソッド）"""
        return SubtitleLayer(
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
            margin_horizontal=style.margin_horizontal,
        )

    def _build_character_layers(
        self,
        script: Script,
        scene_timings: list[SceneTiming],
    ) -> list[CharacterLayer]:
        """キャラクターレイヤーを構築

        Script.characters で定義されたキャラクターを、
        各シーン・セグメントの状態に応じて CharacterLayer に変換する。

        Args:
            script: 台本
            scene_timings: シーンのタイミング情報

        Returns:
            list[CharacterLayer]: キャラクターレイヤーのリスト
        """
        layers: list[CharacterLayer] = []

        # キャラクター定義がない場合は空リストを返す
        if not script.characters:
            return layers

        # Script.CharacterPosition を Layer.CharacterPositionPreset に変換するマッピング
        from .models import CharacterPosition as ScriptCharacterPosition

        position_map = {
            ScriptCharacterPosition.BOTTOM_LEFT: CharacterPositionPreset.BOTTOM_LEFT,
            ScriptCharacterPosition.BOTTOM_RIGHT: CharacterPositionPreset.BOTTOM_RIGHT,
            ScriptCharacterPosition.BOTTOM_CENTER: CharacterPositionPreset.BOTTOM_CENTER,
            ScriptCharacterPosition.LEFT: CharacterPositionPreset.LEFT,
            ScriptCharacterPosition.RIGHT: CharacterPositionPreset.RIGHT,
            ScriptCharacterPosition.CENTER: CharacterPositionPreset.CENTER,
        }

        # Script.CharacterAnimationType を Layer.CharacterAnimationType に変換するマッピング
        from .models import CharacterAnimationType as ScriptAnimationType

        animation_type_map = {
            ScriptAnimationType.NONE: CharacterAnimationType.NONE,
            ScriptAnimationType.BOUNCE: CharacterAnimationType.BOUNCE,
            ScriptAnimationType.SHAKE: CharacterAnimationType.SHAKE,
            ScriptAnimationType.NOD: CharacterAnimationType.NOD,
            ScriptAnimationType.SWAY: CharacterAnimationType.SWAY,
            ScriptAnimationType.BREATHE: CharacterAnimationType.BREATHE,
            ScriptAnimationType.FLOAT: CharacterAnimationType.FLOAT,
            ScriptAnimationType.PULSE: CharacterAnimationType.PULSE,
        }

        # 次のシーンでキャラクターが継続表示されるかを判定するヘルパー
        def _is_char_in_next_scene(char_id: str, scene_idx: int) -> bool:
            """次のシーンでも同じキャラクターが表示されるか"""
            if scene_idx >= len(script.scenes) - 1:
                return False
            next_scene = script.scenes[scene_idx + 1]
            if not next_scene.characters:
                return False
            for next_char_config in next_scene.characters:
                if (
                    next_char_config.character_id == char_id
                    and next_char_config.visible
                ):
                    return True
            return False

        for scene_idx, (scene, scene_timing) in enumerate(
            zip(script.scenes, scene_timings)
        ):
            # このシーンにキャラクターが指定されていない場合はスキップ
            if not scene.characters:
                continue

            # 次のシーンの開始時刻を取得（シーン間ギャップを埋めるため）
            next_scene_start = (
                scene_timings[scene_idx + 1].start_time
                if scene_idx < len(scene_timings) - 1
                else None
            )

            # シーン内のキャラクター設定を処理（リスト順が Z オーダー）
            for scene_char_config in scene.characters:
                char_id = scene_char_config.character_id

                # キャラクター定義を取得
                if char_id not in script.characters:
                    raise ValueError(
                        f"キャラクター '{char_id}' が Script.characters に定義されていません"
                    )
                char_def = script.characters[char_id]

                # シーン全体で非表示の場合はスキップ
                if not scene_char_config.visible:
                    continue

                # 表情名 → 画像パスのマッピングを作成
                expression_paths = {
                    expr.name: expr.path for expr in char_def.expressions
                }

                # シーン固有の設定で上書き
                position = (
                    position_map[scene_char_config.position]
                    if scene_char_config.position
                    else position_map[char_def.position]
                )
                custom_position = (
                    scene_char_config.custom_position
                    if scene_char_config.custom_position
                    else char_def.custom_position
                )
                scale = (
                    scene_char_config.scale
                    if scene_char_config.scale is not None
                    else char_def.scale
                )

                # 次のシーンでもこのキャラクターが表示されるか
                char_continues_next = _is_char_in_next_scene(char_id, scene_idx)

                # セグメントがない場合（ナレーションなしシーン）
                if not scene_timing.segments:
                    # シーン全体にキャラクターを表示（デフォルト表情）
                    expression = char_def.default_expression
                    if expression not in expression_paths:
                        raise ValueError(
                            f"表情 '{expression}' がキャラクター '{char_id}' に定義されていません"
                        )

                    # デフォルトアニメーション
                    default_anim = char_def.default_animation
                    animation_config = CharacterAnimationConfig(
                        type=animation_type_map[default_anim.type],
                        intensity=default_anim.intensity,
                        speed=default_anim.speed,
                    )

                    # 終了時刻: 次のシーンでも表示される場合は次のシーン開始まで延長
                    char_end_time = (
                        next_scene_start
                        if char_continues_next and next_scene_start is not None
                        else scene_timing.end_time
                    )

                    layers.append(
                        CharacterLayer(
                            character_id=char_id,
                            character_name=char_def.name,
                            expression=expression,
                            path=expression_paths[expression],
                            start_time=scene_timing.start_time,
                            end_time=char_end_time,
                            position=position,
                            custom_position=custom_position,
                            scale=scale,
                            animation=animation_config,
                        )
                    )
                    continue

                # セグメント毎にキャラクター状態を処理
                # シーン全体での表示時間を計算するため、セグメント間のギャップも含める
                # 重複を避けるため、各セグメントの開始時刻を基準に時間区間を分割
                num_segments = len(scene_timing.segments)
                for seg_idx, segment_timing in enumerate(scene_timing.segments):
                    segment = scene.narrations[seg_idx]

                    # このセグメントでのキャラクター状態を取得
                    char_state = None
                    for state in segment.character_states:
                        if state.character_id == char_id:
                            char_state = state
                            break

                    # 状態が指定されていない場合はデフォルト
                    if char_state is None:
                        expression = char_def.default_expression
                        visible = True
                        anim = char_def.default_animation
                    else:
                        expression = (
                            char_state.expression
                            if char_state.expression
                            else char_def.default_expression
                        )
                        visible = char_state.visible
                        anim = (
                            char_state.animation
                            if char_state.animation
                            else char_def.default_animation
                        )

                    # 非表示の場合はスキップ
                    if not visible:
                        continue

                    # 表情の検証
                    if expression not in expression_paths:
                        raise ValueError(
                            f"表情 '{expression}' がキャラクター '{char_id}' に定義されていません"
                        )

                    # アニメーション設定を変換
                    animation_config = CharacterAnimationConfig(
                        type=animation_type_map[anim.type],
                        intensity=anim.intensity,
                        speed=anim.speed,
                    )

                    # 表示時間を計算（padding/gap を無視して連続表示、重複なし）
                    # - 最初のセグメント: シーン開始から次のセグメント開始まで
                    # - 中間のセグメント: 現在のセグメント開始から次のセグメント開始まで
                    # - 最後のセグメント: 現在のセグメント開始からシーン終了（または次シーン開始）まで
                    if seg_idx == 0:
                        char_start_time = scene_timing.start_time
                    else:
                        char_start_time = segment_timing.start_time

                    is_last_segment = seg_idx == num_segments - 1
                    if is_last_segment:
                        # 最後のセグメント: 次のシーンでも表示される場合は次のシーン開始まで
                        if char_continues_next and next_scene_start is not None:
                            char_end_time = next_scene_start
                        else:
                            char_end_time = scene_timing.end_time
                    else:
                        # 最初/中間: 次のセグメント開始時刻まで（重複なし）
                        next_segment = scene_timing.segments[seg_idx + 1]
                        char_end_time = next_segment.start_time

                    layers.append(
                        CharacterLayer(
                            character_id=char_id,
                            character_name=char_def.name,
                            expression=expression,
                            path=expression_paths[expression],
                            start_time=char_start_time,
                            end_time=char_end_time,
                            position=position,
                            custom_position=custom_position,
                            scale=scale,
                            animation=animation_config,
                        )
                    )

        return layers

    def _assemble_project(
        self,
        script: Script,
        video_layers: list[Union[VideoLayer, ImageLayer]],
        audio_layers: list[AudioLayer],
        subtitle_layers: list[SubtitleLayer],
        character_layers: list[CharacterLayer],
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
                character_layers=character_layers,
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
