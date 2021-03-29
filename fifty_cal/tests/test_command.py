import os
from tempfile import NamedTemporaryFile

import pytest

from fifty_cal.run import Command


@pytest.fixture
def mock_download(mocker):
    """
    Mock the download method of Command.
    """
    return mocker.patch("fifty_cal.run.Command.download")


@pytest.fixture
def mock_publish(mocker):
    """
    Mock the publish method of Command.
    """
    return mocker.patch("fifty_cal.run.Command.publish")


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

    Command(["", '--download'])

    download.assert_called_once()


def test_runs_in_publish_mode_when_download_option_provided(mocker, mock_publish):
    """
    Runs in Download mode when `--download` option is provided.
    """
    mocker.patch("fifty_cal.run.Command.load_config")
    publish = mock_publish

    Command(["", '--publish'])

    publish.assert_called_once()


def test_load_config(mocker):
    """
    YAML Config loaded and contents stored in relevant instance variable.
    """
    with NamedTemporaryFile(mode='w+', suffix=".yaml", delete=False) as config:
        config.write("- cal_ids:\n")
        config.write("  - Jamie\n")
        config.write("    JM1234\n")

    command = Command([config.name])

    os.remove(config.name)

    assert command.calendar_ids == {'cal_ids': ['Jamie JM1234']}
