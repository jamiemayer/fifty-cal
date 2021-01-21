from typing import List, Optional

from vobject.base import Component
from vobject import ics_diff


def clean_calendar(calendar: Component):
    """
    Remove fields from calendar that trip up the diff function.

    The `diff` function bundled with the `vobject` library seems to trip when some
    fields aren't identical between the two calendars. Annoyingly `sequence` (which
    essentially means revision number - incremented when an event is edited) is one
    of these.
    """
    for event in calendar.contents["vevent"]:
        if hasattr(event, "sequence"):
            delattr(event, "sequence")


def get_diff(first: Component, second: Component) -> Optional[List[Component]]:
    """
    Get the difference between local and downloaded calendar files.
    """

    clean_calendar(first)
    clean_calendar(second)

    return ics_diff.diff(first, second)
