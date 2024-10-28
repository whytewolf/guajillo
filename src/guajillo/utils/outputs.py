import logging
from typing import Any

from rich.console import Console

from guajillo.exceptions import TerminateTaskGroup

log = logging.getLogger(__name__)


class Outputs:
    def __init__(self, console: Console, parser=None, config=None) -> None:
        self.config = config
        self.parser = parser
        self.console = console

    async def json(self, output: str) -> None:
        self.console.print_json(output)

    async def taskMan(self, async_comms: dict[str, Any]) -> None:
        try:
            self.async_comms = async_comms
            log.debug("awaiting Event update")
            await self.async_comms["update"].wait()
            log.debug("recieved event update")
            while len(self.async_comms["events"]) > 0:
                output = self.async_comms["events"].pop()
                await getattr(self, output["meta"]["output"])(output["output"])
        except Exception:
            self.console.print_exception(show_locals=self.config["debug"])
            raise TerminateTaskGroup()
