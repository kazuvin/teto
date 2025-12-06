"""Tests for generator pipeline module."""

import pytest
from unittest.mock import MagicMock, Mock

from teto_core.generator.pipeline import ProcessingStep
from teto_core.generator.context import ProcessingContext


class ConcreteStep(ProcessingStep):
    """Concrete implementation of ProcessingStep for testing."""

    def __init__(self, name: str = "step", next_step: ProcessingStep = None):
        super().__init__(next_step)
        self.name = name
        self.processed = False
        self.process_count = 0

    def process(self, context: ProcessingContext) -> ProcessingContext:
        self.processed = True
        self.process_count += 1
        context.report_progress(f"{self.name} processed")
        return context


class ModifyingStep(ProcessingStep):
    """A step that modifies the context."""

    def __init__(self, modification: str):
        super().__init__()
        self.modification = modification

    def process(self, context: ProcessingContext) -> ProcessingContext:
        # Store modifications in a list attribute we add
        if not hasattr(context, "_modifications"):
            context._modifications = []
        context._modifications.append(self.modification)
        return context


@pytest.fixture
def mock_project():
    """Create a mock project for testing."""
    project = MagicMock()
    project.output = MagicMock()
    return project


@pytest.fixture
def context(mock_project):
    """Create a processing context for testing."""
    return ProcessingContext(project=mock_project)


@pytest.mark.unit
class TestProcessingStep:
    """Test suite for ProcessingStep."""

    def test_init_without_next(self):
        """Test initialization without next step."""
        step = ConcreteStep("test")
        assert step._next is None

    def test_init_with_next(self):
        """Test initialization with next step."""
        next_step = ConcreteStep("next")
        step = ConcreteStep("test", next_step=next_step)
        assert step._next is next_step

    def test_process_is_called(self, context):
        """Test that process is called during execute."""
        step = ConcreteStep("test")

        step.execute(context)

        assert step.processed is True

    def test_execute_returns_context(self, context):
        """Test that execute returns context."""
        step = ConcreteStep("test")

        result = step.execute(context)

        assert result is context

    def test_execute_with_next_step(self, context):
        """Test that execute calls next step."""
        step1 = ConcreteStep("step1")
        step2 = ConcreteStep("step2")
        step1._next = step2

        step1.execute(context)

        assert step1.processed is True
        assert step2.processed is True

    def test_execute_chain_order(self, context):
        """Test that steps are executed in order."""
        step1 = ModifyingStep("first")
        step2 = ModifyingStep("second")
        step3 = ModifyingStep("third")
        step1._next = step2
        step2._next = step3

        result = step1.execute(context)

        assert result._modifications == ["first", "second", "third"]

    def test_then_returns_next_step(self, context):
        """Test that then returns the next step."""
        step1 = ConcreteStep("step1")
        step2 = ConcreteStep("step2")

        result = step1.then(step2)

        assert result is step2

    def test_then_sets_next(self, context):
        """Test that then sets the next step."""
        step1 = ConcreteStep("step1")
        step2 = ConcreteStep("step2")

        step1.then(step2)

        assert step1._next is step2

    def test_fluent_chain(self, context):
        """Test fluent interface chaining with then()."""
        step1 = ConcreteStep("step1")
        step2 = ConcreteStep("step2")
        step3 = ConcreteStep("step3")

        step1.then(step2).then(step3)

        assert step1._next is step2
        assert step2._next is step3

    def test_fluent_chain_execution(self, context):
        """Test that fluent chain executes correctly."""
        step1 = ConcreteStep("step1")
        step2 = ConcreteStep("step2")
        step3 = ConcreteStep("step3")

        step1.then(step2).then(step3)
        step1.execute(context)

        assert step1.processed is True
        assert step2.processed is True
        assert step3.processed is True

    def test_progress_callback_called(self, mock_project):
        """Test that progress callback is called."""
        callback = Mock()
        context = ProcessingContext(project=mock_project, progress_callback=callback)
        step = ConcreteStep("test_step")

        step.execute(context)

        callback.assert_called_with("test_step processed")

    def test_multiple_execute_calls(self, context):
        """Test that step can be executed multiple times."""
        step = ConcreteStep("test")

        step.execute(context)
        step.execute(context)
        step.execute(context)

        assert step.process_count == 3
