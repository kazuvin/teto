"""Asset Resolver interface and implementations"""

from abc import ABC, abstractmethod

from ..models import Visual


class AssetResolver(ABC):
    """アセット解決インターフェース（Strategy）

    NOTE: 将来的にはAI画像/動画生成プロバイダーとの連携を想定。
    現時点では LocalAssetResolver（パス直接指定）のみ実装。

    将来対応予定:
    - AIImageGeneratorResolver: description から画像を生成
    - AIVideoGeneratorResolver: description から動画を生成
    - AssetLibraryResolver: アセットライブラリから検索・選択
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
