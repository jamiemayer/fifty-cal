import os
from tempfile import NamedTemporaryFile

import pytest

from fifty_cal.exceptions import ConfigurationException
from run import Command


def test_runs_in_download_mode_by_default(mocker, mock_download):
    """
    Runs in Download mode when no optional args are specified.
    """
    mocker.patch("run.Command.load_config")
    download = mock_download

    Command([""])

    download.assert_called_once()


def test_runs_in_download_mode_when_download_option_provided(mocker, mock_download):
    """
    Runs in Download mode when `--download` option is provided.
    """
    mocker.patch("run.Command.load_config")
    download = mock_download

    Command(["", "--download"])

    download.assert_called_once()


def test_runs_in_publish_mode_when_download_option_provided(mocker, mock_publish):
    """
    Runs in Download mode when `--download` option is provided.
    """
    mocker.patch("run.Command.load_config")
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
    assert mock_get_calendar.call_args_list[0][0] == (
        "AB1234",
        request_session,
        "https://example.com/",
    )
    assert mock_get_calendar.call_args_list[1][0] == (
        "AB4321",
        request_session,
        "https://example.com/",
    )


def test_update_local_not_called_when_new_calendar_downloaded(
    mock_save, mock_update_local, mock_get_calendar, standard_config
):
    """
    Nothing updated when a downloaded calendar doesn't exist locally.
    """
    Command([standard_config.name])

    assert mock_update_local.call_count == 0


def test_update_local_called_when_downloaded_calendar_already_exists(
    mock_save, mock_update_local, mock_get_calendar, mocker
):
    """
    When an update to an existing calendar is downloaded, the two should be merged.
    """
    downloaded_calendar_mock = mocker.MagicMock()
    mock_get_calendar.return_value = downloaded_calendar_mock

    with NamedTemporaryFile(mode="w+", suffix=".ics", delete=False) as calendar_file:
        calendar_file.write("placeholder")
    mock_cal_file_path = calendar_file.name

    with NamedTemporaryFile(mode="w+", suffix=".yaml", delete=False) as config:
        config.writelines("username: test_user\n")
        config.writelines("password: allYourBase\n")
        config.writelines("output_path: /tmp/\n")
        config.write("cal_ids:\n")
        config.write(f"  {mock_cal_file_path.split('/')[-1].split('.')[0]}: AB1234\n")
        config.writelines("calendar_url: https://example.com/\n")

    Command([config.name])

    os.remove(config.name)
    os.remove(calendar_file.name)

    assert mock_update_local.call_args_list[0][0] == (
        downloaded_calendar_mock,
        f"{mock_cal_file_path}",
    )


def test_full_download_process(
    config_factory, mock_get_calendar, mock_update_local, mock_save
):
    """
    Test the entire download process from running the command and saving the file.
    """

    with open("fifty_cal/tests/resources/dummy_local.ics", "r") as local_calendar:
        with NamedTemporaryFile(mode="w+", suffix=".ics", delete=False) as temp_local:
            for line in local_calendar.read():
                temp_local.write(line)
    mock_local_cal_path = temp_local.name

    config = config_factory(
        output_path="/tmp/",
        cal_ids=[f"{mock_local_cal_path.split('/')[-1].split('.')[0]}: "],
    )

    Command([config.name])

    mock_get_calendar.assert_called_once()
    mock_update_local.assert_called_once()
    mock_save.assert_called_once()
