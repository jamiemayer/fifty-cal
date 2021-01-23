from typing import Mapping

import pytest
from vobject import readOne
from vobject.base import Component


@pytest.fixture
def local_cal() -> Component:
    """
    Read in test local calendar file and load into `vobject.Component` object.
    """
    with open("fifty_cal/tests/resources/dummy_local.ics", 'r') as cal_file:
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
            modified.contents['vevent'][event_index][attribute].value = value

        return modified
    return _


def test_new_event_in_both_calendars(local_cal):
    """
    Both calendars have a new event that the other doesn't.

    Ensure that the merged calendar contains both of the new events as well as all
    shared events.
    """
