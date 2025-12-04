"""Unified Cache Manager - Manages all asset caches"""

from dataclasses import dataclass

from .base import CacheInfo
from .tts import TTSCacheManager, get_tts_cache_manager
from .image import ImageCacheManager, get_image_cache_manager
from .video import VideoCacheManager, get_video_cache_manager


@dataclass
class AllCacheInfo:
    """全キャッシュの統合情報"""

    tts: CacheInfo
    image: CacheInfo
    video: CacheInfo

    @property
    def total_files(self) -> int:
        """総ファイル数"""
        return self.tts.total_files + self.image.total_files + self.video.total_files

    @property
    def total_size_bytes(self) -> int:
        """総サイズ（バイト）"""
        return (
            self.tts.total_size_bytes
            + self.image.total_size_bytes
            + self.video.total_size_bytes
        )

    @property
    def total_size_mb(self) -> float:
        """総サイズ（MB）"""
        return self.total_size_bytes / (1024 * 1024)


class CacheManager:
    """統合キャッシュマネージャー

    TTS、画像、動画のキャッシュを一括管理します。
    """

    def __init__(
        self,
        tts_cache: TTSCacheManager | None = None,
        image_cache: ImageCacheManager | None = None,
        video_cache: VideoCacheManager | None = None,
    ):
        """
        Args:
            tts_cache: TTSキャッシュマネージャー
            image_cache: 画像キャッシュマネージャー
            video_cache: 動画キャッシュマネージャー
        """
        self._tts = tts_cache or get_tts_cache_manager()
        self._image = image_cache or get_image_cache_manager()
        self._video = video_cache or get_video_cache_manager()

    @property
    def tts(self) -> TTSCacheManager:
        """TTSキャッシュマネージャー"""
        return self._tts

    @property
    def image(self) -> ImageCacheManager:
        """画像キャッシュマネージャー"""
        return self._image

    @property
    def video(self) -> VideoCacheManager:
        """動画キャッシュマネージャー"""
        return self._video

    def clear_all(self) -> dict[str, int]:
        """全キャッシュをクリア

        Returns:
            各キャッシュタイプの削除ファイル数
        """
        return {
            "tts": self._tts.clear(),
            "image": self._image.clear(),
            "video": self._video.clear(),
        }

    def clear_tts(self) -> int:
        """TTSキャッシュをクリア"""
        return self._tts.clear()

    def clear_image(self) -> int:
        """画像キャッシュをクリア"""
        return self._image.clear()

    def clear_video(self) -> int:
        """動画キャッシュをクリア"""
        return self._video.clear()

    def get_info(self) -> AllCacheInfo:
        """全キャッシュの情報を取得"""
        return AllCacheInfo(
            tts=self._tts.get_info(),
            image=self._image.get_info(),
            video=self._video.get_info(),
        )


# グローバルキャッシュマネージャー（シングルトン）
_default_cache_manager: CacheManager | None = None


def get_cache_manager() -> CacheManager:
    """デフォルトの統合キャッシュマネージャーを取得"""
    global _default_cache_manager
    if _default_cache_manager is None:
        _default_cache_manager = CacheManager()
    return _default_cache_manager


def clear_all_cache() -> dict[str, int]:
    """全キャッシュをクリア"""
    return get_cache_manager().clear_all()


def get_all_cache_info() -> AllCacheInfo:
    """全キャッシュの情報を取得"""
    return get_cache_manager().get_info()
