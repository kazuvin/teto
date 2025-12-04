"""ElevenLabs Text-to-Speech API クライアント"""

from typing import TYPE_CHECKING, Optional
from pathlib import Path
import os

if TYPE_CHECKING:
    from .models import ElevenLabsVoiceConfig

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from elevenlabs.client import ElevenLabs
except ImportError:
    ElevenLabs = None


class ElevenLabsTTSClient:
    """ElevenLabs Text-to-Speech API クライアント"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: ElevenLabs API キー
                    (Noneの場合は環境変数 ELEVENLABS_API_KEY から取得)
        """
        if ElevenLabs is None:
            raise ImportError(
                "elevenlabs package is not installed. "
                "Please install it with: pip install elevenlabs"
            )

        # .envファイルを読み込み
        if load_dotenv is not None and not api_key:
            self._load_env_file()

        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ElevenLabs API key is required. "
                "Set ELEVENLABS_API_KEY environment variable or pass api_key parameter."
            )

        self.client = ElevenLabs(api_key=self.api_key)

    def _load_env_file(self):
        """環境変数ファイルを読み込み"""
        env_candidates = [
            Path.cwd() / ".env",
            Path.cwd() / "packages" / "core" / ".env",
            Path(__file__).parent.parent.parent.parent / ".env",
            Path(__file__).parent.parent.parent / ".env",
        ]

        for env_path in env_candidates:
            if env_path.exists():
                load_dotenv(dotenv_path=env_path, override=False)
                break

    def synthesize(
        self,
        text: str,
        voice_config: "ElevenLabsVoiceConfig",
    ) -> bytes:
        """テキストから音声データを生成

        Args:
            text: 変換するテキスト
            voice_config: 音声設定

        Returns:
            音声データ(バイト列)

        Raises:
            Exception: API呼び出しに失敗した場合
        """
        audio_generator = self.client.text_to_speech.convert(
            text=text,
            voice_id=voice_config.voice_id,
            model_id=voice_config.model_id,
            output_format=voice_config.output_format,
        )

        # ジェネレータからバイト列を取得
        audio_bytes = b"".join(audio_generator)
        return audio_bytes

    def list_voices(self) -> list[dict]:
        """利用可能な音声のリストを取得

        Returns:
            音声情報のリスト
        """
        response = self.client.voices.get_all()

        voices = []
        for voice in response.voices:
            voices.append(
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": voice.category,
                    "labels": voice.labels,
                }
            )

        return voices

    def estimate_duration(
        self, text: str, voice_config: "ElevenLabsVoiceConfig"
    ) -> float:
        """生成される音声の推定長さ

        Args:
            text: テキスト
            voice_config: 音声設定

        Returns:
            推定長さ(秒)
        """
        # 日本語の場合は約5文字/秒、英語の場合は約15文字/秒として推定
        is_japanese = any(ord(c) > 0x3000 for c in text)
        chars_per_second = 5.0 if is_japanese else 15.0

        base_duration = len(text) / chars_per_second
        return base_duration
