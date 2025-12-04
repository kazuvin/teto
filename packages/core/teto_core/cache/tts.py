"""TTS Cache Manager - Text-to-Speech audio caching"""

from pathlib import Path
from typing import TYPE_CHECKING

from .base import AssetCacheManager, CacheInfo

if TYPE_CHECKING:
    from ..script.models import VoiceConfig


class TTSCacheManager(AssetCacheManager):
    """TTS 音声キャッシュマネージャー

    テキストと音声設定のハッシュをキーにして音声ファイルをキャッシュします。
    """

    ASSET_TYPE = "tts"
    DEFAULT_CACHE_SUBDIR = "tts"

    def _compute_cache_key(self, text: str, voice_config: "VoiceConfig") -> str:
        """キャッシュキーを計算

        Args:
            text: テキスト
            voice_config: 音声設定

        Returns:
            キャッシュキー（ハッシュ値）
        """
        # 音声設定から関連するフィールドを抽出
        config_dict = {
            "provider": voice_config.provider,
            "voice_id": voice_config.voice_id,
            "language_code": voice_config.language_code,
            "speed": voice_config.speed,
            "pitch": voice_config.pitch,
            # ElevenLabs
            "model_id": voice_config.model_id,
            "output_format": voice_config.output_format,
            # Gemini
            "voice_name": voice_config.voice_name,
            "gemini_model_id": voice_config.gemini_model_id,
            "style_prompt": voice_config.style_prompt,
        }

        # テキストと設定を結合してハッシュ化
        return self.compute_hash({"text": text, "config": config_dict})

    def get(self, text: str, voice_config: "VoiceConfig", ext: str) -> bytes | None:
        """キャッシュから音声データを取得

        Args:
            text: テキスト
            voice_config: 音声設定
            ext: 拡張子

        Returns:
            キャッシュされた音声データ、なければ None
        """
        cache_key = self._compute_cache_key(text, voice_config)
        return self.get_by_key(cache_key, ext)

    def put(
        self, text: str, voice_config: "VoiceConfig", ext: str, audio_data: bytes
    ) -> Path:
        """音声データをキャッシュに保存

        Args:
            text: テキスト
            voice_config: 音声設定
            ext: 拡張子
            audio_data: 音声データ

        Returns:
            キャッシュファイルのパス
        """
        cache_key = self._compute_cache_key(text, voice_config)
        return self.put_by_key(cache_key, ext, audio_data)

    def has(self, text: str, voice_config: "VoiceConfig", ext: str) -> bool:
        """キャッシュが存在するか確認

        Args:
            text: テキスト
            voice_config: 音声設定
            ext: 拡張子

        Returns:
            キャッシュが存在すれば True
        """
        cache_key = self._compute_cache_key(text, voice_config)
        return self.has_by_key(cache_key, ext)


# グローバルキャッシュマネージャー（シングルトン）
_default_tts_cache_manager: TTSCacheManager | None = None


def get_tts_cache_manager() -> TTSCacheManager:
    """デフォルトのTTSキャッシュマネージャーを取得"""
    global _default_tts_cache_manager
    if _default_tts_cache_manager is None:
        _default_tts_cache_manager = TTSCacheManager()
    return _default_tts_cache_manager


def clear_tts_cache() -> int:
    """TTSキャッシュをクリア"""
    return get_tts_cache_manager().clear()


def get_tts_cache_info() -> CacheInfo:
    """TTSキャッシュの情報を取得"""
    return get_tts_cache_manager().get_info()
