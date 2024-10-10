import argparse
from pathlib import Path
import tomllib
from rich import print


class App:
    def __init__(self) -> None:
        self._build_args()
        self._load_config()

    def _build_args(self) -> None:
        """
        Build the args for the cli command
        """
        parser = argparse.ArgumentParser(
            prog="guajillo",
            description="Salt-api CLI access",
            epilog="Copyright 2024 Thomas Phipps",
        )
        parser.add_argument("-C", "--config")
        self.parsed_args = parser.parse_args()
        print(self.parsed_args)

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
        print(path)
        with open(path, "rb") as fd:
            try:
                self.config = tomllib.load(fd)
            except Exception as err:
                print(err)

    async def run(self):
        pass
