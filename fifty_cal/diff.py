from vobject.base import Component
from vobject.ics_diff import diff


class CalendarDiff:
    """
    Represents the diff between two calendars
    """

    cal1: Component
    cal2: Component
    cal1_cleaned: Component
    cal2_cleaned: Component
    diff: list

    def __init__(self, cal1: Component, cal2: Component):
        """
        Set the two calendars.
        """
        self.cal1 = cal1
        self.cal2 = cal2

    def clean_calendars(self):
        """
        Remove attributes that the diff function has issues with.

        At the moment this only removes the `sequence` attribute. It appears that
        this attribute is incremented any time the event is amended. However the
        diffing function supplied with `vobject` does not recognise calendar events
        that are identical in every way apart from this `sequence` value.
        """
        cal1_cleaned = Component.duplicate(self.cal1)
        cal2_cleaned = Component.duplicate(self.cal2)
        for calendar in [cal1_cleaned, cal2_cleaned]:
            for event in calendar.contents["vevent"]:
                if hasattr(event, "sequence"):
                    delattr(event, "sequence")

        self.cal1_cleaned = cal1_cleaned
        self.cal2_cleaned = cal2_cleaned

    def get_diff(self):
        """
        Get the diff between cal1 and cal2
        """
        self.diff = diff(self.cal1_cleaned, self.cal2_cleaned)
