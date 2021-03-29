import sys
from argparse import ArgumentParser
from typing import Mapping, Sequence

import yaml

from fifty_cal.exceptions import ArgumentConflictException


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
        """"""
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

        run_methods.get(mode)()

    def load_config(self, config_path: str):
        """
        Load the YAML configuration file and store the contents in the relevant
        instance variables.
        """
        with open(config_path) as config:
            self.calendar_ids = yaml.full_load(config)[0]


    def download(self):
        """
        Run the command in Download mode.
        """

    def publish(self):
        """
        Run the command in Publish mode.
        """


if __name__ == "__main__":
    Command(sys.argv[1:])