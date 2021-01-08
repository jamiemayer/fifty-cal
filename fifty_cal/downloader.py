import logging
from typing import Mapping

from requests import Session

from fifty_cal.exceptions import (
    HttpErrorException,
    NotFoundException,
    ServerErrorException,
    UnauthorizedException,
)

# TODO move this to config maybe?
CALENDAR_URL = "https://webmail.names.co.uk/?_task=calendar&_cal="

ERROR_RESPONSE_CODES = {
    403: UnauthorizedException,
    404: NotFoundException,
    500: ServerErrorException,
}


log = logging.getLogger(__name__)


def get_requests_session(cookies: Mapping[str, str]) -> Session:
    """
    Create and return a `requests.Session` object.

    Expects session and auth cookies to be passed in.
    """
    session = Session()

    session.cookies.update(cookies)

    return session


def get_calendar(calendar_hash: str, session: Session) -> str:
    """
    Get the most recent version of the calendar.
    """

    url = f"{CALENDAR_URL}{calendar_hash}.ics&_action=feed"

    calendar_request = session.get(url)

    response_code = calendar_request.status_code

    if response_code != 200:
        log.exception(
            f"Request Failed {calendar_request.status_code}: {calendar_request.reason}"
        )
        raise ERROR_RESPONSE_CODES.get(response_code, HttpErrorException)
    else:
        return calendar_request.text
