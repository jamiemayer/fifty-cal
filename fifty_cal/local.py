from vobject.base import Component, readOne


def get_local_calendar(file_path: str) -> Component:
    """
    Read and parse a local calendar file, returning a vobject Component object.
    """
    with open(file_path) as calendar_file:
        local_calendar = calendar_file.read()

    return readOne(local_calendar)
