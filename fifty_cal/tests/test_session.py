import pytest
from selenium.common.exceptions import NoSuchElementException

from fifty_cal.exceptions import UnableToLogoutException
from fifty_cal.session import Session


@pytest.fixture
def setup_mocks(mocker):
    """
    Mock the selenium object methods for testing.
    """
    mocker.patch("fifty_cal.session.webdriver.Firefox.get")
    mocker.patch("fifty_cal.session.webdriver.Firefox.find_element_by_id")
    mocker.patch("fifty_cal.session.webdriver.Firefox.find_element_by_class_name")
    mocker.patch(
        "fifty_cal.session.webdriver.Firefox.get_cookies",
        return_value=[{"name": "test", "value": "test"}],
    )
    yield


@pytest.fixture
def session(setup_mocks):
    return Session()


def test_start_session_gets_session_cookies(session):
    """
    Test the start_session context manager yields cookies.
    """
    with session.start_session(username="", password="") as cookies:
        assert cookies == {"test": "test"}


def test_start_session_logs_out_when_exiting(session):
    """
    Ensure the start_session context manager logs out on exit.
    """
    with session.start_session(username="", password=""):
        assert session.logged_in
    assert not session.logged_in


def test_exception_raised_if_unable_to_logout(session, mocker):
    """
    Test that `UnableToLogoutException` is raised if logout button does not appear.
    """
    mocker.patch(
        "fifty_cal.session.webdriver.Firefox.find_element_by_class_name",
        side_effect=NoSuchElementException,
    )
    session.LOGOUT_RETRY_MAX_SECONDS = 1
    with pytest.raises(UnableToLogoutException):
        with session.start_session(username="", password=""):
            pass
