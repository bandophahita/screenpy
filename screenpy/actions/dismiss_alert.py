"""
An action to dismiss an alert.
"""

from screenpy.abilities import BrowseTheWeb
from screenpy.actor import Actor
from screenpy.pacing import aside, beat
from screenpy.protocols import Performable


class DismissAlert(Performable):
    """Dismiss an alert.

    Abilities Required:
        |BrowseTheWeb|

    Examples::

        the_actor.attempts_to(DismissAlert())
    """

    @beat("{} dismisses the alert.")
    def perform_as(self, the_actor: Actor) -> None:
        """Direct the actor to dismiss the alert."""
        browser = the_actor.uses_ability_to(BrowseTheWeb).browser
        alert = browser.switch_to.alert
        aside(f'... the alert says "{alert.text}"')
        alert.dismiss()
