import argparse
import sys

from rich.console import Console
from rich.table import Table

from guajillo.utils.console import stderr_console


class CliParse:
    def __init__(self, console: Console = stderr_console) -> None:
        self.parser = argparse.ArgumentParser(
            prog="guajillo",
            description="a program for interacting with salt from any terminal window",
            epilog="Copyright 2024 Thomas Phipps",
            add_help=False,
        )
        self.console = console

    def build_args(self, args: list["str"]) -> None:
        """
        Build the args for the cli command

        TODO: This will become its own class at some point.
        """

        self.parser.add_argument(
            "-c", "--config", dest="config", help="Config file location."
        )
        self.parser.add_argument(
            "-p",
            "--profile",
            dest="profile",
            default="netapi",
            help="profile from config to use for connection",
        )
        self.parser.add_argument(
            "-o",
            "--out",
            dest="output",
            choices=["json", "yaml", "boolean", "highstate", "profile"],
            help="Output method will auto detect if possable, use this to force or set to json for json output",
        )
        self.parser.add_argument(
            "--output-file", dest="output_file", help="Output File"
        )
        self.parser.add_argument(
            "-l",
            "--log",
            dest="log_level",
            choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
            help="logging level",
        )
        self.parser.add_argument(
            "-t",
            "--timeout",
            type=int,
            default=30,
            help="timeout for internal operations",
        )
        self.parser.add_argument("-h", "--help", action="store_true")

        self.parsed_args, self.salt_args = self.parser.parse_known_args(args)
        if self.parsed_args.help:
            self.help()

    def help(self, doexit: bool = True):
        """
        display help txt
        """
        self.console.print(
            "[bold]usage[/bold]: guajillo [-h] [-c CONFIG] [-p PROFILE] [-o OUTPUT] [--out-list] [--output-file OUTPUT_FILE] [-L {[bold red]CRITICAL[/bold red],[red]ERROR[/red],[yellow]WARNING[/yellow],[blue]INFO[/blue],[green]DEBUG[/green]}] [SALT commands]"
        )
        self.console.print(
            "\nA CLI program for interacting with the salt-api with better output\n"
        )

        options = Table(title="Options")
        options.add_column("Short")
        options.add_column("Long")
        options.add_column("option name")
        options.add_column("description")
        options.add_column("default")
        options.add_row("-h", "--help", "", "Show this help and exit", "")
        options.add_row(
            "-c",
            "--config",
            "CONFIG",
            "Config file location",
            "~/.config/guajillo/config.toml",
        )
        options.add_row(
            "-p",
            "--profile",
            "PROFILE",
            "Profile from config file to use as login info",
            "netapi",
        )
        options.add_row(
            "-o",
            "--out",
            "{json, yaml, boolean, highstate}",
            "force output style through a known output",
            "auto",
        )
        options.add_row(
            "",
            "--output-file",
            "OUTPUT_FILE",
            "Not implimented, output file to dump output to",
            "",
        )
        options.add_row(
            "-t",
            "--timeout",
            "TIMEOUT",
            "timeout for internal operations, loops to fetch",
            "30",
        )
        options.add_row(
            "-l",
            "--log",
            "{[bold red]CRITICAL[/bold red],[red]ERROR[/red],[yellow]WARNING[/yellow],[blue]INFO[/blue],[green]DEBUG[/green]}",
            "console log level",
            "WARNING",
        )
        self.console.print(options)

        self.console.print("\n[bold]Copyright:copyright: 2024 Thomas Phipps[/bold]\n")
        if doexit:
            sys.exit()
