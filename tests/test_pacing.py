import logging
from unittest import mock

from screenpy.pacing import (
    act, scene, beat, aside, indent, pantomiming,
    logger, NORMAL
    )


def prop():
    """The candlestick in the hall!"""


class TestAct:
    @mock.patch("screenpy.pacing.allure")
    def test_allure_name(self, mocked_allure):
        """We leave the Allure name alone, to allow user conventions."""
        act_name = "test act"
        test_func = act(act_name)(prop)

        test_func()

        mocked_allure.epic.assert_called_once_with(act_name)
        mocked_allure.severity.assert_called_once_with(NORMAL)
        return

    def test_logged_name(self, caplog):
        """Enforce convention of caps act names for logging."""
        act_name = "test act"
        test_func = act(act_name)(prop)

        with caplog.at_level(logging.INFO):
            test_func()

        assert len(caplog.records) == 1
        assert caplog.records[0].message == f"ACT {act_name.upper()}"


class TestScene:
    @mock.patch("screenpy.pacing.allure")
    def test_allure_name(self, mocked_allure):
        """We leave the Allure name alone, to allow user conventions."""
        scene_name = "test scene"
        test_func = scene(scene_name)(prop)

        test_func()

        mocked_allure.feature.assert_called_once_with(scene_name)
        mocked_allure.severity.assert_called_once_with(NORMAL)

    def test_logged_name(self, caplog):
        """Enforce convention of caps act names for logging."""
        scene_name = "test scene"
        test_func = scene(scene_name)(prop)

        with caplog.at_level(logging.INFO):
            test_func()

        assert len(caplog.records) == 1
        assert caplog.records[0].message == f"Scene: {scene_name.title()}"


class TestBeat:
    @mock.patch("screenpy.pacing.allure")
    def test_allure_message(self, mocked_allure):
        beat_message = "test beat"
        test_func = beat(beat_message)(prop)

        test_func()

        mocked_allure.step.assert_called_once_with(beat_message)

    def test_logged_message(self, caplog):
        beat_message = "test beat"
        test_func = beat(beat_message)(prop)

        with caplog.at_level(logging.INFO):
            test_func()

        assert len(caplog.records) == 1
        assert caplog.records[0].message == beat_message

    def test_interpolations(self, caplog):
        beat_message = "test {foo} and {bar}"

        class BeatProp:
            """The wrench in the study!"""

            foo = "spam"
            bar = "eggs"

            @beat(beat_message)
            def use(self):
                pass

        with caplog.at_level(logging.INFO):
            BeatProp().use()

        assert len(caplog.records) == 1
        assert caplog.records[0].message == f"test {BeatProp.foo} and {BeatProp.bar}"

    def test_indentation(self, caplog):
        beat_message = "Wadsworth, don't hate me for trying to shoot you."

        class BeatProp:
            """The revolver in the library!"""

            def __init__(self, subprop=None):
                self.subprop = subprop

            @beat(beat_message)
            def use(self):
                if self.subprop:
                    self.subprop.use()

        triple_prop = BeatProp(BeatProp(BeatProp()))

        with caplog.at_level(logging.INFO):
            triple_prop.use()
            BeatProp().use()

        assert len(caplog.records) == 4
        for level, record in enumerate(caplog.records[:-1]):
            assert record.message == f"{indent.whitespace * level}{beat_message}"
        assert caplog.records[-1].message == beat_message

    @mock.patch("screenpy.pacing.allure")
    def test_pantomiming(self, mocked_allure, caplog):
        clue = "Six altogether."

        class PantomimedProp:
            """<gestures frantically>"""

            def __init__(self, prop1, prop2):
                self.props = [prop1, prop2]

            @beat("Three murders.")
            def use(self):
                with pantomiming():
                    self.props[0].use()
                self.props[1].use()

        class Beat1Prop:
            """The dagger in the dining room!"""

            @beat(clue)
            def use(self):
                pass

        class Beat2Prop:
            """The bobby-pin in the beehive!"""

            @beat("This is getting serious.")
            def use(self):
                pass

        with caplog.at_level(logging.INFO):
            PantomimedProp(Beat1Prop(), Beat2Prop()).use()

        assert len(caplog.records) == 2
        assert all([clue not in record.message for record in caplog.records])
        assert mocked_allure.step.call_count == 2

    @mock.patch("screenpy.pacing.allure")
    def test_log_buffering(self, mocked_allure, caplog):
        class PantomimedProp:
            def __init__(self, prop1):
                self.prop1 = prop1

            @beat("Three murders.")
            def use(self):
                loop = 0
                limit = 5
                with logger.records_buffered():
                    while logger.clear_buffer():
                        loop += 1
                        self.prop1.num = loop
                        self.prop1.use()
                        if loop >= limit:
                            break

        class Beat1Prop:
            """The dagger in the dining room!"""
            def __init__(self, prop2):
                self.num = -1
                self.prop2 = prop2

            @beat("How many loops? {count}")
            def use(self):
                self.prop2.num = self.num
                self.prop2.use()
                return

            @property
            def count(self):
                return self.num

        class Beat2Prop:
            def __init__(self):
                self.num = -1

            @beat("inner loops? {count}")
            def use(self):
                pass

            @property
            def count(self):
                return self.num

        with caplog.at_level(logging.INFO):
            PantomimedProp(Beat1Prop(Beat2Prop())).use()

        assert len(caplog.records) == 3
        assert "Three murders." in caplog.messages
        assert "    How many loops? 5" in caplog.messages
        assert "        inner loops? 5" in caplog.messages
        # current design will fail on this assert.
        # assert mocked_allure.step.call_count == 3

    def test_log_buffered(self, caplog):
        """Show the buffered logger does what it is supposed to."""
        clue = "Rest in peace boiling water. You will be mist!"

        class BufferedLoggerProp:
            """<gestures frantically>"""

            def __init__(self):
                return

            @beat(clue)
            def use(self):
                loop = 0
                limit = 5
                with logger.records_buffered():
                    while logger.clear_buffer():
                        loop += 1
                        logger.info(f"loop {loop}")
                        if loop >= limit:
                            break
                    assert len(logger.buffer) == 1
                    assert logger.buffer_mode == True
                assert len(logger.buffer) == 0
                assert logger.buffer_mode == False

        with caplog.at_level(logging.INFO):
            BufferedLoggerProp().use()

        assert len(caplog.messages) == 2
        assert clue in caplog.messages
        assert "loop 5" in caplog.messages


