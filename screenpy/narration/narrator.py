"""
The Narrator for the screenplay, who informs the audience what the actors are
doing. The Narrator's microphone is modular, allowing for any number of
adapters to be applied. Adapters must follow the Adapter protocol outlined in
screenpy.protocols.
"""

from contextlib import contextmanager
from typing import Callable, ContextManager, Generator, List, Optional, Union

from screenpy.protocols import Adapter

# pylint: disable=stop-iteration-return
# The above may be a false-positive since this file calls `next` directly
# instead of iterating over the generators.

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

    @contextmanager
    def vocalize(self, channel: str, **kwargs: Union[Callable, str, None]) -> Generator:
        """Handle the entanglement of encapsulation from each adapter."""
        channel_args = {
            key: value for key, value in kwargs.items() if value is not None
        }
        exits = []

        # This loops through all the adapters attached to the narrator's
        # microphone. Each adapter yields the function back, potentially
        # applying its own context or decorators. We extract the function
        # with the context still intact. We will need to close the context
        # as we leave, so we store each level in exits.
        for adapter in self.adapters:
            closure = getattr(adapter, channel)(**channel_args)
            enclosed_func = next(closure)
            exits.append(closure)

        try:
            yield enclosed_func
        finally:
            # close all the closures
            for exit_ in exits:
                next(exit_, None)

    def announcing_the_act(
        self, func: Callable, line: str, gravitas: str = NORMAL
    ) -> ContextManager:
        """Announce the name of the act into the microphone."""
        return self.vocalize("act", func=func, line=line, gravitas=gravitas)

    def setting_the_scene(
        self, func: Callable, line: str, gravitas: str = NORMAL
    ) -> ContextManager:
        """Set the scene into the microphone."""
        return self.vocalize("scene", func=func, line=line, gravitas=gravitas)

    def stating_a_beat(self, func: Callable, line: str) -> ContextManager:
        """State the beat into the microphone."""
        return self.vocalize("beat", func=func, line=line)

    def whispering_an_aside(self, line: str) -> ContextManager:
        """Whisper the aside (as a stage-whisper) into the microphone."""
        return self.vocalize("aside", line=line)
