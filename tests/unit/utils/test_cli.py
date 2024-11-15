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
    testing.build_args(["-l", "DEBUG"])
    assert testing.parsed_args.log_level == "DEBUG"


def test_cli_log_fail():
    testing = CliParse()
    with pytest.raises(SystemExit) as excinfo:
        testing.build_args(["-l", "ALL"])
    assert excinfo.value.code == 2


def test_help():
    output = Console()
    with output.capture() as capture:
        testing = CliParse(output)
        testing.help(doexit=False)
    expected = """usage: guajillo [-h] [-c CONFIG] [-p PROFILE] [-o OUTPUT] [--out-list] 
[--output-file OUTPUT_FILE] [-L {CRITICAL,ERROR,WARNING,INFO,DEBUG}] [SALT 
commands]

A CLI program for interacting with the salt-api with better output

                                    Options                                     
┏━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Short ┃ Long          ┃ option name     ┃ description      ┃ default         ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ -h    │ --help        │                 │ Show this help   │                 │
│       │               │                 │ and exit         │                 │
│ -c    │ --config      │ CONFIG          │ Config file      │ ~/.config/guaj… │
│       │               │                 │ location         │                 │
│ -p    │ --profile     │ PROFILE         │ Profile from     │ netapi          │
│       │               │                 │ config file to   │                 │
│       │               │                 │ use as login     │                 │
│       │               │                 │ info             │                 │
│ -o    │ --out         │ {json, yaml,    │ force output     │ auto            │
│       │               │ boolean}        │ style through a  │                 │
│       │               │                 │ known output     │                 │
│       │ --output-file │ OUTPUT_FILE     │ Not implimented, │                 │
│       │               │                 │ output file to   │                 │
│       │               │                 │ dump output to   │                 │
│ -t    │ --timeout     │ TIMEOUT         │ timeout for      │ 30              │
│       │               │                 │ internal         │                 │
│       │               │                 │ operations,      │                 │
│       │               │                 │ loops to fetch   │                 │
│ -l    │ --log         │ {CRITICAL,ERRO… │ console log      │ WARNING         │
│       │               │                 │ level            │                 │
└───────┴───────────────┴─────────────────┴──────────────────┴─────────────────┘

Copyright© 2024 Thomas Phipps

"""
    assert capture.get() == expected
    with pytest.raises(SystemExit):
        testing.build_args(["-h"])
