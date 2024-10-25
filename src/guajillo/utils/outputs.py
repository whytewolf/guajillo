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
            output = list(self.async_comms["events"].keys())[0]
            await getattr(self, output)(self.async_comms["events"][output])
        except Exception:
            self.console.print_exception(show_locals=False)
            raise TerminateTaskGroup()
