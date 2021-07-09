"""
Logs the Narrator's narration using Python's standard logging library.
"""

import logging
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Generator

from screenpy import settings

# pylint: disable=unused-argument
# Adapters must use the function signatures exactly in order to have the
# correct arguments passed to them. This adapter does not use the gravitas
# argument since log severity doesn't line up with test criticality, so the
# functions accept the argument but don't do anything with it.


class IndentManager:
    """Handle the indentation for CLI logging."""

    def __init__(self) -> None:
        self.level = 0
        self.indent = settings.INDENT_SIZE
        self.whitespace = self.indent * settings.INDENT_CHAR
        self.enabled = settings.INDENT_LOGS

    def add_level(self) -> None:
        """Increase the indentation level."""
        self.level += 1

    def remove_level(self) -> None:
        """Decrease the indentation level."""
        if self.level > 0:
            self.level -= 1

    @contextmanager
    def next_level(self) -> Generator:
        """Move to the next level of indentation, with context."""
        self.add_level()
        try:
            yield self.level
        finally:
            self.remove_level()

    def __str__(self) -> str:
        """Allow this manager to be used directly for string formatting."""
        if self.enabled:
            return f"{self.level * self.whitespace}"
        return ""


# Indentation will be managed globally for the run.
indent = IndentManager()


class StdOutAdapter:
    """Adapt the Narrator's microphone to allow narration to stdout."""

    logger = logging.getLogger("screenpy")

    def act(self, func: Callable, line: str, gravitas: str) -> Generator:
        """Log the Act title to stdout, with some styling."""

        @wraps(func)
        def func_wrapper(*args: Any, **kwargs: Any) -> Callable:
            """Wrap the func, so we log at the correct time."""
            self.logger.info(f"ACT {line.upper()}")
            return func(*args, **kwargs)

        yield func_wrapper

    def scene(self, func: Callable, line: str, gravitas: str) -> Generator:
        """Log the Scene title to stdout, with some styling."""

        @wraps(func)
        def func_wrapper(*args: Any, **kwargs: Any) -> Callable:
            """Wrap the func, so we log at the correct time."""
            self.logger.info(f"Scene: {line.title()}")
            return func(*args, **kwargs)

        yield func_wrapper

    def beat(self, func: Callable, line: str) -> Generator:
        """Log the beat to stdout, increasing the indent level."""

        @wraps(func)
        def func_wrapper(*args: Any, **kwargs: Any) -> Callable:
            """Wrap the func, so we log at the correct time."""
            self.logger.info(f"{indent}{line}")
            with indent.next_level():
                return func(*args, **kwargs)

        yield func_wrapper

    def aside(self, func: Callable, line: str) -> Generator:
        """Log the aside to stdout."""

        @wraps(func)
        def func_wrapper(*args: Any, **kwargs: Any) -> Callable:
            """Wrap the func, so we log at the correct time."""
            self.logger.info(f"{indent}{line}")
            return func(*args, **kwargs)

        yield func_wrapper
