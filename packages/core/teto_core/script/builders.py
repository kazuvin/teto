"""Script builders - Builder pattern implementations for Script construction"""

from .models import (
    Script,
    Scene,
    NarrationSegment,
    Visual,
    AssetType,
    TimingConfig,
    BGMConfig,
    VoiceConfig,
    SoundEffect,
)
from ..output_config.models import OutputSettings, VideoAspectRatio


class NarrationSegmentBuilder:
    """ナレーションセグメントのビルダー"""

    def __init__(self, text: str):
        """NarrationSegmentBuilderを初期化する

        Args:
            text: 字幕テキスト
        """
        self._text = text
        self._pause_after = 0.0

    def pause_after(self, seconds: float) -> "NarrationSegmentBuilder":
        """セグメント後の間隔を設定する

        Args:
            seconds: 間隔（秒）

        Returns:
            NarrationSegmentBuilder: 自身のインスタンス（チェーン呼び出し用）
        """
        self._pause_after = seconds
        return self

    def build(self) -> NarrationSegment:
        """NarrationSegmentを構築する

        Returns:
            NarrationSegment: 構築されたナレーションセグメント
        """
        return NarrationSegment(
            text=self._text,
            pause_after=self._pause_after,
        )


class SceneBuilder:
    """シーンのビルダー"""

    def __init__(self):
        """SceneBuilderを初期化する"""
        self._narrations: list[NarrationSegment] = []
        self._visual: Visual | None = None
        self._duration: float | None = None
        self._pause_after = 0.0
        self._note: str | None = None
        self._sound_effects: list[SoundEffect] = []
        self._mute_video = False

    def add_narration(self, text: str, pause_after: float = 0.0) -> "SceneBuilder":
        """ナレーションを追加する

        Args:
            text: 字幕テキスト
            pause_after: セグメント後の間隔（秒）

        Returns:
            SceneBuilder: 自身のインスタンス（チェーン呼び出し用）
        """
        self._narrations.append(NarrationSegment(text=text, pause_after=pause_after))
        return self

    def visual_path(
        self, path: str, asset_type: AssetType = AssetType.IMAGE
    ) -> "SceneBuilder":
        """映像をパスで指定する

        Args:
            path: ファイルパス
            asset_type: アセットタイプ（image または video）

        Returns:
            SceneBuilder: 自身のインスタンス（チェーン呼び出し用）
        """
        self._visual = Visual(type=asset_type, path=path)
        return self

    def visual_description(
        self, description: str, asset_type: AssetType = AssetType.IMAGE
    ) -> "SceneBuilder":
        """映像を説明で指定する（将来のAI生成用）

        Args:
            description: 映像の説明
            asset_type: アセットタイプ（image または video）

        Returns:
            SceneBuilder: 自身のインスタンス（チェーン呼び出し用）
        """
        self._visual = Visual(type=asset_type, description=description)
        return self

    def duration(self, seconds: float) -> "SceneBuilder":
        """シーンの長さを設定する（ナレーションなしの場合に必須）

        Args:
            seconds: シーンの長さ（秒）

        Returns:
            SceneBuilder: 自身のインスタンス（チェーン呼び出し用）
        """
        self._duration = seconds
        return self

    def pause_after(self, seconds: float) -> "SceneBuilder":
        """シーン後の間隔を設定する

        Args:
            seconds: 間隔（秒）

        Returns:
            SceneBuilder: 自身のインスタンス（チェーン呼び出し用）
        """
        self._pause_after = seconds
        return self

    def note(self, text: str) -> "SceneBuilder":
        """演出メモを設定する

        Args:
            text: メモテキスト

        Returns:
            SceneBuilder: 自身のインスタンス（チェーン呼び出し用）
        """
        self._note = text
        return self

    def add_sound_effect(
        self, path: str, offset: float = 0.0, volume: float = 1.0
    ) -> "SceneBuilder":
        """効果音を追加する

        Args:
            path: 効果音ファイルパス
            offset: シーン開始からのオフセット（秒）
            volume: 音量 (0.0〜1.0)

        Returns:
            SceneBuilder: 自身のインスタンス（チェーン呼び出し用）
        """
        self._sound_effects.append(SoundEffect(path=path, offset=offset, volume=volume))
        return self

    def mute_video(self, mute: bool = True) -> "SceneBuilder":
        """動画の音声をミュートにするか設定する

        Args:
            mute: True の場合、動画ファイルの音声を無音にする

        Returns:
            SceneBuilder: 自身のインスタンス（チェーン呼び出し用）
        """
        self._mute_video = mute
        return self

    def build(self) -> Scene:
        """Sceneを構築する

        Returns:
            Scene: 構築されたシーン

        Raises:
            ValueError: 必須パラメータが設定されていない場合
        """
        if self._visual is None:
            raise ValueError(
                "Visual is required. Use visual_path() or visual_description()."
            )

        return Scene(
            narrations=self._narrations,
            visual=self._visual,
            duration=self._duration,
            pause_after=self._pause_after,
            note=self._note,
            sound_effects=self._sound_effects,
            mute_video=self._mute_video,
        )


