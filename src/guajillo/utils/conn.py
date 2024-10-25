import json
import logging
from typing import Any

from httpx import URL, AsyncClient, Cookies, Headers
from rich.console import Console

from guajillo.exceptions import GuajilloException, TerminateTaskGroup
from guajillo.utils.cli import CliParse

log = logging.getLogger(__name__)


class Guajillo:
    def __init__(
        self,
        url: str,
        parser: CliParse,
        config: dict["str", Any],
        console: Console,
    ) -> None:
        self.url: URL = URL(url)
        if self.url.scheme not in ["http", "https"]:
            raise GuajilloException(
                f"Unknown URL Scheme {self.url.scheme} in url: {self.url}"
            )
        self.headers: Headers = Headers(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
            }
        )
        self.cookies: Cookies = Cookies()
        self.client: AsyncClient = AsyncClient(
            headers=self.headers, cookies=self.cookies, timeout=20
        )
        self.parser = parser
        self.config = config
        self.console = console

    async def login(self):
        profile = self.config[self.parser.parsed_args.profile]
        username = profile["username"]
        password = profile["password"]
        auth = profile["auth"]
        url = URL(f"{self.url}/login")
        params = {
            "username": username,
            "password": password,
            "eauth": auth,
        }
        request = self.client.build_request(
            "POST",
            url,
            headers=self.headers,
            cookies=self.cookies,
            json=params,
            timeout=30,
        )
        response = await self.client.send(request)
        if response.status_code != 200:
            response.raise_for_status()
        return response.json()

    def _get_target_type(self, target_type_abbrv: str) -> str:
        tgts = {
            "-C": "compound",
            "-E": "pcre",
            "-P": "grain_pcre",
            "-G": "grain",
            "-L": "list",
            "-I": "pillar",
            "-J": "pillar_pcre",
            "-S": "ipcidr",
            "-R": "range",
            "-N": "nodegroup",
        }
        if target_type_abbrv in tgts:
            return tgts[target_type_abbrv]
        raise GuajilloException("Unknown Target Type")

    async def cmd(self):
        salt_args = self.parser.salt_args
        if salt_args[0].startswith("-"):
            tgt_type = self._get_target_type(salt_args.pop(0))
            target = salt_args.pop(0)
        else:
            tgt_type = "glob"
            target = salt_args.pop(0)
        fun = self.parser.salt_args.pop(0)
        args = []
        kwargs = {}
        for index, value in enumerate(self.parser.salt_args):
            if "=" in value:
                svalue = value.split("=")
                try:
                    rendered = json.loads(svalue[1])
                except ValueError:
                    log.debug("json rendering failed, useing str")
                    rendered = svalue[1]
                kwargs.update({svalue[0]: rendered})
            else:
                args.append(value)

        params = [
            {
                "client": "local",
                "tgt": target,
                "tgt_type": tgt_type,
                "fun": fun,
                "arg": args,
                "kwarg": kwargs,
            }
        ]
        request = self.client.build_request(
            "POST",
            self.url,
            headers=self.headers,
            cookies=self.cookies,
            json=params,
            timeout=30,
        )
        response = await self.client.send(request)
        if response.status_code != 200:
            response.raise_for_status()
        return response.json()

    async def runner(self):
        fun = self.parser.salt_args.pop(0)
        args = []
        kwargs = {}
        for index, value in enumerate(self.parser.salt_args):
            if "=" in value:
                svalue = value.split("=")
                log.debug(f"json loading: {svalue[1]} of type: {type(svalue[1])}")
                try:
                    rendered = json.loads(svalue[1])
                except ValueError:
                    log.debug("json rendering failed, useing str")
                    rendered = svalue[1]
                kwargs.update({svalue[0]: rendered})
            else:
                args.append(value)

        params = [
            {
                "client": "runner",
                "fun": fun,
                "arg": args,
                "kwarg": kwargs,
            }
        ]
        request = self.client.build_request(
            "POST",
            self.url,
            headers=self.headers,
            cookies=self.cookies,
            json=params,
            timeout=30,
        )
        response = await self.client.send(request)
        if response.status_code != 200:
            response.raise_for_status()
        return response.json()

    async def taskMan(self, async_comms: dict["str", Any]) -> None:
        """
        async controller for salt-API client.
        """
        try:
            self.async_comms = async_comms
            login_response = await self.login()
            if len(self.parser.salt_args) > 0:
                self._protocol = self.parser.salt_args.pop(0)
                if self._protocol.lower() in ["salt", "salt-call"]:
                    output = await self.cmd()
                if self._protocol.lower() == "salt-run":
                    output = await self.runner()

                self.async_comms["events"].update({"json": json.dumps(output)})
                self.async_comms["update"].set()
            else:
                self.async_comms["events"].update({"json": json.dumps(login_response)})
                self.async_comms["update"].set()
        except Exception:
            self.console.print_exception(show_locals=False)
            raise TerminateTaskGroup()
