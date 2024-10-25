import argparse


class CliParse:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            prog="guajillo",
            description="a program for interacting with salt from any terminal window",
            epilog="Copyright 2024 Thomas Phipps",
        )

    def build_args(self) -> None:
        """
        Build the args for the cli command

        TODO: This will become its own class at some point.
        """

        self.parser.add_argument(
            "-c", "--config", dest="config", help="Config file location."
        )
        self.parser.add_argument(
            "-p",
            dest="profile",
            default="netapi",
            help="profile from config to use for connection",
        )
        self.parser.add_argument(
            "-o",
            "--out",
            dest="output",
            help="Output method will auto detect if possable, use this to force or set to json for json output",
        )
        self.parser.add_argument(
            "--out-list", help="list known output methods", action="store_true"
        )
        self.parser.add_argument(
            "--output-file", dest="output_file", help="Output File"
        )
        self.parser.add_argument(
            "-L",
            "--log",
            dest="log_level",
            choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
            help="logging level",
        )
        self.parsed_args, self.salt_args = self.parser.parse_known_args()
