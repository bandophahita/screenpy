import logging
from unittest import mock

from screenpy import settings
from screenpy.narration.adapters.stdout_adapter import indent
from screenpy.pacing import (
    act, scene, beat, aside,
    NORMAL,
    the_narrator,
    )


def prop():
    """The candlestick in the hall!"""


class TestIndentManager:
    """
    For the rest of the unit tests we expect the settings to have a
    single space as the indent char.  If that were to change, some of the
    tests may need to get updated.
    """
    def test_indentation_amount(self):
        assert indent.whitespace == settings.INDENT_SIZE * settings.INDENT_CHAR

    def test_indentation_char(self):
        assert settings.INDENT_CHAR == " "

    def test_indentation_size(self):
        assert settings.INDENT_SIZE == 4


class TestAct:
    @mock.patch("screenpy.narration.adapters.allure_adapter.allure")
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
    @mock.patch("screenpy.narration.adapters.allure_adapter.allure")
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
    @mock.patch("screenpy.narration.adapters.allure_adapter.allure")
    def test_allure_message(self, mocked_allure):
        beat_message = "test beat"
        test_func = beat(beat_message)(prop)

        test_func()

        mocked_allure.step.assert_called_once_with(beat_message)

    @mock.patch("screenpy.narration.adapters.allure_adapter.allure")
    def test_embedded_beat_allure_message(self, mocked_allure, caplog):
        """
        This test confirms that beat will start a new step context
        for each embedded function
        """
        self.level = 0

        @beat("1")
        def func1():
            self.level += 1

            @beat("2")
            def func2():
                self.level += 1

                @beat("3")
                def func3():
                    self.level += 1
                    pass

                func3()

            func2()

        with caplog.at_level(logging.INFO):
            func1()

        calls = mocked_allure.step.mock_calls

        assert len(calls) == 9
        assert calls[0].args[0] == "1"
        assert calls[1][0] == "().__enter__"
        assert calls[2].args[0] == f"2"
        assert calls[3][0] == "().__enter__"
        assert calls[4].args[0] == f"3"
        assert calls[5][0] == "().__enter__"
        assert calls[6][0] == "().__exit__"
        assert calls[7][0] == "().__exit__"
        assert calls[8][0] == "().__exit__"
        return

    @mock.patch("screenpy.narration.adapters.allure_adapter.allure")
    def test_buffered_beat_allure(self, mocked_allure, caplog):
        """Show the buffered logger does what it is supposed to."""
        limit = 5

        class AnotherProp:
            def __init__(self):
                return

            @beat("3")
            def use(self):
                aside("4")

        class BufferedLoggerProp:
            """<gestures frantically>"""

            def __init__(self):
                self.prop2 = AnotherProp()
                return

            @beat("1")
            def use(self):
                loop = 0
                with the_narrator.mic_cable_kinked():
                    while True:
                        the_narrator.clear_backup()
                        loop += 1
                        aside(f"2 loop {loop}")
                        self.prop2.use()
                        if loop >= limit:
                            break
                the_narrator.flush_backup()

        with caplog.at_level(logging.INFO):
            BufferedLoggerProp().use()

        calls = mocked_allure.step.mock_calls

        assert len(calls) == 12
        assert calls[0].args[0] == "1"
        assert calls[1][0] == "().__enter__"
        assert calls[2].args[0] == f"2 loop {limit}"
        assert calls[3][0] == "().__enter__"
        assert calls[4][0] == "().__exit__"
        assert calls[5].args[0] == f"3"
        assert calls[6][0] == "().__enter__"
        assert calls[7].args[0] == f"4"
        assert calls[8][0] == "().__enter__"
        assert calls[9][0] == "().__exit__"
        assert calls[10][0] == "().__exit__"
        assert calls[11][0] == "().__exit__"
        return

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
        indt = indent.whitespace
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
            assert record.message == f"{indt * level}{beat_message}"
        assert caplog.records[-1].message == beat_message

    @mock.patch("screenpy.narration.adapters.allure_adapter.allure")
    def test_log_buffering(self, mocked_allure, caplog):
        indt = indent.whitespace

        class BufferedLoggerProp:
            def __init__(self, prop1):
                self.prop1 = prop1

            @beat("Three murders.")
            def use(self):
                loop = 0
                limit = 5
                with the_narrator.mic_cable_kinked():
                    while True:
                        the_narrator.clear_backup()
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
            BufferedLoggerProp(Beat1Prop(Beat2Prop())).use()

        assert len(caplog.records) == 3
        assert f"Three murders." in caplog.messages
        assert f"{indt}How many loops? 5" in caplog.messages
        assert f"{indt * 2}inner loops? 5" in caplog.messages
        assert mocked_allure.step.call_count == 3

    def test_log_buffered(self, caplog):
        """Show the buffered logger does what it is supposed to."""
        indt = indent.whitespace
        limit = 5

        class AnotherProp:
            def __init__(self):
                return

            @beat("3")
            def use(self):
                aside("4")

        class BufferedLoggerProp:
            """<gestures frantically>"""

            def __init__(self):
                self.prop2 = AnotherProp()
                return

            @beat("1")
            def use(self):
                loop = 0
                with the_narrator.mic_cable_kinked():
                    while True:
                        the_narrator.clear_backup()
                        loop += 1
                        aside(f"2 loop {loop}")
                        self.prop2.use()
                        if loop >= limit:
                            break
                    assert len(the_narrator.backed_up_narrations) == 3
                    assert the_narrator.cable_kinked == True
                assert len(the_narrator.backed_up_narrations) == 0
                assert the_narrator.cable_kinked == False

        with caplog.at_level(logging.INFO):
            BufferedLoggerProp().use()

        assert len(caplog.messages) == 4
        assert "1" in caplog.messages
        assert f"{indt}2 loop {limit}" in caplog.messages
        assert f"{indt}3" in caplog.messages
        assert f"{indt * 2}4" in caplog.messages
        return


class TestAside:
    @mock.patch("screenpy.narration.adapters.allure_adapter.allure")
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
        indt = indent.whitespace
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
            assert message == f"{indt * (level + 1)}{aside_message}"
        assert aside_messages[-1] == f"{indt}{aside_message}"

    def test_aside_buffered(self, caplog):
        clue = "You don't need any help from me, Sir."

        class AsideProp:
            """The rope in the ballroom!"""

            def use(self):
                aside(
                    "Are you trying to make me look foolish "
                    "in front of the other guest?!?"
                    )

                with the_narrator.mic_cable_kinked():
                    aside(clue)
                    the_narrator.clear_backup()

                aside("That's right!")

        with caplog.at_level(logging.INFO):
            AsideProp().use()

        assert len(caplog.records) == 2
        assert all([clue not in record.message for record in caplog.records])
