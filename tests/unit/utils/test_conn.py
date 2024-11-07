import re

import httpx
import pytest
from rich.console import Console

from guajillo.exceptions import GuajilloException
from guajillo.utils.cli import CliParse
from guajillo.utils.conn import Guajillo


@pytest.fixture
def build_conn(request):
    cli = CliParse()
    marker = request.node.get_closest_marker("buildargs_data")
    if marker is None:
        data = []
    else:
        data = marker.args[0]

    print(data)

    cli.build_args(data)
    config = {"netapi": {"username": "testUser", "password": "testPass", "auth": "pam"}}
    testClass = Guajillo(
        url="http://test.com:8000", parser=cli, config=config, console=Console()
    )
    return testClass


@pytest.fixture(scope="module", params=[0, 1, 2, 3])
def build_conn_parm(request):
    cli = CliParse()
    param = request.param
    testing = [
        {
            "expected": [
                {
                    "client": "local_async",
                    "tgt": "*",
                    "tgt_type": "glob",
                    "fun": "test.arg",
                    "arg": ["test"],
                    "kwarg": {"testing": "test"},
                }
            ],
            "data": ["salt", "*", "test.arg", "test", "testing=test"],
            "eresponse": {"return": "blah"},
            "status_code": 200,
        },
        {
            "expected": [
                {
                    "client": "local_async",
                    "tgt": "*",
                    "tgt_type": "compound",
                    "fun": "test.arg",
                    "arg": ["test"],
                    "kwarg": {"testing": "test"},
                }
            ],
            "data": ["salt", "-C", "*", "test.arg", "test", "testing=test"],
            "eresponse": {"return": "blah"},
            "status_code": 200,
        },
        {
            "expected": [
                {
                    "client": "runner_async",
                    "fun": "test.arg",
                    "arg": ["test"],
                    "kwarg": {"testing": "test"},
                }
            ],
            "data": ["salt-run", "test.arg", "test", "testing=test"],
            "eresponse": {"return": "blah"},
            "status_code": 200,
        },
        {
            "expected": [
                {
                    "client": "runner_async",
                    "fun": "test.args",
                    "arg": ["test"],
                    "kwarg": {"testing": "test"},
                }
            ],
            "data": ["salt-run", "test.args", "test", "testing=test"],
            "eresponse": {"return": "blah"},
            "status_code": 500,
        },
    ][param]

    cli.build_args(testing["data"])
    config = {"netapi": {"username": "testUser", "password": "testPass", "auth": "pam"}}
    testClass = Guajillo(
        url="http://test.com:8000", parser=cli, config=config, console=Console()
    )
    testing.update({"testClass": testClass})
    return testing


def test_init():
    cli = CliParse()
    cli.build_args(["-p", "profile"])
    config = {"profile": {"username": "test", "password": "fake", "auth": "pam"}}
    testClass = Guajillo(
        url="http://test.com:8000", parser=cli, config=config, console=Console()
    )
    assert testClass.config == config
    assert testClass.parser is cli
    assert testClass.url == "http://test.com:8000"
    assert testClass.url.scheme == "http"
    assert testClass.url.host == "test.com"
    assert testClass.url.port == 8000
    assert testClass.cookies == httpx.Cookies()
    with pytest.raises(
        GuajilloException,
        match=re.escape("Unknown URL Scheme hxxp in url: hxxp://test.com"),
    ):
        testClass = Guajillo(
            url="hxxp://test.com", parser=cli, config=config, console=Console()
        )


@pytest.mark.asyncio
async def test_login(httpx_mock, build_conn):
    return_response = {
        "return": [
            {
                "token": "fakeToken",
                "user": "testUser",
                "eauth": "pam",
                "perms": [".*", "@jobs", "@runner", "@wheel"],
            }
        ]
    }

    httpx_mock.add_response(url="http://test.com:8000/login", json=return_response)
    httpx_mock.add_response(url="http://test.com:8000/login", status_code=403)

    testClass = build_conn

    response = await testClass.login()
    assert response == return_response

    with pytest.raises(httpx.HTTPStatusError):
        response = await testClass.login()


def test__get_target_type(build_conn):
    testClass = build_conn
    assert testClass._get_target_type("-C") == "compound"
    assert testClass._get_target_type("-E") == "pcre"
    assert testClass._get_target_type("-P") == "grain_pcre"
    assert testClass._get_target_type("-G") == "grain"
    assert testClass._get_target_type("-L") == "list"
    assert testClass._get_target_type("-I") == "pillar"
    assert testClass._get_target_type("-J") == "pillar_pcre"
    assert testClass._get_target_type("-S") == "ipcidr"
    assert testClass._get_target_type("-R") == "range"
    assert testClass._get_target_type("-N") == "nodegroup"

    with pytest.raises(GuajilloException, match="Unknown Target Type"):
        _ = testClass._get_target_type("-Q")


def test__make_params(build_conn_parm):
    testClass = build_conn_parm["testClass"]
    params = testClass._make_params()
    assert params == build_conn_parm["expected"]


@pytest.mark.asyncio
async def test_call(httpx_mock, build_conn_parm):
    testClass = build_conn_parm["testClass"]
    httpx_mock.add_response(
        url="http://test.com:8000",
        json=build_conn_parm["eresponse"],
        status_code=build_conn_parm["status_code"],
    )
    test = await testClass.call(build_conn_parm["expected"])
    assert test == build_conn_parm["eresponse"]
