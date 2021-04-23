from vobject.base import Component

from fifty_cal.diff import CalendarDiff


def merge(diff: CalendarDiff) -> Component:
    """
    Take a diff and rebuild the calendar such that it is up to date.

    Out of sync calendars will be updated with new events and any conflicts resolved by
    taking the latest version of the event.
    """

    if not diff.diff:
        diff.clean_calendars()
        diff.get_diff()

    calendar_1 = diff.cal1
    calendar_2 = diff.cal2
    updated_events = {}

    for event_diff in diff.diff:
        if None in event_diff:
            # `None` in event_diff implies no conflict - just that one calendar has an
            # event that the other doesn't.
            event = event_diff[0] or event_diff[1]
            uid = event.uid.value
            updated_events[uid] = event
            continue
        # `None` not in event_diff implies a conflict.
        uid = event_diff[0].uid.value

        # Get the version that was last modified more recently.
        event_1_last_modified = event_diff[0].contents["LAST-MODIFIED"][0].value
        event_2_last_modified = event_diff[1].contents["LAST-MODIFIED"][0].value

        if event_1_last_modified > event_2_last_modified:
            for event in calendar_1.contents["vevent"]:
                if event.contents["uid"][0].value == uid:
                    updated_events[uid] = event
                    break
            continue

        for event in calendar_2.contents["vevent"]:
            if event.contents["uid"][0].value == uid:
                updated_events[uid] = event
                break
        continue

    updated_cal = Component.duplicate(calendar_2)
    out_of_date_events = []

    for event in updated_cal.contents["vevent"]:
        uid = event.uid.value
        if uid not in updated_events:
            continue
        event = updated_events[uid]
        out_of_date_events.append(event)

    for event in out_of_date_events:
        del event

    for uid, event in updated_events.items():
        updated_cal.add(event)

    return updated_cal
