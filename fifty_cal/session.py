import logging
from contextlib import contextmanager
from time import sleep
from typing import Mapping

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

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
        self.driver = webdriver.Firefox(options=options)
        self.driver.service.log_file = None
        self.wait = WebDriverWait(self.driver, 60)

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

        username_field = self.driver.find_element_by_id("rcmloginuser")
        password_field = self.driver.find_element_by_id("rcmloginpwd")
        login_button = self.driver.find_element_by_id("rcmloginsubmit")


        actions = ActionChains(self.driver)
        actions.send_keys_to_element(username_field, username)
        actions.send_keys_to_element(password_field, password)
        actions.click(login_button)
        actions.perform()

        cookies = self.driver.get_cookies()
        self.logged_in = True
        self.wait.until(
            expected_conditions.presence_of_element_located(
                (By.ID, "rcmbtn110")
            )
        )
        calendar_button = self.driver.find_element_by_id("rcmbtn110")
        # For some reason we have to click twice.
        actions.click(calendar_button)
        actions.click(calendar_button)
        actions.perform()



        self.get_calendar_map()
        yield {cookie["name"]: cookie["value"] for cookie in cookies}
        log.debug("Session exited. Logging out.")
        self.logout()
        self.driver.quit()

    def get_calendar_map(self):
        """
        Get a mapping of calendar name to the calendar ID.
        """
        self.wait.until(
            expected_conditions.presence_of_element_located(
                (By.ID, "calendarslist")
            )
        )

        cal_map = {}

        calendar_list = self.driver.find_element(By.ID, "calendarslist")
        calendars = calendar_list.find_elements(By.TAG_NAME, "li")
        for calendar in calendars:
            cal_attributes = calendar.find_element(By.CLASS_NAME, 'calname')
            cal_map[cal_attributes.text] = cal_attributes.get_attribute('id')[3:]

        return cal_map


    def logout(self):
        """
        Log out of the current session.

        Sometimes the session can exit before the page has had a chance to load,
        causing a `NoSuchElementException` to be raised. If this happens,
        wait 5 seconds for the page to load and try again up to a maximum of 2 minutes.

        # TODO: Change this to use the `wait_until` method.
        """
        elapsed_seconds = 0
        while self.logged_in and elapsed_seconds <= self.LOGOUT_RETRY_MAX_SECONDS:
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
