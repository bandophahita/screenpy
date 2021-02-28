"""
An example of a test module that follows the typical unittest.TestCase
test structure. These tests exercise the Wait and Enter actions.
"""


import unittest

from selenium.webdriver import Firefox

from screenpy import AnActor, given, then, when
from screenpy.abilities import BrowseTheWeb
from screenpy.actions import Enter, Open, Wait
from screenpy.pacing import act, scene
from screenpy.questions import Text
from screenpy.resolutions import ReadsExactly

from ..user_interface.key_presses import ENTRY_INPUT, RESULT_TEXT, URL


class TestKeyPresses(unittest.TestCase):
    """
    Flexes Waiting with various strategies.
    """

    def setUp(self):
        self.actor = AnActor.named("Perry").who_can(BrowseTheWeb.using(Firefox()))

    @act("Perform")
    @scene("Wait for text")
    def test_wait_for_text(self):
        """Can select an option from a dropdown by text."""
        test_text = "H"
        Perry = self.actor

        given(Perry).was_able_to(Open.their_browser_on(URL))
        when(Perry).attempts_to(
            Enter.the_text(test_text).into_the(ENTRY_INPUT),
            Wait.for_the(RESULT_TEXT).to_contain_text(test_text),
        )
        then(Perry).should_see_the(
            (Text.of_the(RESULT_TEXT), ReadsExactly(f"You entered: {test_text}"))
        )

    @act("Perform")
    @scene("Wait with custom")
    def test_wait_with_custom(self):
        """Can wait using a contrived custom wait function."""
        test_text = "H"
        Perry = self.actor

        def text_to_have_all(locator, preamble, body, suffix):
            """Very contrived custom condition."""

            def _predicate(driver):
                element = driver.find_element(*locator)
                return f"{preamble} {body} {suffix}" in element.text

            return _predicate

        given(Perry).was_able_to(Open.their_browser_on(URL))
        when(Perry).attempts_to(
            Enter.the_text(test_text).into_the(ENTRY_INPUT),
            Wait()
            .using(text_to_have_all)
            .with_(RESULT_TEXT, "You", "entered:", test_text),
        )
        then(Perry).should_see_the(
            (Text.of_the(RESULT_TEXT), ReadsExactly(f"You entered: {test_text}"))
        )

    def tearDown(self):
        self.actor.exit_stage_right()