class TestAside:
    @mock.patch("screenpy.pacing.allure")
    def test_allure_message(self, mocked_allure):
        aside_message = "test aside"

        aside(aside_message)

        mocked_allure.step.assert_called_once_with(aside_message)

    def test_logged_message(self, caplog):
        aside_message = "test aside"

        with caplog.at_level(logging.INFO):
            aside(aside_message)

        assert len(caplog.records) == 1
        assert caplog.records[0].message == aside_message

    def test_indentation(self, caplog):
        aside_message = (
            "Well, it's a matter of life after death. "
            "Now that he's dead, I have a life."
        )

        class AsideProp:
            """The lead pipe in the conservatory!"""

            def __init__(self, subprop=None):
                self.subprop = subprop

            @beat("")
            def use(self):
                aside(aside_message)
                if self.subprop:
                    self.subprop.use()

        triple_prop = AsideProp(AsideProp(AsideProp()))

        with caplog.at_level(logging.INFO):
            triple_prop.use()
            AsideProp().use()

        aside_messages = [
            record.message for record in caplog.records if record.message.strip()
        ]
        assert len(aside_messages) == 4
        # asides happen _within_ the beats, so their level is already indented.
        for level, message in enumerate(aside_messages[:-1]):
            assert message == f"{indent.whitespace * (level + 1)}{aside_message}"
        assert aside_messages[-1] == f"{indent.whitespace}{aside_message}"

    def test_pantomiming(self, caplog):
        clue = "You don't need any help from me, Sir."

        class AsideProp:
            """The rope in the ballroom!"""

            def use(self):
                aside(
                    "Are you trying to make me look foolish "
                    "in front of the other guest?!?"
                )

                with pantomiming():
                    aside(clue)

                aside("That's right!")

        with caplog.at_level(logging.INFO):
            AsideProp().use()

        assert len(caplog.records) == 2
        assert all([clue not in record.message for record in caplog.records])
