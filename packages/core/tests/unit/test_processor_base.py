"""ProcessorBase のテスト"""

import pytest
from teto_core.processors.base import ProcessorBase


class SimpleProcessor(ProcessorBase[str, str]):
    """テスト用の簡単なプロセッサー"""

    def process(self, data: str, **kwargs) -> str:
        """文字列を大文字に変換"""
        return data.upper()


class ValidatingProcessor(ProcessorBase[int, int]):
    """バリデーション機能を持つプロセッサー"""

    def validate(self, data: int, **kwargs) -> bool:
        """正の数のみ許可"""
        return data > 0

    def process(self, data: int, **kwargs) -> int:
        """数値を2倍にする"""
        return data * 2


class PreprocessingProcessor(ProcessorBase[str, str]):
    """前処理・後処理を持つプロセッサー"""

    def preprocess(self, data: str, **kwargs) -> str:
        """前処理: 前後の空白を削除"""
        return data.strip()

    def process(self, data: str, **kwargs) -> str:
        """メイン処理: 大文字に変換"""
        return data.upper()

    def postprocess(self, result: str, **kwargs) -> str:
        """後処理: 感嘆符を追加"""
        return f"{result}!"


class TestProcessorBase:
    """ProcessorBase のテスト"""

    def test_simple_execute(self):
        """シンプルな実行テスト"""
        processor = SimpleProcessor()
        result = processor.execute("hello")
        assert result == "HELLO"

    def test_validation_success(self):
        """バリデーション成功時のテスト"""
        processor = ValidatingProcessor()
        result = processor.execute(5)
        assert result == 10

    def test_validation_failure(self):
        """バリデーション失敗時のテスト"""
        processor = ValidatingProcessor()
        with pytest.raises(ValueError) as exc_info:
            processor.execute(-1)
        assert "Validation failed" in str(exc_info.value)

    def test_preprocessing_and_postprocessing(self):
        """前処理・後処理のテスト"""
        processor = PreprocessingProcessor()
        result = processor.execute("  hello  ")
        assert result == "HELLO!"

    def test_kwargs_passing(self):
        """kwargs がすべてのメソッドに渡されることを確認"""

        class KwargsProcessor(ProcessorBase[str, str]):
            def validate(self, data: str, **kwargs) -> bool:
                return kwargs.get("allow", True)

            def preprocess(self, data: str, **kwargs) -> str:
                prefix = kwargs.get("prefix", "")
                return f"{prefix}{data}"

            def process(self, data: str, **kwargs) -> str:
                return data.upper()

            def postprocess(self, result: str, **kwargs) -> str:
                suffix = kwargs.get("suffix", "")
                return f"{result}{suffix}"

        processor = KwargsProcessor()
        result = processor.execute("test", prefix="[", suffix="]", allow=True)
        assert result == "[TEST]"

    def test_validation_with_kwargs(self):
        """kwargs を使ったバリデーションのテスト"""

        class ConditionalProcessor(ProcessorBase[int, int]):
            def validate(self, data: int, **kwargs) -> bool:
                min_value = kwargs.get("min_value", 0)
                return data >= min_value

            def process(self, data: int, **kwargs) -> int:
                return data * 2

        processor = ConditionalProcessor()

        # min_value=10 の場合、5 は無効
        with pytest.raises(ValueError):
            processor.execute(5, min_value=10)

        # min_value=3 の場合、5 は有効
        result = processor.execute(5, min_value=3)
        assert result == 10


class TestProcessorBaseInheritance:
    """ProcessorBase の継承に関するテスト"""

    def test_abstract_process_method(self):
        """process メソッドが抽象メソッドであることを確認"""
        with pytest.raises(TypeError):
            # process メソッドを実装していないとインスタンス化できない
            class IncompleteProcessor(ProcessorBase[str, str]):
                pass

            IncompleteProcessor()

    def test_default_validate_returns_true(self):
        """デフォルトの validate が True を返すことを確認"""
        processor = SimpleProcessor()
        assert processor.validate("test") is True

    def test_default_preprocess_returns_data(self):
        """デフォルトの preprocess がデータをそのまま返すことを確認"""
        processor = SimpleProcessor()
        assert processor.preprocess("test") == "test"

    def test_default_postprocess_returns_result(self):
        """デフォルトの postprocess が結果をそのまま返すことを確認"""
        processor = SimpleProcessor()
        assert processor.postprocess("TEST") == "TEST"
