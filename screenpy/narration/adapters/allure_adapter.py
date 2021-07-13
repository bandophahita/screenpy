"""
Applies Allure's decorators and contexts to the Narrator's narration.
"""

from typing import Callable, Generator

import allure

from screenpy.narration import narrator


class AllureAdapter:
    """Adapt the Narrator's microphone to allow narration to Allure."""

    chain_direction = narrator.FORWARD

    GRAVITAS = {
        None: allure.severity_level.NORMAL,
        narrator.AIRY: allure.severity_level.TRIVIAL,
        narrator.LIGHT: allure.severity_level.MINOR,
        narrator.NORMAL: allure.severity_level.NORMAL,
        narrator.HEAVY: allure.severity_level.CRITICAL,
        narrator.EXTREME: allure.severity_level.BLOCKER,
    }

    def act(self, func: Callable, line: str, gravitas: str) -> Generator:
        """Announce the Act."""
        func = allure.epic(line)(func)
        if gravitas:
            func = allure.severity(self.GRAVITAS[gravitas])(func)
        yield func

    def scene(self, func: Callable, line: str, gravitas: str) -> Generator:
        """Set the Scene."""
        func = allure.feature(line)(func)
        if gravitas:
            func = allure.severity(self.GRAVITAS[gravitas])(func)
        yield func

    def beat(self, func: Callable, line: str) -> Generator:
        """Encapsulate the function within the beat context."""
        with allure.step(line):
            yield func

    def aside(self, func: Callable, line: str) -> Generator:
        """Add the aside to the report."""
        with allure.step(line):
            yield func
