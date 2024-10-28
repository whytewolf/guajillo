"""
Main app for cli program
"""

import asyncio
import logging
import sys
import tomllib
from pathlib import Path
from typing import Any

from rich.logging import RichHandler
from rich.traceback import install

from guajillo.exceptions import TerminateTaskGroup
from guajillo.utils.cli import CliParse
from guajillo.utils.conn import Guajillo
from guajillo.utils.console import console, stderr_console
from guajillo.utils.outputs import Outputs

FORMAT = "%(asctime)s %(name)s %(taskName)s %(message)s"
log = logging.getLogger(__name__)


class App:
    def __init__(self) -> None:
        self.console = console
        self.parsed = CliParse()
        install(show_locals=False)
        """
        FIX: This should not be a part of init. make a setup class. pass results into init
        """

    def setup(self) -> None:
        self.parsed.build_args()
        self._load_config()
        self._validate_config()
        self._setup_logging()
        self._load_taskmans()

    def _load_config(self) -> None:
        """
        load the config file from either the location given by the user,
        or load from default path in .config

        TODO: this needs to be part of a config class.
        """
        if self.parsed.parsed_args.config is not None:
            self.config_path = Path(self.parsed.parsed_args.config)
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
            handlers=[
                RichHandler(
                    console=stderr_console,
                    markup=True,
                    rich_tracebacks=True,
                )
            ],
        )
        log.info("Rich logging loaded")

    def _validate_config(self) -> None:
        """
        TODO: move this into the config class when a config class exists.
        """
        defaults: dict["str", Any] = {
            "logging": {"log_level": "WARNING"},
        }
        debug = False
        defaults.update(self.config)
        if self.parsed.parsed_args.log_level is not None:
            debug = self.parsed.parsed_args.log_level in ["DEBUG"]
            defaults.update(
                {
                    "logging": {"log_level": self.parsed.parsed_args.log_level},
                }
            )
        defaults.update({"debug": debug})
        self.config = defaults

    def _load_taskmans(self):
        self.client = Guajillo(
            self.config["netapi"]["url"], self.parsed, self.config, console=self.console
        )
        self.outputs = Outputs(self.console, parser=self.parsed, config=self.config)

    async def run(self):
        """
        Run the bloody thing
        """
        try:
            async_comms = {
                "lock": asyncio.Lock(),
                "update": asyncio.Event(),
                "cond": asyncio.Condition(),
                "events": [],
            }
            log.debug("starting Tasks, client and output")
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self.client.taskMan(async_comms))
                tg.create_task(self.outputs.taskMan(async_comms))
        except* TerminateTaskGroup:
            pass
