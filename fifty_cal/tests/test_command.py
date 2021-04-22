import os
from tempfile import NamedTemporaryFile

import pytest

from fifty_cal.exceptions import ConfigurationException
from fifty_cal.run import Command


@pytest.fixture(autouse=True)
def mock_session(mocker):
    """
    Mock out the fifty_cal.Session object imported in the run.py module
    """
    return mocker.patch("fifty_cal.run.Session")


@pytest.fixture(autouse=True)
def mock_publish(mocker):
    """
    Mock the publish method of Command.
    """
    return mocker.patch("fifty_cal.run.Command.publish")


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
    return mocker.patch("fifty_cal.run.Command.save_calendar")


@pytest.fixture()
def mock_update_local(mocker):
    """
    Mock out the fifty_cal.Session object imported in the run.py module
    """
    return mocker.patch("fifty_cal.run.Command.update_local")


@pytest.fixture()
def mock_download(mocker):
    """
    Mock the download method of Command.
    """
    return mocker.patch("fifty_cal.run.Command.download")


@pytest.fixture()
def mock_get_calendar(mocker):
    """
    Mock the fifty_cal.downloader.get_calendar function.
    """
    return mocker.patch("fifty_cal.run.downloader.get_calendar")


@pytest.fixture()
def standard_config():
    """
    Create a temporary YAML config file in memory and yield it.

    Delete upon exiting.
    """
    with NamedTemporaryFile(mode="w+", suffix=".yaml", delete=False) as config:
        config.writelines("username: test_user\n")
        config.writelines("password: allYourBase\n")
        config.writelines("output_path: /test/\n")
        config.write("cal_ids:\n")
        config.write("  person_1: AB1234\n")
        config.write("  person_2: AB4321\n")
        config.writelines("calendar_url: https://example.com/\n")
    yield config
    os.remove(config.name)


def test_runs_in_download_mode_by_default(mocker, mock_download):
    """
    Runs in Download mode when no optional args are specified.
    """
    mocker.patch("fifty_cal.run.Command.load_config")
    download = mock_download

    Command([""])

    download.assert_called_once()


def test_runs_in_download_mode_when_download_option_provided(mocker, mock_download):
    """
    Runs in Download mode when `--download` option is provided.
    """
    mocker.patch("fifty_cal.run.Command.load_config")
    download = mock_download

    Command(["", "--download"])

    download.assert_called_once()


def test_runs_in_publish_mode_when_download_option_provided(mocker, mock_publish):
    """
    Runs in Download mode when `--download` option is provided.
    """
    mocker.patch("fifty_cal.run.Command.load_config")
    publish = mock_publish

    Command(["", "--publish"])

    publish.assert_called_once()


def test_load_config(standard_config, mock_download):
    """
    YAML Config loaded and contents stored in relevant instance variable.
    """

    command = Command([standard_config.name])

    assert command.username == "test_user"
    assert command.password == "allYourBase"
    assert command.calendar_ids == {"person_1": "AB1234", "person_2": "AB4321"}


@pytest.mark.parametrize(
    "line_to_omit, expected_error_message",
    [
        (0, "No username provided in config file."),
        (1, "No password provided in config file."),
        (2, "No calendar URL provided in config file."),
        (3, "No output path provided."),
    ],
)
def test_invalid_config_raises_errors(line_to_omit, expected_error_message):
    """
    Exception thrown when a required configuration parameter is not provided.
    """
    required_values = [
        "username: test_user",
        "password: allYourBase",
        "calendar_url: https://example.com/",
        "output_path: /test/",
    ]

    config_values = required_values[:line_to_omit] + required_values[line_to_omit + 1 :]

    with NamedTemporaryFile(mode="w+", suffix=".yaml", delete=False) as config:
        config.writelines("\n".join(config_values) + "\n")
        config.write("cal_ids:\n")
        config.write("  person_1: AB1234\n")
        config.write("  person_2: AB4321\n")

    with pytest.raises(ConfigurationException) as e:
        Command([config.name])
        assert e.value.args[0] == expected_error_message


def test_get_calendar_called_with_calendar_ids(
    standard_config, mocker, mock_save, mock_get_calendar
):
    """
    Management Command makes a call to downloader.get_calendar with expected args.
    """
    request_session = mocker.MagicMock()

    mocker.patch(
        "fifty_cal.downloader.get_requests_session", return_value=request_session
    )

    Command([standard_config.name])

    assert mock_get_calendar.call_count == 2
    assert mock_get_calendar.call_args_list[0][0] == ("AB1234", request_session)
    assert mock_get_calendar.call_args_list[1][0] == ("AB4321", request_session)


def test_update_local_not_called_when_new_calendar_downloaded(
    mocker, mock_save, mock_update_local, mock_get_calendar, standard_config
):
    """
    Nothing updated when a downloaded calendar doesn't exist locally.
    """
    Command([standard_config.name])

    assert mock_update_local.call_count == 0