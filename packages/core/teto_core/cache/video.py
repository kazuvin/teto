"""Video Cache Manager - AI-generated video caching"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .base import AssetCacheManager, CacheInfo


@dataclass
class VideoGenerationConfig:
    """動画生成設定

    将来のAI動画生成（Runway, Pika, Sora等）用の設定。
    """

    provider: str  # "runway", "pika", "sora", etc.
    model: str  # モデルID
    prompt: str  # プロンプト
    negative_prompt: str | None = None  # ネガティブプロンプト
    width: int = 1920
    height: int = 1080
    fps: int = 24
    duration: float = 4.0  # 秒
    seed: int | None = None  # シード値（再現性用）
    style: str | None = None  # スタイル指定
    motion_bucket_id: int | None = None  # モーション強度（一部プロバイダー用）
    image_ref: str | None = None  # 参照画像パス（image-to-video用）

    def to_dict(self) -> dict[str, Any]:
        """辞書に変換"""
        return {
            "provider": self.provider,
            "model": self.model,
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "duration": self.duration,
            "seed": self.seed,
            "style": self.style,
            "motion_bucket_id": self.motion_bucket_id,
            "image_ref": self.image_ref,
        }


class VideoCacheManager(AssetCacheManager):
    """動画キャッシュマネージャー

    プロンプトと動画生成設定のハッシュをキーにして動画ファイルをキャッシュします。
    """

    ASSET_TYPE = "video"
    DEFAULT_CACHE_SUBDIR = "videos"

    def _compute_cache_key(self, config: VideoGenerationConfig) -> str:
        """キャッシュキーを計算

        Args:
            config: 動画生成設定

        Returns:
            キャッシュキー（ハッシュ値）
        """
        return self.compute_hash(config.to_dict())

    def get(self, config: VideoGenerationConfig, ext: str = ".mp4") -> bytes | None:
        """キャッシュから動画データを取得

        Args:
            config: 動画生成設定
            ext: 拡張子

        Returns:
            キャッシュされた動画データ、なければ None
        """
        cache_key = self._compute_cache_key(config)
        return self.get_by_key(cache_key, ext)

    def put(
        self, config: VideoGenerationConfig, video_data: bytes, ext: str = ".mp4"
    ) -> Path:
        """動画データをキャッシュに保存

        Args:
            config: 動画生成設定
            video_data: 動画データ
            ext: 拡張子

        Returns:
            キャッシュファイルのパス
        """
        cache_key = self._compute_cache_key(config)
        return self.put_by_key(cache_key, ext, video_data)

    def has(self, config: VideoGenerationConfig, ext: str = ".mp4") -> bool:
        """キャッシュが存在するか確認

        Args:
            config: 動画生成設定
            ext: 拡張子

        Returns:
            キャッシュが存在すれば True
        """
        cache_key = self._compute_cache_key(config)
        return self.has_by_key(cache_key, ext)


# グローバルキャッシュマネージャー（シングルトン）
_default_video_cache_manager: VideoCacheManager | None = None


def get_video_cache_manager() -> VideoCacheManager:
    """デフォルトの動画キャッシュマネージャーを取得"""
    global _default_video_cache_manager
    if _default_video_cache_manager is None:
        _default_video_cache_manager = VideoCacheManager()
    return _default_video_cache_manager


def clear_video_cache() -> int:
    """動画キャッシュをクリア"""
    return get_video_cache_manager().clear()


def get_video_cache_info() -> CacheInfo:
    """動画キャッシュの情報を取得"""
    return get_video_cache_manager().get_info()
