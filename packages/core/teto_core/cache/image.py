"""Image Cache Manager - AI-generated image caching"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .base import AssetCacheManager, CacheInfo


@dataclass
class ImageGenerationConfig:
    """画像生成設定

    将来のAI画像生成（DALL-E, Stable Diffusion等）用の設定。
    """

    provider: str  # "dalle", "stable_diffusion", "midjourney", etc.
    model: str  # モデルID
    prompt: str  # プロンプト
    negative_prompt: str | None = None  # ネガティブプロンプト
    width: int = 1024
    height: int = 1024
    seed: int | None = None  # シード値（再現性用）
    style: str | None = None  # スタイル指定
    quality: str | None = None  # 品質設定

    def to_dict(self) -> dict[str, Any]:
        """辞書に変換"""
        return {
            "provider": self.provider,
            "model": self.model,
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "width": self.width,
            "height": self.height,
            "seed": self.seed,
            "style": self.style,
            "quality": self.quality,
        }


class ImageCacheManager(AssetCacheManager):
    """画像キャッシュマネージャー

    プロンプトと画像生成設定のハッシュをキーにして画像ファイルをキャッシュします。
    """

    ASSET_TYPE = "image"
    DEFAULT_CACHE_SUBDIR = "images"

    def _compute_cache_key(self, config: ImageGenerationConfig) -> str:
        """キャッシュキーを計算

        Args:
            config: 画像生成設定

        Returns:
            キャッシュキー（ハッシュ値）
        """
        return self.compute_hash(config.to_dict())

    def get(self, config: ImageGenerationConfig, ext: str = ".png") -> bytes | None:
        """キャッシュから画像データを取得

        Args:
            config: 画像生成設定
            ext: 拡張子

        Returns:
            キャッシュされた画像データ、なければ None
        """
        cache_key = self._compute_cache_key(config)
        return self.get_by_key(cache_key, ext)

    def put(
        self, config: ImageGenerationConfig, image_data: bytes, ext: str = ".png"
    ) -> Path:
        """画像データをキャッシュに保存

        Args:
            config: 画像生成設定
            image_data: 画像データ
            ext: 拡張子

        Returns:
            キャッシュファイルのパス
        """
        cache_key = self._compute_cache_key(config)
        return self.put_by_key(cache_key, ext, image_data)

    def has(self, config: ImageGenerationConfig, ext: str = ".png") -> bool:
        """キャッシュが存在するか確認

        Args:
            config: 画像生成設定
            ext: 拡張子

        Returns:
            キャッシュが存在すれば True
        """
        cache_key = self._compute_cache_key(config)
        return self.has_by_key(cache_key, ext)


# グローバルキャッシュマネージャー（シングルトン）
_default_image_cache_manager: ImageCacheManager | None = None


def get_image_cache_manager() -> ImageCacheManager:
    """デフォルトの画像キャッシュマネージャーを取得"""
    global _default_image_cache_manager
    if _default_image_cache_manager is None:
        _default_image_cache_manager = ImageCacheManager()
    return _default_image_cache_manager


def clear_image_cache() -> int:
    """画像キャッシュをクリア"""
    return get_image_cache_manager().clear()


def get_image_cache_info() -> CacheInfo:
    """画像キャッシュの情報を取得"""
    return get_image_cache_manager().get_info()
