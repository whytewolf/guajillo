import asyncio
import json
import logging
from typing import Any

import yaml
from rich.console import Console
from rich.status import Status
from rich.syntax import Syntax

from guajillo.exceptions import TerminateTaskGroup

log = logging.getLogger(__name__)


class Outputs:
    def __init__(self, console: Console, parser=None, config=None) -> None:
        self.config = config
        self.parser = parser
        self.console = console
        self.cstatus = Status("Waiting ...", console=self.console)
        self.cstatus.start()

    async def json(self, event: dict["str", Any]) -> None:
        self.console.print_json(json.dumps(event))

    async def yaml(self, event: dict["str", Any]) -> None:
        yaml_output = yaml.dump(event["return"][0])
        syntax = Syntax(yaml_output, "yaml", line_numbers=True)
        self.console.print(syntax)

    async def status(self, event: dict[str, Any]) -> None:
        if "Minions" in event["info"][0]:
            queued = f"{len(list(event['return'][0].keys()))}/{len(event["info"][0]["Minions"])}"
            msg = f"{queued} returned from jid: {event['info'][0]['jid']}"
        if "Error" in event["info"][0]:
            msg = f"waiting on master for jid: {event['info'][0]['jid']}"
        self.cstatus.update(msg)

    async def boolean(self, event: dict[str, Any]) -> None:
        nonreturned = []
        output = event["return"][0]
        if "Minions" in event["info"][0]:
            items = event["info"][0]["Minions"]
            nonreturned = [x for x in items if x not in output]
        for item in event["info"][0]["Result"]:
            if (
                "success" in event["info"][0]["Result"][item]
                and event["info"][0]["Result"][item]["success"]
            ) or (
                "success" in event["info"][0]["Result"][item]["return"]
                and event["info"][0]["Result"][item]["return"]["success"]
            ):
                self.console.print(f"[green]✔ {item}[/green]")
            else:
                self.console.print(f"[red]:-1: {item}[/red]")
        if len(nonreturned) > 0:
            self.console.print("[red]Minions that did not return[/red]")
            for item in nonreturned:
                self.console.print(f"[red]✘ {item}[/red]")

    async def taskMan(self, async_comms: dict[str, Any]) -> None:
        try:
            log.info("Starting output Task Manager")
            self.async_comms = async_comms
            event = self.async_comms["events"].pop()
            while event["meta"]["step"] != "final":
                log.debug("awaiting Event update")
                log.debug("received event update")
                if len(self.async_comms["events"]) > 0:
                    event = self.async_comms["events"].pop()
                    if event["meta"]["step"] == "final":
                        self.cstatus.stop()
                    log.debug(f"calling outputer {event["meta"]["output"]}")
                    await getattr(self, event["meta"]["output"])(event["output"])
                await asyncio.sleep(0.5)
            self.async_comms["one"] = True
        except Exception:
            self.console.print_exception(show_locals=self.config["debug"])
            raise TerminateTaskGroup()
