from rich.console import Console

from guajillo.utils.cli import CliParse
from guajillo.utils.conn import Guajillo


def test_init():
    cli = CliParse()
    cli.build_args(["-p", "netapi"])
    config = {"profile": {"username": "test", "password": "fake", "auth": "pam"}}
    testClass = Guajillo(
        url="http://test.com", parser=cli, config=config, console=Console()
    )
    assert testClass.config == config
    assert testClass.parser is cli
    assert testClass.url == "http://test.com"
    assert testClass.url.scheme == "http"
    assert testClass.url.host == "test.com"
