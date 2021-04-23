import datetime as dt
import random
import string
from typing import Mapping

import pytest
from vobject import readOne
from vobject.base import Component, newFromBehavior

from fifty_cal.diff import CalendarDiff
from fifty_cal.merge import merge


@pytest.fixture
def local_cal() -> Component:
    """
    Read in test local calendar file and load into `vobject.Component` object.
    """
    with open("fifty_cal/tests/resources/dummy_local.ics", "r") as cal_file:
        cal = readOne(cal_file.read())
    return cal


@pytest.fixture
def update_calendar():
    """
    Create and return a function that updates a passed in calendar.
    """

    def _(calendar: Component, event_index: int, modifications: Mapping) -> Component:
        """
        Duplicate calendar, modify an event, and return the given calendar.

        Modifications passed in as kwargs.
        """
        modified = Component.duplicate(calendar)

        event = modified.contents["vevent"][event_index]

        for attribute, value in modifications.items():
            setattr(event, f"{attribute}.value", value)

        return modified

    return _


@pytest.fixture
def create_event():
    """
    Create and return an event factory.
    """

    def _(attributes: Mapping) -> Component:
        """
        Create and return a `vevent`.
        """
        event = newFromBehavior("vevent")

        event.add("uid").value = "".join(
            random.choice(string.ascii_lowercase) for i in range(32)
        )

        for attrib, value in attributes.items():
            event.add(attrib).value = value

        return event

    return _


def test_new_event_in_both_calendars(local_cal: Component, create_event: callable):
    """
    Both calendars have a new event that the other doesn't.

    Ensure that the merged calendar contains both of the new events as well as all
    shared events.
    """

    cal_1 = Component.duplicate(local_cal)
    cal_1_new_event = create_event({"SUMMARY": "Calendar 1 new event."})
    cal_1.add(cal_1_new_event)

    cal_2 = Component.duplicate(local_cal)
    cal_2_new_event = create_event({"SUMMARY": "Calendar 2 new event."})
    cal_2.add(cal_2_new_event)

    diff = CalendarDiff(cal_1, cal_2)

    merged_cal = merge(diff)

    assert merged_cal.contents["vevent"][-1].contents == cal_1_new_event.contents
    assert merged_cal.contents["vevent"][-2].contents == cal_2_new_event.contents


def test_latest_in_output(local_cal: Component, update_calendar: callable):
    """
    When both calendars have different copies of an event, the latest is in the output.

    If one calendar contains an event that has been updated, the version that was
    updated the most recently should be in the output calendar.
    """
    # Change the last entered event.
    event_index = -1

    # Move the event forward by one hour.
    event_time_delta = dt.timedelta(hours=1)

    modifications = {
        "DTSTART": local_cal.contents["vevent"][-1].dtstart.value + event_time_delta,
        "DTEND": local_cal.contents["vevent"][-1].dtend.value + event_time_delta,
        "SUMMARY": "Updated Test",
        "LAST-MODIFIED": [dt.datetime.now(tz=dt.timezone.utc)],
    }

    # Update the calendar
    updated_cal = update_calendar(local_cal, event_index, modifications)

    diff = CalendarDiff(local_cal, updated_cal)

    merged = merge(diff)

    # Ensure that the length of the original calendar is the same as the merged one.
    assert len(merged.contents["vevent"]) == len(local_cal.contents["vevent"])

    # Ensure that there is only one entry for the uid of the modified event.
    uid = updated_cal.contents["vevent"][-1].uid.value
    uid_occurrences = sum(
        [1 for event in merged.contents["vevent"] if event.uid.value == uid]
    )
    assert uid_occurrences == 1

    # Ensure that the values for the updated event are the latest.
    merged_event = merged.contents["vevent"][-1]
    updated_event = updated_cal.contents["vevent"][-1]

    assert merged_event.dtstart.value == updated_event.dtstart.value
    assert merged_event.dtend.value == updated_event.dtend.value
    assert merged_event.summary.value == updated_event.summary.value
    assert merged_event.last_modified.value == updated_event.last_modified.value


def test_new_and_updated_events_merged_correctly(
    local_cal: Component, update_calendar: callable, create_event: callable
):
    """
    Ensure that output is still as expected when the above two cases are both true.
    """
    event_time_delta = dt.timedelta(hours=1)

    modifications = {
        "DTSTART": local_cal.contents["vevent"][-1].dtstart.value + event_time_delta,
        "DTEND": local_cal.contents["vevent"][-1].dtend.value + event_time_delta,
        "SUMMARY": "Updated Test",
        "LAST-MODIFIED": [dt.datetime.now(tz=dt.timezone.utc)],
    }

    updated_calendar = update_calendar(local_cal, -1, modifications)

    new_event = create_event({"Summary": "New event"})

    local_cal.add(new_event)

    diff = CalendarDiff(local_cal, updated_calendar)

    merged = merge(diff)

    # Ensure that the merged calendar has an extra event when compared with the modified
    # calendar.
    assert (
        len(merged.contents["vevent"]) == len(updated_calendar.contents["vevent"]) + 1
    )

    # Ensure that the updated event in merged is the latest version.
    # Ensure that the values for the updated event are the latest.
    merged_event = merged.contents["vevent"][-2]
    updated_event = updated_calendar.contents["vevent"][-1]

    assert merged_event.dtstart.value == updated_event.dtstart.value
    assert merged_event.dtend.value == updated_event.dtend.value
    assert merged_event.summary.value == updated_event.summary.value
    assert merged_event.last_modified.value == updated_event.last_modified.value

    # Lastly ensure that the new event is present in the merged calendar.
    assert (
        merged.contents["vevent"][-1].contents
        == local_cal.contents["vevent"][-1].contents
    )
