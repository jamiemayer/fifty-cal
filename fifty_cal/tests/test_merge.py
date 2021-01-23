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

        for attribute, value in modifications.items():
            modified.contents["vevent"][event_index][attribute].value = value

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


def test_new_event_in_both_calendars(local_cal: Component, create_event):
    """
    Both calendars have a new event that the other doesn't.

    Ensure that the merged calendar contains both of the new events as well as all
    shared events.
    """

    cal_1 = Component.duplicate(local_cal)
    cal_1_new_event = create_event({'SUMMARY': 'Calendar 1 new event.'})
    cal_1.add(cal_1_new_event)

    cal_2 = Component.duplicate(local_cal)
    cal_2_new_event = create_event({'SUMMARY': 'Calendar 2 new event.'})
    cal_2.add(cal_2_new_event)

    diff = CalendarDiff(cal_1, cal_2)

    merged_cal = merge(diff)

    assert merged_cal.contents['vevent'][-1].contents == cal_1_new_event.contents
    assert merged_cal.contents['vevent'][-2].contents == cal_2_new_event.contents


