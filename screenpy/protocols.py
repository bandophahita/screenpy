"""
Protocols to define the expected functions each of the types of Screenplay
Pattern will need to implement.

ScreenPy uses structural subtyping to define its "subclasses" -- for example,
any class that implements ``perform_as`` can be an Action, any class that
implements ``answered_by`` is a Question, etc. For more information, see
https://mypy.readthedocs.io/en/stable/protocols.html
"""

from typing import TYPE_CHECKING, Any, Callable, Generator

from selenium.webdriver.common.action_chains import ActionChains
from typing_extensions import Protocol

if TYPE_CHECKING:
    from .actor import Actor


class Answerable(Protocol):
    """Questions are Answerable"""

    def answered_by(self, the_actor: "Actor") -> Any:
        """
        Pose the Question to the Actor, who will investigate and provide the
        answer to their best knowledge.

        Args:
            the_actor: the |Actor| who will answer the |Question|.

        Returns:
            The answer, based on the sleuthing the Actor has done.
        """
        ...


class Chainable(Protocol):
    """Actions that can be added to a chain are Chainable"""

    def add_to_chain(self, the_actor: "Actor", the_chain: ActionChains) -> None:
        """
        Add this chainable Action to an in-progress chain.

        Args:
            the_actor: the |Actor| who will be performing the |Action| chain.
            the_chain: the |ActionChains| instance that is being built.
        """
        ...


class Forgettable(Protocol):
    """Abilities are Forgettable"""

    def forget(self) -> None:
        """
        Forget this Ability by doing any necessary cleanup (quitting browsers,
        closing connections, etc.)
        """
        ...


class Performable(Protocol):
    """Actions that can be performed are Performable"""

    def perform_as(self, the_actor: "Actor") -> None:
        """
        Direct the Actor to perform this Action.

        Args:
            the_actor: the |Actor| who will perform this |Action|.
        """
        ...


class Adapter(Protocol):
    """Required functions for an Adapter to the Narrator.

    Adapters allow the Narrator's microphone to broadcast to multiple logging
    sources, such as stdout or Allure.

    Each of the required methods pass in the message the narrator is set to
    speak, along with the function that is decorated by the corresponding
    ``screenpy.pacing`` function. The narrator expects the function to be
    returned. This allows the adapter to decorate the test step, log the
    message, or both, or neither!

    Adapters must follow the function signatures exactly, even if the adapter
    does not use one or more of them. The Narrator passes these arguments in
    as keyword arguments.
    """

    def act(self, func: Callable, line: str, gravitas: str) -> Generator:
        """Handle narrating an Act, which designates a group of tests."""
        ...

    def scene(self, func: Callable, line: str, gravitas: str) -> Generator:
        """Handle narrating a Scene, which designates a subgroup of tests."""
        ...

    def beat(self, func: Callable, line: str) -> Generator:
        """Handle narrating a Beat, which is a step in a test."""
        ...

    def aside(self, func: Callable, line: str) -> Generator:
        """Handle narrating an Aside, which can happen any time."""
        ...
