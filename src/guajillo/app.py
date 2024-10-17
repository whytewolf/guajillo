"""
Main app for cli program
"""

import argparse
import json
import logging
import sys
import tomllib
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

from guajillo.conn import Guajillo

FORMAT = "%(message)s"
log = logging.getLogger(__name__)

console = Console()


class App:
    def __init__(self) -> None:
        self.console = console
        """
        FIX: This should not be a part of init. make a setup class. pass results into init
        """
        self._build_args()
        self._load_config()
        self._validate_config()
        self._setup_logging()
        self._load_client()

    def _build_args(self) -> None:
        """
        Build the args for the cli command

        TODO: This will become its own class at some point.
        """

        parser = argparse.ArgumentParser(
            prog="guajillo",
            description="Salt-api CLI access",
            epilog="Copyright 2024 Thomas Phipps",
        )
        parser.add_argument(
            "-C", "--config", dest="config", help="Config file location."
        )
        parser.add_argument(
            "-p",
            dest="profile",
            default="netapi",
            help="profile from config to use for connection",
        )
        parser.add_argument(
            "-o",
            "--out",
            dest="output",
            help="Output method will auto detect if possable, use this to force or set to json for json output",
        )
        parser.add_argument(
            "--out-list", help="list known output methods", action="store_true"
        )
        parser.add_argument("--output-file", dest="output_file", help="Output File")
        parser.add_argument(
            "-L",
            "--log",
            dest="log_level",
            choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
            help="logging level",
        )
        self.parsed_args, self.salt_args = parser.parse_known_args()
        console.print(self.parsed_args)
        console.print(self.salt_args)

    def _load_config(self) -> None:
        """
        load the config file from either the location given by the user,
        or load from default path in .config
        """
        if self.parsed_args.config is not None:
            self.config_path = Path(self.parsed_args.config)
        else:
            self.config_path = Path("~/.config/guajillo/config.toml")
        path = self.config_path.expanduser()
        if not path.exists():
            log.error(f"File: {path} does not exist")
            sys.exit(1)

        if not path.is_file():
            log.error(f"File: {path} is not a file")
            sys.exit(1)

        with open(path, "rb") as fd:
            try:
                self.config = tomllib.load(fd)
            except Exception as err:
                log.error(err)

    def _setup_logging(self) -> None:
        """
        Setup logging
        TODO: really? stop being lazy this needs its own thing and a lot more smarts
        """

        logging.basicConfig(
            level=self.config["logging"]["log_level"],
            format=FORMAT,
            datefmt="[%X]",
            handlers=[RichHandler(markup=True)],
        )
        log.info("Rich logging loaded")

    def _validate_config(self) -> None:
        """
        TODO: move this into the config class when a config class exists.
        """
        defaults = {
            "logging": {"log_level": "WARNING"},
        }
        defaults.update(self.config)
        if self.parsed_args.log_level is not None:
            defaults.update({"logging": {"log_level": self.parsed_args.log_level}})
        self.config = defaults

    def _load_client(self):
        self.client = Guajillo(self.config["netapi"]["url"])

    async def run(self):
        """
        Run the bloody thing
        """
        username = self.config["netapi"]["username"]
        password = self.config["netapi"]["password"]
        auth = self.config["netapi"]["auth"]
        login_info = await self.client.login(username, password, auth)
        self.console.print_json(json.dumps(login_info["return"][0]))
