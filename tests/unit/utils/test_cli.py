import pytest
from rich.console import Console

from guajillo.utils.cli import CliParse


def test_cli_config():
    testing = CliParse()
    testing.build_args(["-c", "/fake/file"])
    assert testing.parsed_args.config == "/fake/file"


def test_cli_config_fail():
    testing = CliParse()
    with pytest.raises(SystemExit) as excinfo:
        testing.build_args(["-c"])
    assert excinfo.value.code == 2


def test_cli_profile():
    testing = CliParse()
    testing.build_args(["-p", "netapi"])
    assert testing.parsed_args.profile == "netapi"


def test_cli_profile_fail():
    testing = CliParse()
    with pytest.raises(SystemExit) as excinfo:
        testing.build_args(["-p"])
    assert excinfo.value.code == 2


def test_cli_out():
    testing = CliParse()
    testing.build_args(["-o", "json"])
    assert testing.parsed_args.output == "json"


def test_cli_out_fail():
    testing = CliParse()
    with pytest.raises(SystemExit) as excinfo:
        testing.build_args(["-o"])
    assert excinfo.value.code == 2


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
    with pytest.raises(SystemExit) as excinfo:
        testing.build_args(["--output-file"])
    assert excinfo.value.code == 2


def test_cli_log():
    testing = CliParse()
    testing.build_args(["-L", "DEBUG"])
    assert testing.parsed_args.log_level == "DEBUG"


def test_cli_log_fail():
    testing = CliParse()
    with pytest.raises(SystemExit) as excinfo:
        testing.build_args(["-L", "ALL"])
    assert excinfo.value.code == 2


def test_help():
    output = Console()
    with output.capture() as capture:
        testing = CliParse(output)
        testing.help(doexit=False)
    expected = "usage: guajillo [-h] [-c CONFIG] [-p PROFILE] [-o OUTPUT] [--out-list] \n[--output-file OUTPUT_FILE] [-L {CRITICAL,ERROR,WARNING,INFO,DEBUG}] [SALT \ncommands]\n\nA CLI program for interacting with the salt-api with better output\n\n                                    Options                                     \n┏━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓\n┃ Short ┃ Long          ┃ option name     ┃ description      ┃ default         ┃\n┡━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩\n│ -h    │ --help        │                 │ Show this help   │                 │\n│       │               │                 │ and exit         │                 │\n│ -c    │ --config      │ CONFIG          │ Config file      │ ~/.config/guaj… │\n│       │               │                 │ location         │                 │\n│ -p    │ --profile     │ PROFILE         │ Profile from     │ netapi          │\n│       │               │                 │ config file to   │                 │\n│       │               │                 │ use as login     │                 │\n│       │               │                 │ info             │                 │\n│ -o    │ --out         │ OUTPUT          │ currently not    │ auto            │\n│       │               │                 │ used, but will   │                 │\n│       │               │                 │ let uses force   │                 │\n│       │               │                 │ output style     │                 │\n│       │ --out-list    │                 │ list known       │                 │\n│       │               │                 │ output types,    │                 │\n│       │               │                 │ currently not    │                 │\n│       │               │                 │ implimented      │                 │\n│       │ --output-file │ OUTPUT_FILE     │ Not implimented, │                 │\n│       │               │                 │ output file to   │                 │\n│       │               │                 │ dump output to   │                 │\n│ -t    │ --timeout     │ TIMEOUT         │ timeout for      │ 30              │\n│       │               │                 │ internal         │                 │\n│       │               │                 │ operations       │                 │\n│ -L    │ --log         │ {CRITICAL,ERRO… │ console log      │ WARNING         │\n│       │               │                 │ level            │                 │\n└───────┴───────────────┴─────────────────┴──────────────────┴─────────────────┘\n\n\nCopyright© 2024 Thomas Phipps\n\n"
    assert capture.get() == expected
    with pytest.raises(SystemExit) as excinfo:
        testing.build_args(["-h"])
