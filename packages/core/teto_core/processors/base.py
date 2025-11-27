"""プロセッサーの基底クラス"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic

T = TypeVar("T")


class ProcessorBase(ABC, Generic[T]):
    """プロセッサーの基底クラス

    各プロセッサーはこのクラスを継承して、process メソッドを実装する。
    これにより、プラグインシステムでカスタムプロセッサーを追加可能になる。
    """

    @abstractmethod
    def process(self, data: T, **kwargs) -> Any:
        """データを処理する

        Args:
            data: 処理対象のデータ
            **kwargs: 追加のパラメータ

        Returns:
            処理結果
        """
        pass

    def validate(self, data: T) -> bool:
        """データのバリデーション（オプション）

        Args:
            data: 検証対象のデータ

        Returns:
            バリデーション結果
        """
        return True

    def preprocess(self, data: T) -> T:
        """前処理（オプション）

        Args:
            data: 前処理対象のデータ

        Returns:
            前処理されたデータ
        """
        return data

    def postprocess(self, result: Any) -> Any:
        """後処理（オプション）

        Args:
            result: 後処理対象の結果

        Returns:
            後処理された結果
        """
        return result
