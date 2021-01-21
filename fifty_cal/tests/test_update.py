import datetime as dt

import pytest
from vobject.base import Component, readOne

from fifty_cal.update import get_diff


def test_new_events_in_one_calendar_are_found():
    """
    Test that new downloaded events are identified.
    """

    with open("tests/resources/dummy_downloaded.ics") as calendar:
        calendar = readOne(calendar)

    updated_calendar = Component.duplicate(calendar)

    assert get_diff(calendar, updated_calendar) == []

    updated_calendar.add("vevent").add("summary").value = "Test Event"

    assert (
        get_diff(calendar, updated_calendar)[0][1]
        == updated_calendar.contents["vevent"][-1]
    )


def test_updated_event_is_found():
    """
    Test that when a single event has been updated that it is picked up in the diff.
    """
    with open("tests/resources/dummy_downloaded.ics") as calendar:
        calendar = readOne(calendar)

    updated_calendar = Component.duplicate(calendar)

    updated_calendar.contents["vevent"][-1].dtstart.value = dt.datetime(
        2021, 1, 12, 10, 0, tzinfo=dt.timezone.utc
    )
    updated_calendar.contents["vevent"][-1].dtend.value = dt.datetime(
        2021, 1, 12, 11, 0, tzinfo=dt.timezone.utc
    )

    actual = get_diff(calendar, updated_calendar)

    assert (
        actual[0][0].contents["uid"] == calendar.contents["vevent"][-1].contents["uid"]
    )

    assert (
        actual[0][0].contents["DTSTART"]
        == calendar.contents["vevent"][-1].contents["dtstart"]
    )

    assert (
        actual[0][0].contents["DTEND"]
        == calendar.contents["vevent"][-1].contents["dtend"]
    )

    assert (
        actual[0][1].contents["uid"]
        == updated_calendar.contents["vevent"][-1].contents["uid"]
    )

    assert (
        actual[0][1].contents["DTSTART"]
        == updated_calendar.contents["vevent"][-1].contents["dtstart"]
    )

    assert (
        actual[0][1].contents["DTEND"]
        == updated_calendar.contents["vevent"][-1].contents["dtend"]
    )
