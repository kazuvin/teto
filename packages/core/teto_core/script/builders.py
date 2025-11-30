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
)


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
        )
