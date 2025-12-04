"""Asset Resolver interface and implementations"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from ..models import Visual, StabilityImageConfig, ImageGenerationConfig

if TYPE_CHECKING:
    from ...image_generation.generator import ImageGenerator


class AssetResolver(ABC):
    """アセット解決インターフェース（Strategy）

    利用可能な実装:
    - LocalAssetResolver: パス直接指定
    - AIImageResolver: description から AI 画像生成
    - CompositeAssetResolver: 複数の Resolver を組み合わせ
    """

    @abstractmethod
    def resolve(self, visual: Visual) -> str:
        """Visual指定からファイルパスを解決

        Args:
            visual: 映像指定

        Returns:
            str: 解決されたファイルパス
        """
        ...


class LocalAssetResolver(AssetResolver):
    """ローカルアセット解決（パス直接使用）"""

    def resolve(self, visual: Visual) -> str:
        """Visual指定からファイルパスを解決

        Args:
            visual: 映像指定

        Returns:
            str: 解決されたファイルパス

        Raises:
            ValueError: pathが指定されていない場合
        """
        if visual.path:
            return visual.path
        raise ValueError(
            f"LocalAssetResolver requires path. "
            f"description='{visual.description}' からの解決は未対応です。"
        )


class AIImageResolver(AssetResolver):
    """AI画像生成によるアセット解決

    Visual.generate が指定されている場合、
    description をプロンプトとして画像を生成します。
    """

    def __init__(
        self,
        default_config: ImageGenerationConfig | None = None,
        api_key: str | None = None,
        cache_dir: Path | str | None = None,
    ):
        """
        Args:
            default_config: デフォルトの画像生成設定
            api_key: Stability AI API キー
            cache_dir: キャッシュディレクトリ
        """
        self._default_config = default_config or StabilityImageConfig()
        self._api_key = api_key
        self._cache_dir = cache_dir
        self._generator: "ImageGenerator | None" = None

    @property
    def generator(self) -> "ImageGenerator":
        """遅延初期化で画像生成器を取得"""
        if self._generator is None:
            from ...image_generation.generator import ImageGenerator

            self._generator = ImageGenerator(
                api_key=self._api_key,
                cache_dir=self._cache_dir,
            )
        return self._generator

    def resolve(self, visual: Visual) -> str:
        """Visual指定からファイルパスを解決

        Args:
            visual: 映像指定

        Returns:
            str: 解決された（生成された）ファイルパス

        Raises:
            ValueError: description が指定されていない場合
        """
        if visual.generate is None:
            raise ValueError(
                "AIImageResolver requires Visual.generate to be set. "
                "Use LocalAssetResolver for path-based resolution."
            )

        if visual.description is None:
            raise ValueError("AIImageResolver requires Visual.description as prompt.")

        # 生成設定をマージ（Visual の設定がデフォルトを上書き）
        config = visual.generate

        # 画像を生成
        image_path = self.generator.generate(
            prompt=visual.description,
            config=config,
        )

        return str(image_path)

    def close(self) -> None:
        """リソースを解放"""
        if self._generator is not None:
            self._generator.close()
            self._generator = None


class CompositeAssetResolver(AssetResolver):
    """複合アセット解決

    Visual の設定に応じて適切な Resolver を選択します。
    - path が指定されている場合: LocalAssetResolver
    - generate が指定されている場合: AIImageResolver
    """

    def __init__(
        self,
        default_config: ImageGenerationConfig | None = None,
        api_key: str | None = None,
        cache_dir: Path | str | None = None,
    ):
        """
        Args:
            default_config: デフォルトの画像生成設定
            api_key: Stability AI API キー
            cache_dir: キャッシュディレクトリ
        """
        self._local_resolver = LocalAssetResolver()
        self._ai_resolver = AIImageResolver(
            default_config=default_config,
            api_key=api_key,
            cache_dir=cache_dir,
        )

    def resolve(self, visual: Visual) -> str:
        """Visual指定からファイルパスを解決

        Args:
            visual: 映像指定

        Returns:
            str: 解決されたファイルパス
        """
        # path が指定されている場合はローカルファイルを使用
        if visual.path:
            return self._local_resolver.resolve(visual)

        # generate が指定されている場合は AI 生成
        if visual.generate is not None:
            return self._ai_resolver.resolve(visual)

        # どちらも指定されていない場合はエラー
        raise ValueError(
            "Visual must have either 'path' or 'generate' specified. "
            f"description='{visual.description}'"
        )

    def close(self) -> None:
        """リソースを解放"""
        self._ai_resolver.close()
