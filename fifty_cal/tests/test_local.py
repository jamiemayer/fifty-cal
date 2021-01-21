from vobject import readOne

from fifty_cal.local import get_local_calendar


def test_local_calendar_events_loaded_as_expected():
    """
    Test that the events from the local calendar are loaded correctly.
    """
    loaded_cal = get_local_calendar("fifty_cal/tests/resources/test_calendar.ics")

    with open("fifty_cal/tests/resources/test_calendar.ics") as local_test:
        expected = local_test.read()

    assert str(loaded_cal) == str(readOne(expected))
