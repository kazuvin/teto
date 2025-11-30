"""Google Cloud Text-to-Speech API クライアント"""

from google.cloud import texttospeech
from typing import TYPE_CHECKING, Optional
from pathlib import Path
import os

if TYPE_CHECKING:
    from .models import GoogleTTSVoiceConfig, GoogleTTSAudioConfig

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


class GoogleTTSClient:
    """Google Cloud Text-to-Speech API クライアント"""

    def __init__(self, credentials_path: Optional[Path] = None):
        """
        Args:
            credentials_path: サービスアカウント認証情報のパス
                             (Noneの場合は環境変数から取得)
        """
        # .envファイルを読み込み（複数の場所を探す）
        if load_dotenv is not None and not credentials_path:
            self._load_env_file()

        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)

        self.client = texttospeech.TextToSpeechClient()

    def _load_env_file(self):
        """環境変数ファイルを読み込み"""
        # 探索する.envファイルの場所（優先順位順）
        env_candidates = [
            Path.cwd() / ".env",  # カレントディレクトリ
            Path.cwd() / "packages" / "core" / ".env",  # packages/core
            Path(__file__).parent.parent.parent.parent / ".env",  # プロジェクトルート
            Path(__file__).parent.parent.parent / ".env",  # coreパッケージルート
        ]

        for env_path in env_candidates:
            if env_path.exists():
                load_dotenv(dotenv_path=env_path, override=False)

                # 相対パスを絶対パスに変換
                credentials_env = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                if credentials_env and not Path(credentials_env).is_absolute():
                    # .envファイルの場所を基準に相対パスを解決
                    abs_credentials = (env_path.parent / credentials_env).resolve()
                    if abs_credentials.exists():
                        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(
                            abs_credentials
                        )
                break

    def synthesize(
        self,
        text: str,
        voice_config: "GoogleTTSVoiceConfig",
        audio_config: "GoogleTTSAudioConfig",
        use_ssml: bool = False,
    ) -> bytes:
        """テキストから音声データを生成

        Args:
            text: 変換するテキスト
            voice_config: 音声設定
            audio_config: 音声出力設定
            use_ssml: SSMLとして解釈するか

        Returns:
            音声データ(バイト列)

        Raises:
            GoogleCloudError: API呼び出しに失敗した場合
        """
        # 入力テキストの設定
        if use_ssml:
            synthesis_input = texttospeech.SynthesisInput(ssml=text)
        else:
            synthesis_input = texttospeech.SynthesisInput(text=text)

        # 音声設定
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_config.language_code,
            name=voice_config.voice_name,
            ssml_gender=self._convert_gender(voice_config.ssml_gender),
        )

        # 音声出力設定
        audio_config_proto = texttospeech.AudioConfig(
            audio_encoding=self._convert_encoding(audio_config.audio_encoding),
            speaking_rate=audio_config.speaking_rate,
            pitch=audio_config.pitch,
            volume_gain_db=audio_config.volume_gain_db,
            sample_rate_hertz=audio_config.sample_rate_hertz,
            effects_profile_id=audio_config.effects_profile_id,
        )

        # API呼び出し
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config_proto,
        )

        return response.audio_content

    def list_voices(self, language_code: Optional[str] = None) -> list[dict]:
        """利用可能な音声のリストを取得

        Args:
            language_code: 言語コード(Noneの場合は全言語)

        Returns:
            音声情報のリスト
        """
        response = self.client.list_voices(language_code=language_code)

        voices = []
        for voice in response.voices:
            voices.append(
                {
                    "name": voice.name,
                    "language_codes": voice.language_codes,
                    "ssml_gender": voice.ssml_gender.name,
                    "natural_sample_rate_hertz": voice.natural_sample_rate_hertz,
                }
            )

        return voices

    def estimate_duration(
        self, text: str, audio_config: "GoogleTTSAudioConfig"
    ) -> float:
        """生成される音声の推定長さ

        Args:
            text: テキスト
            audio_config: 音声出力設定

        Returns:
            推定長さ(秒)
        """
        # 日本語の場合は約5文字/秒、英語の場合は約15文字/秒として推定
        is_japanese = any(ord(c) > 0x3000 for c in text)
        chars_per_second = 5.0 if is_japanese else 15.0

        base_duration = len(text) / chars_per_second
        return base_duration / audio_config.speaking_rate

    def _convert_gender(self, gender: str) -> texttospeech.SsmlVoiceGender:
        """SSML性別を変換"""
        gender_map = {
            "NEUTRAL": texttospeech.SsmlVoiceGender.NEUTRAL,
            "MALE": texttospeech.SsmlVoiceGender.MALE,
            "FEMALE": texttospeech.SsmlVoiceGender.FEMALE,
        }
        return gender_map.get(gender, texttospeech.SsmlVoiceGender.NEUTRAL)

    def _convert_encoding(self, encoding: str) -> texttospeech.AudioEncoding:
        """音声エンコーディングを変換"""
        encoding_map = {
            "MP3": texttospeech.AudioEncoding.MP3,
            "LINEAR16": texttospeech.AudioEncoding.LINEAR16,
            "OGG_OPUS": texttospeech.AudioEncoding.OGG_OPUS,
        }
        return encoding_map.get(encoding, texttospeech.AudioEncoding.MP3)
