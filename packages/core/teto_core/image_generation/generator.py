"""画像生成器 - キャッシュ付き画像生成"""

from pathlib import Path
from typing import TYPE_CHECKING

from ..cache.base import AssetCacheManager

if TYPE_CHECKING:
    from ..script.models import StabilityImageConfig


class ImageGenerationCacheManager(AssetCacheManager):
    """AI生成画像用キャッシュマネージャー

    プロンプトと生成設定のハッシュをキーにして画像をキャッシュします。
    """

    ASSET_TYPE = "generated_image"
    DEFAULT_CACHE_SUBDIR = "generated_images"

    def _compute_cache_key(self, prompt: str, config: "StabilityImageConfig") -> str:
        """キャッシュキーを計算

        Args:
            prompt: プロンプト
            config: 画像生成設定

        Returns:
            キャッシュキー（ハッシュ値）
        """
        cache_data = {
            "prompt": prompt,
            "provider": config.provider,
            "style_preset": config.style_preset.value,
            "aspect_ratio": config.aspect_ratio.value,
            "negative_prompt": config.negative_prompt,
            "seed": config.seed,
        }
        return self.compute_hash(cache_data)

    def get(
        self, prompt: str, config: "StabilityImageConfig", ext: str = ".png"
    ) -> bytes | None:
        """キャッシュから画像データを取得"""
        cache_key = self._compute_cache_key(prompt, config)
        return self.get_by_key(cache_key, ext)

    def put(
        self,
        prompt: str,
        config: "StabilityImageConfig",
        image_data: bytes,
        ext: str = ".png",
    ) -> Path:
        """画像データをキャッシュに保存"""
        cache_key = self._compute_cache_key(prompt, config)
        return self.put_by_key(cache_key, ext, image_data)

    def has(
        self, prompt: str, config: "StabilityImageConfig", ext: str = ".png"
    ) -> bool:
        """キャッシュが存在するか確認"""
        cache_key = self._compute_cache_key(prompt, config)
        return self.has_by_key(cache_key, ext)

    def get_cache_path(
        self, prompt: str, config: "StabilityImageConfig", ext: str = ".png"
    ) -> Path:
        """キャッシュファイルのパスを取得（存在しなくても返す）"""
        cache_key = self._compute_cache_key(prompt, config)
        return self._get_cache_path(cache_key, ext)


class ImageGenerator:
    """キャッシュ付き画像生成器

    同じプロンプト・設定での重複生成を防ぎます。
    """

    def __init__(
        self,
        api_key: str | None = None,
        cache_dir: Path | str | None = None,
    ):
        """
        Args:
            api_key: Stability AI API キー
            cache_dir: キャッシュディレクトリ
        """
        self._api_key = api_key
        self._client = None
        self._cache = ImageGenerationCacheManager(cache_dir)

    @property
    def client(self):
        """遅延初期化でクライアントを取得"""
        if self._client is None:
            from .stability import StabilityAIClient

            self._client = StabilityAIClient(api_key=self._api_key)
        return self._client

    @property
    def cache(self) -> ImageGenerationCacheManager:
        """キャッシュマネージャーを取得"""
        return self._cache

    def generate(
        self,
        prompt: str,
        config: "StabilityImageConfig",
        use_cache: bool = True,
    ) -> Path:
        """画像を生成してキャッシュに保存

        Args:
            prompt: 画像生成プロンプト
            config: 画像生成設定
            use_cache: キャッシュを使用するか

        Returns:
            生成された画像ファイルのパス
        """
        ext = ".png"

        # キャッシュを確認
        if use_cache and self._cache.has(prompt, config, ext):
            cache_path = self._cache.get_cache_path(prompt, config, ext)
            print(f"  キャッシュから取得: {cache_path}")
            return cache_path

        # 画像を生成
        print(f"  画像を生成中: {prompt[:50]}...")
        image_data = self.client.generate(prompt, config)

        # キャッシュに保存
        cache_path = self._cache.put(prompt, config, image_data, ext)
        print(f"  キャッシュに保存: {cache_path}")

        return cache_path

    def close(self) -> None:
        """リソースを解放"""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> "ImageGenerator":
        return self

    def __exit__(self, *args) -> None:
        self.close()


# グローバルインスタンス
_default_generator: ImageGenerator | None = None


def get_image_generator() -> ImageGenerator:
    """デフォルトの画像生成器を取得"""
    global _default_generator
    if _default_generator is None:
        _default_generator = ImageGenerator()
    return _default_generator


def generate_image(
    prompt: str,
    config: "StabilityImageConfig",
    use_cache: bool = True,
) -> Path:
    """画像を生成（便利関数）

    Args:
        prompt: 画像生成プロンプト
        config: 画像生成設定
        use_cache: キャッシュを使用するか

    Returns:
        生成された画像ファイルのパス
    """
    return get_image_generator().generate(prompt, config, use_cache)
