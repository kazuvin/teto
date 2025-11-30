"""TTS Builder パターン実装"""

from pathlib import Path
from typing import Optional, Literal
from . import TTSRequest, GoogleTTSVoiceConfig, GoogleTTSAudioConfig


class TTSBuilder:
    """TTS リクエストのビルダー(Builder パターン)"""

    def __init__(self):
        self._text: Optional[str] = None
        self._voice_config = GoogleTTSVoiceConfig()
        self._audio_config = GoogleTTSAudioConfig()
        self._output_path: Optional[Path] = None
        self._use_ssml = False

    def text(self, text: str) -> "TTSBuilder":
        """変換するテキストを設定

        Args:
            text: テキスト(1～5000文字)
        """
        self._text = text
        return self

    def voice(self, voice_name: str) -> "TTSBuilder":
        """音声を設定

        Args:
            voice_name: 音声名(例: "ja-JP-Wavenet-A")
        """
        self._voice_config.voice_name = voice_name

        # 音声名から言語コードを推測
        if "-" in voice_name:
            lang_code = "-".join(voice_name.split("-")[:2])
            self._voice_config.language_code = lang_code

        return self

    def language(self, language_code: str) -> "TTSBuilder":
        """言語を設定

        Args:
            language_code: 言語コード(例: "ja-JP", "en-US")
        """
        self._voice_config.language_code = language_code
        return self

    def speed(self, rate: float) -> "TTSBuilder":
        """話す速度を設定

        Args:
            rate: 速度(0.25～4.0倍速)
        """
        self._audio_config.speaking_rate = rate
        return self

    def pitch(self, pitch: float) -> "TTSBuilder":
        """ピッチを設定

        Args:
            pitch: ピッチ調整(-20.0～20.0セミトーン)
        """
        self._audio_config.pitch = pitch
        return self

    def volume(self, gain_db: float) -> "TTSBuilder":
        """音量を設定

        Args:
            gain_db: 音量調整(dB)
        """
        self._audio_config.volume_gain_db = gain_db
        return self

    def sample_rate(self, rate: int) -> "TTSBuilder":
        """サンプリングレートを設定

        Args:
            rate: サンプリングレート(Hz)
        """
        self._audio_config.sample_rate_hertz = rate
        return self

    def output_format(self, format: Literal["mp3", "wav", "ogg"]) -> "TTSBuilder":
        """出力フォーマットを設定

        Args:
            format: 音声フォーマット
        """
        format_map = {
            "mp3": "MP3",
            "wav": "LINEAR16",
            "ogg": "OGG_OPUS",
        }
        self._audio_config.audio_encoding = format_map.get(format, "MP3")
        return self

    def output_path(self, path: str | Path) -> "TTSBuilder":
        """出力先パスを設定

        Args:
            path: 出力先ファイルパス
        """
        self._output_path = Path(path) if isinstance(path, str) else path
        return self

    def effects_profile(self, profiles: list[str]) -> "TTSBuilder":
        """音声効果プロファイルを設定

        Args:
            profiles: プロファイルリスト(例: ["headphone-class-device"])
        """
        self._audio_config.effects_profile_id = profiles
        return self

    def ssml(self, use_ssml: bool = True) -> "TTSBuilder":
        """SSMLモードを設定

        Args:
            use_ssml: SSMLとして解釈するか
        """
        self._use_ssml = use_ssml
        return self

    def build(self) -> TTSRequest:
        """TTSRequestを構築

        Returns:
            構築されたTTSRequest

        Raises:
            ValueError: テキストが設定されていない場合
        """
        if not self._text:
            raise ValueError("Text is required")

        return TTSRequest(
            text=self._text,
            voice_config=self._voice_config,
            audio_config=self._audio_config,
            output_path=self._output_path,
            use_ssml=self._use_ssml,
        )
