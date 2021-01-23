import datetime as dt

import pytest
from vobject import readOne
from vobject.base import Component

from fifty_cal.diff import CalendarDiff


@pytest.fixture
def local_cal():
    """
    Read test local calendar file into a `vobject.Component` object and return
    """
    with open("fifty_cal/tests/resources/dummy_local.ics", 'r') as calendar:
        cal = readOne(calendar.read())
    return cal


@pytest.fixture
def downloaded_cal():
    """
    Read test downloaded calendar file into a `vobject.Component` object and return
    """
    with open("fifty_cal/tests/resources/dummy_downloaded.ics", 'r') as calendar:
        cal = readOne(calendar.read())
    return cal


def test_no_diff_when_passed_identical_calendars(local_cal: Component):
    """
    When passed identical calendars, ensure that the diff is empty.
    """

    cal_diff = CalendarDiff(cal1=local_cal, cal2=local_cal)
    cal_diff.get_diff()

    assert cal_diff.diff == []


def test_sequence_removed_when_cleaned(downloaded_cal: Component):
    """
    Clean the downloaded calendar and ensure that any `sequence attributes are removed."
    """
    def get_sequence_count(calendar: Component) -> int:
        """
        Count and return the number of events in a calendar with a `sequence` attribute.
        """
        sequences = 0
        for event in calendar.contents["vevent"]:
            if hasattr(event, "sequence"):
                sequences += 1
        return sequences


    assert get_sequence_count(downloaded_cal) == 2


    cal_diff = CalendarDiff(cal1=downloaded_cal, cal2=downloaded_cal)

    cal_diff.clean_calendars()

    # Assert that the `sequence attributes have been removed`
    assert get_sequence_count(cal_diff.cal1_cleaned) == 0
    assert get_sequence_count(cal_diff.cal1_cleaned) == 0

    # Assert that the `sequence` attributes are still present in the original calendars.
    assert get_sequence_count(cal_diff.cal1) == 2
    assert get_sequence_count(cal_diff.cal2) == 2


def test_events_are_recognised_as_the_same_after_sequence_is_removed(downloaded_cal):
    """
    Cleaning calendars allows them to be matched once sequences are removed.

    Given a calendar which has an event modified (and hence a sequence number),
    ensure that the diff is found correctly once they have been cleaned.
    """

    original = downloaded_cal
    start = original.contents['vevent'][0].contents['dtstart'][0].value
    end = original.contents['vevent'][0].contents['dtend'][0].value
    sequence = int(original.contents['vevent'][0].contents["sequence"][0].value)

    # Update the original event by shifting it forward by one day
    update = Component.duplicate(downloaded_cal)
    new_start = dt.date(year=start.year, month=start.month, day=start.day+1)
    new_end = dt.date(year=end.year, month=end.month, day=end.day + 1)

    update.contents['vevent'][0].contents['dtstart'][0].value = new_start
    update.contents['vevent'][0].contents['dtend'][0].value = new_end
    # Increment sequence by 1
    new_sequence = str(sequence + 1)
    update.contents['vevent'][0].contents["sequence"][0].value = new_sequence

    cal_diff = CalendarDiff(cal1=original, cal2=update)

    # Set the cleaned calendars to be the original calendars so we can diff them.
    cal_diff.cal1_cleaned = Component.duplicate(cal_diff.cal1)
    cal_diff.cal2_cleaned = Component.duplicate(cal_diff.cal2)
    cal_diff.get_diff()

    # The presence of None in the diff tuple implies that one event isn't present in
    # the other calendar.

    assert None in cal_diff.diff[0]

    # Clean the calendars so that we can now diff the cleaned ones
    cal_diff.clean_calendars()
    # Get the diff on the cleaned calendars with no `sequence attribute`
    cal_diff.get_diff()

    # None should now not be in the diff.
    assert None not in cal_diff.diff

    # The contents should contain only the UID and the attributes that differ.
    expected_attributes = ["uid", "DTSTART", "DTEND"]
    assert list(cal_diff.diff[0][0].contents.keys()) == expected_attributes
    assert list(cal_diff.diff[0][1].contents.keys()) == expected_attributes



