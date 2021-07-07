"""
The Narrator for the screenplay, who informs the audience what the actors are
doing. The Narrator's microphone is modular, allowing for any number of
adapters to be applied. Adapters must follow the Adapter protocol outlined in
screenpy.protocols.
"""

from contextlib import contextmanager
from typing import Callable, Generator, List, Optional

from screenpy.protocols import Adapter

# pylint: disable=stop-iteration-return

# Levels for gravitas
AIRY = "airy"
LIGHT = "light"
NORMAL = "normal"
HEAVY = "heavy"
EXTREME = "extreme"


class Narrator:
    """The narrator conveys the story to the audience."""

    adapters: List[Adapter]

    def __init__(self, adapters: Optional[List[Adapter]] = None) -> None:
        self.adapters = adapters or []

    # def channel(channel: str) -> Callable:
    #     """A factory for the narration channels: act, scene, beat, aside."""

    #     @contextmanager
    #     def vocalize(
    #         self, func: Callable, message: str, gravitas: str = NORMAL
    #     ) -> Generator:
    #         """Handle the multi-encapsulation from each adapter."""
    #         closure = func
    #         exits = []

    #         # This loops through all the adapters attached to the narrator's
    #         # microphone. Each adapter yields the function back, potentially
    #         # applying its own context or decorators. We extract the function
    #         # with the context still intact. We will need to close the context
    #         # as we leave, so we store each level in exits.
    #         for adapter in self.adapters:
    #             closure = next(getattr(adapter, channel)(closure, message, gravitas))
    #             exits.append(closure)

    #         try:
    #             yield closure
    #         finally:
    #             # close all the closures
    #             for exit_ in exits:
    #                 next(exit_, None)

    #     return vocalize

    @contextmanager
    def announcing_the_act(
        self, func: Callable, message: str, gravitas: str = NORMAL
    ) -> Generator:
        """Handle the multi-encapsulation from each adapter."""
        exits = []

        # This loops through all the adapters attached to the narrator's
        # microphone. Each adapter yields the function back, potentially
        # applying its own context or decorators. We extract the function
        # with the context still intact. We will need to close the context
        # as we leave, so we store each level in exits.
        for adapter in self.adapters:
            closure = adapter.act(func, message, gravitas)
            func = next(closure)
            exits.append(closure)

        try:
            yield func
        finally:
            # close all the closures
            for exit_ in exits:
                next(exit_, None)

    @contextmanager
    def setting_the_scene(
        self, func: Callable, message: str, gravitas: str = NORMAL
    ) -> Generator:
        """Handle the multi-encapsulation from each adapter."""
        exits = []

        # This loops through all the adapters attached to the narrator's
        # microphone. Each adapter yields the function back, potentially
        # applying its own context or decorators. We extract the function
        # with the context still intact. We will need to close the context
        # as we leave, so we store each level in exits.
        for adapter in self.adapters:
            closure = adapter.scene(func, message, gravitas)
            func = next(closure)
            exits.append(closure)

        try:
            yield func
        finally:
            # close all the closures
            for exit_ in exits:
                next(exit_, None)

    @contextmanager
    def stating_a_beat(self, func: Callable, message: str) -> Generator:
        """Handle the multi-encapsulation from each adapter."""
        exits = []

        # This loops through all the adapters attached to the narrator's
        # microphone. Each adapter yields the function back, potentially
        # applying its own context or decorators. We extract the function
        # with the context still intact. We will need to close the context
        # as we leave, so we store each level in exits.
        for adapter in self.adapters:
            closure = adapter.beat(func, message)
            func = next(closure)
            exits.append(closure)

        try:
            yield func
        finally:
            # close all the closures
            for exit_ in exits:
                next(exit_, None)

    @contextmanager
    def whispering_an_aside(self, message: str) -> Generator:
        """Handle the multi-encapsulation from each adapter."""
        exits = []

        # This loops through all the adapters attached to the narrator's
        # microphone. Each adapter yields the function back, potentially
        # applying its own context or decorators. We extract the function
        # with the context still intact. We will need to close the context
        # as we leave, so we store each level in exits.
        for adapter in self.adapters:
            closure = adapter.aside(message)
            func = next(closure)
            exits.append(closure)

        try:
            yield func
        finally:
            # close all the closures
            for exit_ in exits:
                next(exit_, None)
