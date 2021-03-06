import os
from tempfile import NamedTemporaryFile

import pytest


@pytest.fixture(autouse=True)
def mock_session(mocker):
    """
    Mock out the fifty_cal.Session object imported in the run.py module
    """
    return mocker.patch("run.Session")


@pytest.fixture(autouse=True)
def mock_publish(mocker):
    """
    Mock the publish method of Command.
    """
    return mocker.patch("run.Command.publish")


@pytest.fixture(autouse=True)
def mock_get_requests_session(mocker):
    """
    Mock the requests.Session class.
    """
    return mocker.patch("fifty_cal.downloader.get_requests_session")


@pytest.fixture()
def mock_save(mocker):
    """
    Mock out the fifty_cal.Session object imported in the run.py module
    """
    return mocker.patch("run.Command.save_calendar")


@pytest.fixture()
def mock_update_local(mocker):
    """
    Mock out the fifty_cal.Session object imported in the run.py module
    """
    return mocker.patch("run.Command.update_local")


@pytest.fixture()
def mock_download(mocker):
    """
    Mock the download method of Command.
    """
    return mocker.patch("run.Command.download")


@pytest.fixture()
def mock_get_calendar(mocker):
    """
    Mock the fifty_cal.downloader.get_calendar function.
    """
    return mocker.patch("run.downloader.get_calendar")


@pytest.fixture()
def standard_config():
    """
    Create a temporary YAML config file in memory and yield it.

    Delete upon exiting.
    """
    with NamedTemporaryFile(mode="w+", suffix=".yaml", delete=False) as config:
        config.writelines("username: test_user\n")
        config.writelines("password: allYourBase\n")
        config.writelines("output_path: path/to/cals/\n")
        config.write("cal_ids:\n")
        config.write("  person_1: AB1234\n")
        config.write("  person_2: AB4321\n")
        config.writelines("calendar_url: https://example.com/\n")
    yield config
    os.remove(config.name)


@pytest.fixture()
def config_factory():
    """
    Factory for creating temp config files.
    """
    config_path = ""

    def factory(
            username="test_user",
            output_path="/path/",
            cal_ids=["person_1: AB1234"],
            calendar_url="https:example.com",
    ):
        """
        Create and yield a temporary config file and then remove.
        """
        nonlocal config_path
        with NamedTemporaryFile(mode="w+", suffix=".yaml", delete=False) as config:
            config.write(f"username: {username}\n")
            config.write("password: allYourBase\n")
            config.write(f"output_path: {output_path}\n")
            config.write("cal_ids:\n")
            for cal_id in cal_ids:
                config.write(f"  {cal_id}\n")
            config.write(f"calendar_url: {calendar_url}\n")
        config_path = config.name
        return config

    yield factory
    os.remove(config_path)

