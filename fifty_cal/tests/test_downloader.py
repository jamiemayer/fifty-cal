import pytest

from fifty_cal.downloader import get_calendar, get_requests_session
from fifty_cal.exceptions import (
    HttpErrorException,
    NotFoundException,
    ServerErrorException,
    UnauthorizedException,
)


def test_cookies_set_in_session():
    """
    Test that the returned requests.Session object is returned with cookies.
    """
    cookies = {"session_id": "1234", "session_auth": "6789"}

    session = get_requests_session(cookies=cookies)

    assert session.cookies == cookies


def test_get_called_on_correct_calendar_url(mocker):
    """
    Test that the http GET request is sent to the correct calendar URL.
    """
    mocker.patch("fifty_cal.downloader.CALENDAR_URL", "test_url")
    calendar_hash = "foo"

    session = mocker.MagicMock()
    request = mocker.MagicMock()
    request.status_code = 200
    session.get.return_value = request

    get_calendar(calendar_hash=calendar_hash, session=session)

    assert session.get.call_args[0][0] == "test_urlfoo.ics&_action=feed"


def test_calendar_returned_from_response(mocker):
    """
    Test that the calendar is returned from the http response
    """
    mocker.patch("fifty_cal.downloader.CALENDAR_URL", "test_url")

    session = mocker.MagicMock()
    request = mocker.MagicMock()
    request.status_code = 200
    request.text = "Test Calendar"
    session.get.return_value = request

    calendar = get_calendar(calendar_hash="", session=session)

    assert calendar == "Test Calendar"


@pytest.mark.parametrize(
    "status_code, exception",
    [
        (403, UnauthorizedException),
        (404, NotFoundException),
        (500, ServerErrorException),
        (999, HttpErrorException),
    ],
)
def test_exceptions_thrown_on_non_200_response_codes(mocker, status_code, exception):
    """
    Test that the calendar is returned from the http response
    """
    mocker.patch("fifty_cal.downloader.CALENDAR_URL", "test_url")

    session = mocker.MagicMock()
    request = mocker.MagicMock()
    request.status_code = status_code
    request.text = "Test Calendar"
    session.get.return_value = request

    with pytest.raises(exception):
        get_calendar(calendar_hash="", session=session)
