"""
Provides decorators to group your tests into acts (features) and scenes
(cases), and provide the gravitas (severity) of those groupings. This will
both use Allure's marking to group the tests together for those reports
and also set the logging severity for Python's built-in logging library.
"""

import logging
import re
from contextlib import contextmanager
from enum import Enum
from functools import wraps
from typing import Any, Callable, Generator, List, Type

import allure

from . import settings

TRIVIAL = allure.severity_level.TRIVIAL
MINOR = allure.severity_level.MINOR
NORMAL = allure.severity_level.NORMAL
CRITICAL = allure.severity_level.CRITICAL
BLOCKER = allure.severity_level.BLOCKER

Function = Callable[..., Any]

__logger: Type[logging.Logger] = logging.getLoggerClass()


class ScreenPyLogger(__logger):  # type: ignore
    """
    A buffered logger which provides the ability to cache records when needed.
    """

    def __init__(
        self,
        name: str,
        level: int = logging.NOTSET,
        capacity: int = 100,
        flush_level: int = logging.ERROR,
    ) -> None:
        super().__init__(name, level)
        self.buffer: List[logging.LogRecord] = []
        self.buffer_mode = False
        self.capacity = capacity
        self.flush_level = flush_level

    def handle(self, record: logging.LogRecord) -> None:
        """
        Buffers the record or sends directly to be handled depending on the
        buffer_mode.
        """
        if not self.buffer_mode:
            super().handle(record)
        else:
            self.buffer.append(record)
            if self.should_flush(record):
                self.flush_buffer()

    def should_flush(self, record: logging.LogRecord) -> bool:
        """Checks if flushing should occur"""
        return (len(self.buffer) >= self.capacity) or (
            record.levelno >= self.flush_level
        )

    def flush_buffer(self) -> None:
        """Sends all the records in the buffer to be handled"""
        for record in self.buffer:
            super().handle(record)
        self.clear_buffer()

    def clear_buffer(self) -> bool:
        """Clears the buffer"""
        self.buffer = []
        return True

    def set_capacity(self, capacity: int) -> None:
        """Sets the buffer capacity"""
        self.capacity = capacity

    @contextmanager
    def records_buffered(self) -> Generator:
        """
        buffers the logged records while context manager is enabled.

        Can be used in conjunction with .clear_buffer() to only log the last
        loop in a while loop.
        """
        self.buffer_mode = True

        try:
            yield
        finally:
            self.flush_buffer()
            self.buffer_mode = False


def create_logger(name: str) -> ScreenPyLogger:
    """
    This will overrides the default logger class with ScreenPyLogger,
    create the logger, and then put the default logger back to the original.
    """
    logging.setLoggerClass(ScreenPyLogger)
    # pycharm gets confused about getLogger returning ScreenPyLogger.
    # mypy also doesn't understand this since it is a dynamic call.

    # noinspection PyTypeChecker
    lger: ScreenPyLogger = logging.getLogger(name)  # type: ignore
    logging.setLoggerClass(__logger)
    # thelogger.setLevel(logging.DEBUG)
    # thelogger.propagate = False
    return lger


logger = create_logger("screenpy")


@contextmanager
def no_logging() -> Generator:
    """Turn off logging of actions during the context window."""
    settings.LOG_ACTIONS = False
    try:
        yield
    finally:
        settings.LOG_ACTIONS = True


pantomiming = no_logging


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
            yield
        finally:
            self.remove_level()

    def __str__(self) -> str:
        if self.enabled:
            return f"{self.level * self.whitespace}"
        return ""


# Indentation will be managed globally for the run.
indent = IndentManager()


def act(title: str, gravitas: Enum = NORMAL) -> Callable[[Function], Function]:
    """Decorator to mark an "act".

    Using the same title for this decorator on multiple test cases will group
    your tests under the same epic in Allure's behavior view. Using the same
    gravitas will group the tests by that severity, which allows you to run
    all those tests together using Allure's pytest plugin.

    Args:
        title: the title of this "act" (the epic name).
        gravitas: how serious this act is (the severity level).
    """

    def decorator(func: Function) -> Function:
        @allure.epic(title)
        @allure.severity(gravitas)
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.info(f"ACT {title.upper()}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def scene(title: str, gravitas: Enum = NORMAL) -> Callable[[Function], Function]:
    """Decorator to mark a "scene".

    Using the same title for this decorator on multiple test cases will group
    your tests under the same "feature" in Allure's behavior view. Using the
    same gravitas will group the tests by that severity, which allows you to
    run all those tests together using Allure's pytest plugin

    Args:
        title: the title of this "scene" (the feature).
        gravitas: how serious this scene is (the severity level).
    """

    def decorator(func: Function) -> Function:
        @allure.feature(title)
        @allure.severity(gravitas)
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.info(f"Scene: {title.title()}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def beat(line: str) -> Callable[[Function], Function]:
    """Decorator to describe a "beat" (a step in a test).

    A beat's line can contain markers for replacement via str.format(), which
    will be figured out from the properties of a decorated method's class.

    For example, if the beat line is "{} clicks on the {target}", then "{}"
    will be replaced by the Actor's name, and "{target}" will be replaced
    using the Click action's ``target`` property (e.g. ``Click.target``).

    Args:
        line: the line spoken during this "beat" (the step description).
    """

    def decorator(func: Function) -> Function:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not settings.LOG_ACTIONS:
                return func(*args, **kwargs)

            action = args[0] if len(args) > 0 else None
            actor = args[1] if len(args) > 1 else ""
            markers = re.findall(r"\{([^0-9\}]+)}", line)
            cues = {mark: getattr(action, mark) for mark in markers}

            completed_line = f"{indent}{line.format(actor, **cues)}"
            logger.info(completed_line)
            with allure.step(completed_line):
                with indent.next_level():
                    retval = func(*args, **kwargs)
                    if retval is not None:
                        aside(f"=> {retval}")

            return retval

        return wrapper

    return decorator


def aside(line: str) -> None:
    """A line spoken in a stage whisper to the audience (log a message)."""
    if not settings.LOG_ACTIONS:
        return

    completed_line = f"{indent}{line}"
    logger.info(completed_line)
    with allure.step(completed_line):
        # Can't call method directly, have to enter or decorate
        pass
