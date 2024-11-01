import re
from argparse import ArgumentError

import pytest

from guajillo.utils.cli import CliParse


def test_cli_config():
    testing = CliParse()
    testing.build_args(["-c", "/fake/file"])
    assert testing.parsed_args.config == "/fake/file"


def test_cli_config_fail():
    testing = CliParse()
    with pytest.raises(
        ArgumentError, match=re.escape("argument -c/--config: expected one argument")
    ):
        testing.build_args(["-c"])


def test_cli_profile():
    testing = CliParse()
    testing.build_args(["-p", "netapi"])
    assert testing.parsed_args.profile == "netapi"


def test_cli_profile_fail():
    testing = CliParse()
    with pytest.raises(
        ArgumentError, match=re.escape("argument -p/--profile: expected one argument")
    ):
        testing.build_args(["-p"])


def test_cli_out():
    testing = CliParse()
    testing.build_args(["-o", "json"])
    assert testing.parsed_args.output == "json"


def test_cli_out_fail():
    testing = CliParse()
    with pytest.raises(
        ArgumentError, match=re.escape("argument -o/--out: expected one argument")
    ):
        testing.build_args(["-o"])


def test_cli_out_list():
    testing = CliParse()
    testing.build_args(["--out-list"])
    assert testing.parsed_args.out_list


def test_cli_out_list_default():
    testing = CliParse()
    testing.build_args(["-c", "/fake/file"])
    assert not testing.parsed_args.out_list


def test_cli_output_file():
    testing = CliParse()
    testing.build_args(["--output-file", "/fake/file"])
    assert testing.parsed_args.output_file == "/fake/file"


def test_cli_output_file_fail():
    testing = CliParse()
    with pytest.raises(
        ArgumentError, match=re.escape("argument --output-file: expected one argument")
    ):
        testing.build_args(["--output-file"])


def test_cli_log():
    testing = CliParse()
    testing.build_args(["-L", "DEBUG"])
    assert testing.parsed_args.log_level == "DEBUG"


def test_cli_log_fail():
    testing = CliParse()
    with pytest.raises(
        ArgumentError,
        match=re.escape(
            "argument -L/--log: invalid choice: 'ALL' (choose from 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG')"
        ),
    ):
        testing.build_args(["-L", "ALL"])
