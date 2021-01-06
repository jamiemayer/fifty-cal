import logging
import os
from contextlib import contextmanager
from time import sleep
from typing import Mapping

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options

from fifty_cal.exceptions import UnableToLogoutException


log = logging.getLogger(__name__)


class Session:
    """
    Handle the user session.

    Uses selenium with the Firefox driver in headless mode. This is so that session
    and auth cookies can be retrieved by interacting with the relevant JavaScript on
    the login page that cannot be done using a simple http request.
    """

    LOGOUT_RETRY_MAX_SECONDS: int = 120

    def __init__(self):
        self.logged_in = False

        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options, service_log_path=os.devnull)

    @contextmanager
    def start_session(self, *, username: str, password: str) -> Mapping[str, str]:
        """
        Log in and get session and auth cookies.

        Implemented as a Context Manager which will log in to a namesco email account
        and yield the relevant cookies. Upon exiting scope, the user will be logged
        out of the session.
        """
        log.debug("Browser Started")
        self.driver.get("http://webmail.names.co.uk/")
        log.debug("Logging in.")

        self.driver.find_element_by_id("rcmloginuser").send_keys(username)
        self.driver.find_element_by_id("rcmloginpwd").send_keys(password)
        self.driver.find_element_by_id("rcmloginsubmit").click()

        cookies = self.driver.get_cookies()
        self.logged_in = True
        yield {cookie["name"]: cookie["value"] for cookie in cookies}
        log.debug("Session exited. Logging out.")
        self.logout()
        self.driver.quit()

    def logout(self):
        """
        Log out of the current session.

        Sometimes the session can exit before the page has had a chance to load,
        causing a `NoSuchElementException` to be raised. If this happens,
        wait 5 seconds for the page to load and try again up to a maximum of 2 minutes.
        """
        elapsed_seconds = 0
        while elapsed_seconds <= self.LOGOUT_RETRY_MAX_SECONDS and self.logged_in:
            try:
                self.driver.find_element_by_class_name("button-logout").click()
                self.logged_in = False
            except NoSuchElementException:
                log.exception(
                    "Logout button not loaded on page. Will Retry in 5 seconds."
                )
                sleep(5)
                elapsed_seconds += 5
                log.debug("Retrying.")

        if self.logged_in:
            log.exception("Unable to log out of current session.")
            raise UnableToLogoutException

        log.debug("Successfully logged out.")
