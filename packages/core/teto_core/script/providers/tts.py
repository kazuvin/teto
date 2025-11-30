"""TTS Provider interface and implementations"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from ..models import VoiceConfig

if TYPE_CHECKING:
    pass


@dataclass
class TTSResult:
    """TTS生成結果"""

    audio_content: bytes = field(repr=False)
    duration: float
    text: str
    path: str | None = None

    def save(self, output_path: str | Path) -> None:
        """音声ファイルを保存する"""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            f.write(self.audio_content)
        self.path = str(path)


class TTSProvider(ABC):
    """TTS プロバイダーインターフェース（Strategy）"""

    @abstractmethod
    def generate(self, text: str, config: VoiceConfig) -> TTSResult:
        """テキストから音声を生成する

        Args:
            text: 変換するテキスト
            config: 音声設定

        Returns:
            TTSResult: 生成された音声データと情報
        """
        ...

    @abstractmethod
    def estimate_duration(self, text: str, config: VoiceConfig) -> float:
        """音声の長さを推定する（秒）

        Args:
            text: テキスト
            config: 音声設定

        Returns:
            float: 推定される音声の長さ（秒）
        """
        ...


class GoogleTTSProvider(TTSProvider):
    """Google Cloud TTS プロバイダー"""

    def __init__(self, credentials_path: Path | None = None):
        """GoogleTTSProviderを初期化する

        Args:
            credentials_path: サービスアカウント認証情報のパス（Noneの場合は環境変数から取得）
        """
        from ...tts.google_tts import GoogleTTSClient
        from ...tts.models import GoogleTTSVoiceConfig, GoogleTTSAudioConfig

        self._client = GoogleTTSClient(credentials_path=credentials_path)
        self._voice_config_cls = GoogleTTSVoiceConfig
        self._audio_config_cls = GoogleTTSAudioConfig

    def generate(self, text: str, config: VoiceConfig) -> TTSResult:
        """テキストから音声を生成する

        Args:
            text: 変換するテキスト
            config: 音声設定

        Returns:
            TTSResult: 生成された音声データと情報
        """
        voice_config = self._voice_config_cls(
            language_code=config.language_code,
            voice_name=config.voice_id or "ja-JP-Wavenet-A",
        )
        audio_config = self._audio_config_cls(
            speaking_rate=config.speed,
            pitch=config.pitch,
        )

        # 音声データを生成
        audio_content = self._client.synthesize(
            text=text,
            voice_config=voice_config,
            audio_config=audio_config,
        )

        # 音声の長さを推定
        duration = self._client.estimate_duration(text, audio_config)

        return TTSResult(
            audio_content=audio_content,
            duration=duration,
            text=text,
        )

    def estimate_duration(self, text: str, config: VoiceConfig) -> float:
        """音声の長さを推定する（秒）

        Args:
            text: テキスト
            config: 音声設定

        Returns:
            float: 推定される音声の長さ（秒）
        """
        audio_config = self._audio_config_cls(speaking_rate=config.speed)
        return self._client.estimate_duration(text, audio_config)


class MockTTSProvider(TTSProvider):
    """テスト用モックTTSプロバイダー

    実際のTTS APIを呼び出さずに、ダミーの音声データを返す。
    """

    def __init__(self, chars_per_second: float = 5.0):
        """MockTTSProviderを初期化する

        Args:
            chars_per_second: 1秒あたりの文字数（音声長さ推定用）
        """
        self._chars_per_second = chars_per_second

    def generate(self, text: str, config: VoiceConfig) -> TTSResult:
        """ダミーの音声データを生成する

        Args:
            text: 変換するテキスト
            config: 音声設定

        Returns:
            TTSResult: ダミーの音声データと情報
        """
        duration = self.estimate_duration(text, config)

        # 最小のMP3ヘッダー（ダミーデータ）
        dummy_audio = b"\xff\xfb\x90\x00" + b"\x00" * 100

        return TTSResult(
            audio_content=dummy_audio,
            duration=duration,
            text=text,
        )

    def estimate_duration(self, text: str, config: VoiceConfig) -> float:
        """音声の長さを推定する（秒）

        Args:
            text: テキスト
            config: 音声設定

        Returns:
            float: 推定される音声の長さ（秒）
        """
        base_duration = len(text) / self._chars_per_second
        return base_duration / config.speed
