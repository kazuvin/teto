"""Google Gemini Text-to-Speech API クライアント"""

from typing import TYPE_CHECKING, Optional
from pathlib import Path
from io import BytesIO
import os
import time
import wave

if TYPE_CHECKING:
    from .models import GeminiTTSVoiceConfig

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


class GeminiTTSClient:
    """Google Gemini Text-to-Speech API クライアント"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Google API キー
                    (Noneの場合は環境変数 GOOGLE_API_KEY から取得)
        """
        if genai is None:
            raise ImportError(
                "google-genai package is not installed. "
                "Please install it with: pip install google-genai"
            )

        # .envファイルを読み込み
        if load_dotenv is not None and not api_key:
            self._load_env_file()

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google API key is required. "
                "Set GOOGLE_API_KEY environment variable or pass api_key parameter."
            )

        self.client = genai.Client(api_key=self.api_key)

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
        voice_config: "GeminiTTSVoiceConfig",
    ) -> bytes:
        """テキストから音声データを生成

        Args:
            text: 変換するテキスト
            voice_config: 音声設定

        Returns:
            音声データ(バイト列) - PCM形式

        Raises:
            Exception: API呼び出しに失敗した場合
        """
        # スタイルプロンプトがある場合はテキストの前に付ける
        if voice_config.style_prompt:
            contents = f"{voice_config.style_prompt} {text}"
        else:
            contents = text

        # リトライロジック（レート制限対応）
        max_retries = 5
        retry_delay = 3.0  # 初期待機時間（秒）

        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=voice_config.model_id,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice_config.voice_name,
                                )
                            )
                        ),
                    ),
                )
                break  # 成功したらループを抜ける
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        print(
                            f"  レート制限に達しました。{wait_time:.1f}秒待機してリトライします..."
                        )
                        time.sleep(wait_time)
                    else:
                        raise
                else:
                    raise

        # PCMデータを取得
        pcm_data = response.candidates[0].content.parts[0].inline_data.data

        # PCM を WAV 形式に変換
        wav_buffer = BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(1)  # モノラル
            wf.setsampwidth(2)  # 16bit
            wf.setframerate(24000)  # 24kHz
            wf.writeframes(pcm_data)

        return wav_buffer.getvalue()

    def estimate_duration(
        self, text: str, voice_config: "GeminiTTSVoiceConfig"
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