class ScriptBuilder:
    """台本のビルダー"""

    def __init__(self, title: str):
        """ScriptBuilderを初期化する

        Args:
            title: 動画タイトル
        """
        self._title = title
        self._scenes: list[Scene] = []
        self._voice: VoiceConfig = VoiceConfig()
        self._timing: TimingConfig = TimingConfig()
        self._bgm: BGMConfig | None = None
        self._description: str | None = None
        self._output: OutputSettings = OutputSettings()

    def add_scene(self, scene: Scene) -> "ScriptBuilder":
        """シーンを追加する

        Args:
            scene: 追加するシーン

        Returns:
            ScriptBuilder: 自身のインスタンス（チェーン呼び出し用）
        """
        self._scenes.append(scene)
        return self

    def add_scene_builder(self, builder: SceneBuilder) -> "ScriptBuilder":
        """SceneBuilderからシーンを追加する

        Args:
            builder: シーンビルダー

        Returns:
            ScriptBuilder: 自身のインスタンス（チェーン呼び出し用）
        """
        self._scenes.append(builder.build())
        return self

    def voice(
        self,
        provider: str = "google",
        voice_id: str | None = None,
        language_code: str = "ja-JP",
        speed: float = 1.0,
        pitch: float = 0.0,
    ) -> "ScriptBuilder":
        """音声設定を設定する

        Args:
            provider: TTSプロバイダー（google, openai, voicevox）
            voice_id: 声の指定
            language_code: 言語コード
            speed: 話速（0.5〜2.0）
            pitch: ピッチ（-20〜20）

        Returns:
            ScriptBuilder: 自身のインスタンス（チェーン呼び出し用）
        """
        self._voice = VoiceConfig(
            provider=provider,  # type: ignore
            voice_id=voice_id,
            language_code=language_code,
            speed=speed,
            pitch=pitch,
        )
        return self

    def timing(
        self,
        segment_gap: float = 0.3,
        scene_gap: float = 0.5,
        subtitle_padding: float = 0.1,
    ) -> "ScriptBuilder":
        """タイミング設定を設定する

        Args:
            segment_gap: ナレーションセグメント間のデフォルト間隔（秒）
            scene_gap: シーン間のデフォルト間隔（秒）
            subtitle_padding: 字幕の前後パディング（秒）

        Returns:
            ScriptBuilder: 自身のインスタンス（チェーン呼び出し用）
        """
        self._timing = TimingConfig(
            default_segment_gap=segment_gap,
            default_scene_gap=scene_gap,
            subtitle_padding=subtitle_padding,
        )
        return self

    def bgm(
        self,
        path: str,
        volume: float = 0.3,
        fade_in: float = 0.0,
        fade_out: float = 0.0,
    ) -> "ScriptBuilder":
        """BGM設定を設定する

        Args:
            path: BGMファイルパス
            volume: 音量（0.0〜1.0）
            fade_in: フェードイン時間（秒）
            fade_out: フェードアウト時間（秒）

        Returns:
            ScriptBuilder: 自身のインスタンス（チェーン呼び出し用）
        """
        self._bgm = BGMConfig(
            path=path,
            volume=volume,
            fade_in=fade_in,
            fade_out=fade_out,
        )
        return self

    def description(self, text: str) -> "ScriptBuilder":
        """動画の説明を設定する

        Args:
            text: 説明テキスト

        Returns:
            ScriptBuilder: 自身のインスタンス（チェーン呼び出し用）
        """
        self._description = text
        return self

    def output(
        self,
        aspect_ratio: VideoAspectRatio | str | None = None,
        width: int | None = None,
        height: int | None = None,
        fps: int | None = None,
    ) -> "ScriptBuilder":
        """出力設定を設定する

        Args:
            aspect_ratio: アスペクト比プリセット（"16:9", "9:16"など）
            width: 出力幅（aspect_ratioが指定されている場合は無視される）
            height: 出力高さ（aspect_ratioが指定されている場合は無視される）
            fps: フレームレート

        Returns:
            ScriptBuilder: 自身のインスタンス（チェーン呼び出し用）

        Examples:
            >>> builder.output(aspect_ratio="9:16")  # TikTok/Shorts用
            >>> builder.output(width=1440, height=2560, fps=60)  # カスタム
        """
        # aspect_ratioの処理
        if aspect_ratio is not None:
            if isinstance(aspect_ratio, str):
                aspect_ratio = VideoAspectRatio(aspect_ratio)
            self._output.aspect_ratio = aspect_ratio

        # width/heightの処理（aspect_ratioが指定されていない場合のみ）
        if aspect_ratio is None:
            if width is not None:
                self._output.width = width
            if height is not None:
                self._output.height = height

        # fpsの処理
        if fps is not None:
            self._output.fps = fps

        return self

    def build(self) -> Script:
        """Scriptを構築する

        Returns:
            Script: 構築された台本

        Raises:
            ValueError: シーンが1つも追加されていない場合
        """
        if not self._scenes:
            raise ValueError("At least one scene is required.")

        return Script(
            title=self._title,
            scenes=self._scenes,
            voice=self._voice,
            timing=self._timing,
            bgm=self._bgm,
            description=self._description,
            output=self._output,
        )
