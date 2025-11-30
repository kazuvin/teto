"""プロセッサーの基底クラス"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic

T = TypeVar("T")
R = TypeVar("R")


class ProcessorBase(ABC, Generic[T, R]):
    """プロセッサーの基底クラス

    Template Method パターンを使用して、共通の処理フローを定義。
    各サブクラスは具体的な処理のみを実装する。
    """

    def execute(self, data: T, **kwargs) -> R:
        """処理を実行（Template Method）

        Args:
            data: 処理対象のデータ
            **kwargs: 追加のパラメータ

        Returns:
            処理結果
        """
        # 1. バリデーション
        if not self.validate(data, **kwargs):
            raise ValueError(f"Validation failed for {type(data).__name__}")

        # 2. 前処理
        data = self.preprocess(data, **kwargs)

        # 3. メイン処理（サブクラスで実装）
        result = self.process(data, **kwargs)

        # 4. 後処理
        result = self.postprocess(result, **kwargs)

        return result

    @abstractmethod
    def process(self, data: T, **kwargs) -> R:
        """メイン処理（サブクラスで実装）

        Args:
            data: 処理対象のデータ
            **kwargs: 追加のパラメータ

        Returns:
            処理結果
        """
        pass

    def validate(self, data: T, **kwargs) -> bool:
        """データのバリデーション（オプション）

        Args:
            data: 検証対象のデータ
            **kwargs: 追加のパラメータ

        Returns:
            バリデーション結果
        """
        return True

    def preprocess(self, data: T, **kwargs) -> T:
        """前処理（オプション）

        Args:
            data: 前処理対象のデータ
            **kwargs: 追加のパラメータ

        Returns:
            前処理されたデータ
        """
        return data

    def postprocess(self, result: R, **kwargs) -> R:
        """後処理（オプション）

        Args:
            result: 後処理対象の結果
            **kwargs: 追加のパラメータ

        Returns:
            後処理された結果
        """
        return result
