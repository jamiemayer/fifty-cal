import logging
import sys
from argparse import ArgumentParser
from typing import Mapping, Sequence

import yaml

from fifty_cal import downloader
from fifty_cal.exceptions import ArgumentConflictException, ConfigurationException
from fifty_cal.session import Session

log = logging.getLogger(__name__)


class Command:
    """
    Main entry point.

    Takes one positional argument:
        * config_path
            - The full path to the configuration file. Currently only supports YAML
              files.

    Can be run in two modes:
        * Fetch mode
            - Will fetch the calendars specified in the configuration file. This is
              the default mode and will be used if no flag is published. The command
              can take a `--download` argument if explicitness is required in things
              like crontab etc.
        * Publish
            - Uploads the calendars specified in the configuration file to the NamesCo
              server. Use the `--publish` optional arg to run in Publish mode.
    """

    calendar_ids: Mapping[str, str]

    def __init__(self, command_args: Sequence[str]):
        """
        Entry point into the command.

        # TODO: Break this out into a smaller __init__ and a handle method.
        """
        self.session: Session = Session()
        self.username: str = ""
        self.password: str = ""
        self.output_path: str = ""
        run_methods = {"download": self.download, "publish": self.publish}

        parser = ArgumentParser()

        parser.add_argument(
            "config_path", help="The path to the config file.", type=str
        )

        parser.add_argument(
            "--download",
            help="Run in Download mode. Not required but exists when explicitness is "
            "required.",
            action="store_true",
        )
        parser.add_argument(
            "--publish",
            help="Run in Publish mode.",
            action="store_true",
        )

        args = parser.parse_args(command_args)

        if args.download and args.publish:
            raise ArgumentConflictException(
                "Both download and publish options specified. Pick one or the other."
            )

        self.load_config(config_path=args.config_path)

        mode = "publish" if args.publish else "download"
        with self.session.start_session(self.username, self.password) as cookies:
            run_methods.get(mode)(cookies)

    def load_config(self, config_path: str):
        """
        Load the YAML configuration file and store the contents in the relevant
        instance variables.
        """
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file)
        try:
            self.username = config["username"]
        except KeyError:
            raise ConfigurationException("No username provided in config file.")
        try:
            self.password = config["password"]
        except KeyError:
            raise ConfigurationException("No password provided in config file.")
        try:
            self.output_path = config["output_path"]
        except KeyError:
            raise ConfigurationException("No output path provided.")
        try:
            self.calendar_ids = config["cal_ids"]
        except KeyError:
            log.warning("No calendar IDs provided in config.")

    def download(self, cookies: Mapping[str, str]):
        """
        Run the command in Download mode.
        """
        requests_session = downloader.get_requests_session(cookies)
        for person, cal_id in self.calendar_ids.items():
            downloader.get_calendar(cal_id, requests_session)

    def publish(self, cookies: Mapping[str, str]):
        """
        Run the command in Publish mode.
        """

    def save_calendar(self):
        """
        Save the downloaded calendar to disk
        """


if __name__ == "__main__":
    Command(sys.argv[1:])
