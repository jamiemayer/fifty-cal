import pytest
from selenium.common.exceptions import NoSuchElementException

from fifty_cal.exceptions import UnableToLogoutException
from fifty_cal.session import Session


@pytest.fixture
def setup_mocks(mocker):
    """
    Mock the selenium object methods for testing.
    """
    webdriver = mocker.patch("fifty_cal.session.webdriver")
    firefox = mocker.MagicMock()

    get_cookies = mocker.MagicMock()
    get_cookies.return_value = [{"name": "test", "value": "test"}]

    firefox.get_cookies = get_cookies
    webdriver.Firefox.return_value = firefox

    mocker.patch("fifty_cal.session.ActionChains")
    mocker.patch("fifty_cal.session.Options")
    mocker.patch("fifty_cal.session.expected_conditions")
    mocker.patch("fifty_cal.session.WebDriverWait")
    mocker.patch("fifty_cal.session.By")
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
    click = mocker.MagicMock()
    click.click.side_effect = UnableToLogoutException()

    session.LOGOUT_RETRY_MAX_SECONDS = 1
    session.driver = mocker.MagicMock()
    session.driver.find_element_by_class_name.return_value = click
    with pytest.raises(UnableToLogoutException):
        with session.start_session(username="", password=""):
            pass
