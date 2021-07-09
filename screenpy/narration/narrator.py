"""
The Narrator for the screenplay, who informs the audience what the actors are
doing. The Narrator's microphone is modular, allowing for any number of
adapters to be applied. Adapters must follow the Adapter protocol outlined in
screenpy.protocols.
"""

from contextlib import contextmanager
from typing import Any, Callable, Generator, List, Optional, Tuple, Union

from screenpy.protocols import Adapter

# pylint: disable=stop-iteration-return
# The above may be a false-positive since this file calls `next` directly
# instead of iterating over the generators.

Kwargs = Union[Callable, str, None]
Entangled = Tuple[Callable, List[Generator]]

# Levels for gravitas
AIRY = "airy"
LIGHT = "light"
NORMAL = "normal"
HEAVY = "heavy"
EXTREME = "extreme"


class Narrator:
    """The narrator conveys the story to the audience."""

    def __init__(self, adapters: Optional[List[Adapter]] = None) -> None:
        self.adapters: List[Adapter] = adapters or []
        self.on_air = True
        self.cable_kinked = False
        self.backed_up_narrations: List[Tuple[str, dict]] = []

    @contextmanager
    def off_the_air(self) -> Generator:
        """Turns off narration completely during this context."""
        self.on_air = False
        yield
        self.on_air = True

    @contextmanager
    def mic_cable_kinked(self) -> Generator:
        """Put a kink in the microphone line, storing narrations during the context."""
        self.cable_kinked = True
        yield
        self.cable_kinked = False

    def clear_backup(self) -> None:
        """Clears the backed up narration from a kinked cable."""
        self.backed_up_narrations = []

    def flush_backup(self) -> None:
        """Let all the backed-up narration flow through the kink."""
        for channel, kwargs in self.backed_up_narrations:
            enclosed_func, exits = self._entangle_func(channel, **kwargs)
            enclosed_func()
            for exit_ in exits:
                next(exit_, None)
        self.clear_backup()

    def _entangle_func(self, channel: str, **channel_kwargs: Kwargs) -> Entangled:
        """Entangle the function in the adapters' contexts and decorations.

        Each adapter yields the function back, potentially applying its own
        context or decorators. We extract the function with that context still
        intact. We will need to close the context as we leave, so we store
        each level of entanglement in exits.
        """
        exits = []
        for adapter in self.adapters:
            closure = getattr(adapter, channel)(**channel_kwargs)
            enclosed_func = next(closure)
            exits.append(closure)
        return enclosed_func, exits

    @contextmanager
    def narrate(self, channel: str, **kwargs: Kwargs) -> Generator:
        """Handle the entanglement of encapsulation from each adapter."""
        channel_kwargs = {
            key: value for key, value in kwargs.items() if value is not None
        }
        if self.cable_kinked:
            enclosed_func = kwargs["func"]
            kwargs["func"] = lambda: "overflow"
            self.backed_up_narrations.append((channel, kwargs))
        else:
            enclosed_func, exits = self._entangle_func(channel, **channel_kwargs)

        try:
            yield enclosed_func
        finally:
            if not self.cable_kinked:
                # close all the closures
                for exit_ in exits:
                    next(exit_, None)

    def announcing_the_act(
        self, func: Callable, line: str, gravitas: str = NORMAL
    ) -> Any:
        """Announce the name of the act into the microphone."""
        if not self.on_air:
            return func
        return self.narrate("act", func=func, line=line, gravitas=gravitas)

    def setting_the_scene(
        self, func: Callable, line: str, gravitas: str = NORMAL
    ) -> Any:
        """Set the scene into the microphone."""
        if not self.on_air:
            return func
        return self.narrate("scene", func=func, line=line, gravitas=gravitas)

    def stating_a_beat(self, func: Callable, line: str) -> Any:
        """State the beat into the microphone."""
        if not self.on_air:
            return func
        return self.narrate("beat", func=func, line=line)

    def whispering_an_aside(self, line: str) -> Any:
        """Whisper the aside (as a stage-whisper) into the microphone."""
        if not self.on_air:
            return lambda: "<static>"
        return self.narrate("aside", func=lambda: "ssh", line=line)
