"""処理パイプラインの基底クラス"""

from abc import ABC, abstractmethod
from .context import ProcessingContext


class ProcessingStep(ABC):
    """処理ステップの基底クラス

    Chain of Responsibility パターンを使用して、
    複数の処理ステップをチェーン接続する
    """

    def __init__(self, next_step: "ProcessingStep" = None):
        """初期化

        Args:
            next_step: 次の処理ステップ（オプション）
        """
        self._next = next_step

    @abstractmethod
    def process(self, context: ProcessingContext) -> ProcessingContext:
        """このステップの処理を実行

        Args:
            context: 処理コンテキスト

        Returns:
            更新されたコンテキスト
        """
        pass

    def execute(self, context: ProcessingContext) -> ProcessingContext:
        """このステップと次のステップを実行

        Args:
            context: 処理コンテキスト

        Returns:
            最終的なコンテキスト
        """
        context = self.process(context)

        if self._next:
            return self._next.execute(context)

        return context

    def then(self, next_step: "ProcessingStep") -> "ProcessingStep":
        """次のステップをチェーンに追加（Fluent Interface）

        Args:
            next_step: 次の処理ステップ

        Returns:
            次のステップ（チェーン可能）
        """
        self._next = next_step
        return next_step
