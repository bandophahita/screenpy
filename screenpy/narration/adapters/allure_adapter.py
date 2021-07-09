"""
Applies Allure's decorators and contexts to the Narrator's narration.
"""

from typing import Callable, Generator

import allure

from screenpy.narration.narrator import AIRY, EXTREME, HEAVY, LIGHT, NORMAL


class AllureAdapter:
    """Adapt the Narrator's microphone to allow narration to Allure."""

    GRAVITAS = {
        None: allure.severity_level.NORMAL,
        AIRY: allure.severity_level.TRIVIAL,
        LIGHT: allure.severity_level.MINOR,
        NORMAL: allure.severity_level.NORMAL,
        HEAVY: allure.severity_level.CRITICAL,
        EXTREME: allure.severity_level.BLOCKER,
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

    def aside(self, line: str) -> Generator:
        """Add the aside to the report."""
        with allure.step(line):
            yield lambda: "shh"
