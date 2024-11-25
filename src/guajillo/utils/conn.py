import asyncio
import json
import logging
from typing import Any

from httpx import URL, AsyncClient, Cookies, Headers, ReadError
from httpx_sse import aconnect_sse
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
        self.authed = False

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

    def _make_params(self):
        salt_args = self.parser.salt_args
        params = {}
        protocol = salt_args.pop(0)
        if protocol.lower() in ["salt", "salt-call"]:
            if salt_args[0].startswith("-"):
                tgt_type = self._get_target_type(salt_args.pop(0))
                target = salt_args.pop(0)
            else:
                tgt_type = "glob"
                target = salt_args.pop(0)
            params = {
                "client": "local_async",
                "tgt": target,
                "tgt_type": tgt_type,
            }

        if protocol.lower() == "salt-run":
            params = {"client": "runner_async"}

        if protocol.lower() == "salt-wheel":
            params = {"client": "wheel_async"}
        if params == {}:
            raise GuajilloException("Unknown salt protocol")

        fun = salt_args.pop(0)
        args = []
        kwargs = {}
        for index, value in enumerate(salt_args):
            if "=" in value:
                svalue = value.split("=")
                try:
                    rendered = json.loads(svalue[1])
                except ValueError:
                    log.debug("json rendering failed, useing str")
                    rendered = svalue[1]
                kwargs.update({svalue[0]: rendered})
            else:
                try:
                    rendered = json.loads(value)
                except ValueError:
                    rendered = value
                args.append(rendered)

        params.update(
            {
                "fun": fun,
                "arg": args,
                "kwarg": kwargs,
            }
        )
        return [params]

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
        if response.status_code not in [200, 401]:
            response.raise_for_status()
        if response.status_code == 401:
            self.authed = False
            return '{"Status": "Unable to authorize connection"}'
        self.authed = True
        return response.json()

    async def call(self, params=list[dict[str, str]]):
        request = self.client.build_request(
            "POST",
            self.url,
            headers=self.headers,
            cookies=self.cookies,
            json=params,
            timeout=30,
        )
        log.debug(f"sending {params} to {self.url}")
        response = await self.client.send(request)
        return response.json()

    async def job_lookup(self, jid: str):
        url = f"{self.url}/jobs/{jid}"
        request = self.client.build_request(
            "GET",
            url,
            headers=self.headers,
            cookies=self.cookies,
            timeout=30,
        )
        response = await self.client.send(request)
        return response

    async def check_outputer(self, fun: str) -> str:
        defined_outputers = {
            "test.ping": "boolean",
            "state.sls": "highstate",
            "state.highstate": "highstate",
            "state.apply": "highstate",
        }
        if self.parser.parsed_args.output is not None:
            return self.parser.parsed_args.output
        if fun in defined_outputers:
            return defined_outputers[fun]
        return "yaml"

    async def taskMan(self, async_comms: dict["str", Any]) -> None:
        """
        async controller for salt-API client.
        """
        # TODO: This methed is way to big. need to break it into smaller parts
        try:
            log.info("Starting Client Task Manager")
            self.async_comms = async_comms
            output = await self.login()
            if len(self.parser.salt_args) > 0:
                params = self._make_params()
                output = await self.call(params)

                output_event = {
                    "meta": {"output": "json", "step": "normal"},
                    "output": output,
                }
                if "tag" in output["return"][0]:
                    job_type = "master"
                    jid = output["return"][0]["jid"]
                elif "jid" in output["return"][0]:
                    job_type = "minion"
                    jid = output["return"][0]["jid"]
                else:
                    job_type = "error"
                    output_event = {
                        "meta": {
                            "output": "json",
                            "step": "final",
                        },
                        "output": output,
                    }
                    self.async_comms["events"].append(output_event)
                    self.async_comms["update"].set()
            else:
                output_event = {
                    "meta": {
                        "output": "json",
                        "step": "final",
                    },
                    "output": output,
                }
                self.async_comms["events"].append(output_event)
                self.async_comms["update"].set()
            ttl = self.parser.parsed_args.timeout
            # TODO: This needs to be split into its own function
            # TODO: use streamMon as a way to tell if we need to check the job
            while output_event["meta"]["step"] != "final":
                step = "normal"
                output = "status"
                if ttl == 0:
                    step = "final"
                    output = await self.check_outputer(
                        output_event["output"]["info"][0]["Function"]
                    )
                response = await self.job_lookup(jid)
                log.debug(f"waiting on jid: {jid}")
                event = response.json()
                if job_type == "master" and "Error" not in event["info"][0]:
                    step = "final"
                    output = await self.check_outputer(event["info"][0]["Function"])
                elif job_type == "minion" and len(event["info"][0]["Minions"]) <= len(
                    event["return"][0]
                ):
                    step = "final"
                    output = await self.check_outputer(event["info"][0]["Function"])

                output_event = {
                    "meta": {"output": output, "step": step},
                    "output": event,
                }
                self.async_comms["events"].append(output_event)
                self.async_comms["update"].set()
                ttl -= 1
                await asyncio.sleep(0.5)

            await self.client.aclose()
        except Exception:
            self.console.print_exception(show_locals=self.config["debug"])
            raise TerminateTaskGroup()

    async def streamMon(self) -> None:
        """
        async event stream monitoring controller
        """
        try:
            log.info("Starting Client Stream Monitor")
            await asyncio.sleep(0.5)
            while self.authed is False:
                await asyncio.sleep(0.5)
                log.debug("waiting for token")
                continue
            url = f"{self.url}/events"
            try:
                if not self.client.is_closed:
                    async with aconnect_sse(
                        self.client, "GET", url, timeout=1024
                    ) as event_source:
                        async for sse in event_source.aiter_sse():
                            log.debug(sse)
            except ReadError as re:
                log.debug(re)
            except RuntimeError as re:
                log.debug(re)

        except Exception:
            self.console.print_exception(show_locals=self.config["debug"])
            raise TerminateTaskGroup()

    async def close(self):
        await self.client.aclose()
