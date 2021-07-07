"""
Logs the Narrator's narration using Python's standard logging library.
"""

import logging
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Generator

from screenpy import settings


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
        if self.enabled:
            return f"{self.level * self.whitespace}"
        return ""


# Indentation will be managed globally for the run.
indent = IndentManager()


class StdOutAdapter:
    """Adapt the Narrator's microphone to allow narration to stdout."""

    logger = logging.getLogger("screenpy")

    def act(self, wrapper: Callable, title: str, _: str) -> Generator:
        """Log the Act title to stdout, with some styling."""

        @wraps(wrapper)
        def wrapper_wrapper(*args: Any, **kwargs: Any) -> Callable:
            """Wrap the wrapper, so we log at the correct time."""
            self.logger.info(f"ACT {title.upper()}")
            return wrapper(*args, **kwargs)

        yield wrapper_wrapper

    def scene(self, wrapper: Callable, title: str, _: str) -> Generator:
        """Log the Scene title to stdout, with some styling."""

        @wraps(wrapper)
        def wrapper_wrapper(*args: Any, **kwargs: Any) -> Callable:
            """Wrap the wrapper, so we log at the correct time."""
            self.logger.info(f"Scene: {title.title()}")
            return wrapper(*args, **kwargs)

        yield wrapper_wrapper

    def beat(self, func: Callable, line: str) -> Generator:
        """Log the beat to stdout."""
        self.logger.info(f"{indent}{line}")
        with indent.next_level():
            yield func

    def aside(self, line: str) -> Generator:
        """Log the aside to stdout."""
        yield lambda: self.logger.info(f"{indent}{line}")
