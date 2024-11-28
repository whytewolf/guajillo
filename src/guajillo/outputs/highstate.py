import logging
from typing import Any

import yaml
from rich import box
from rich.console import Console, Group, group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

import guajillo.outputs

log = logging.getLogger(__name__)

HIGHSTATE: box.Box = box.Box(
    " ── \n" "    \n" " ── \n" "    \n" " ── \n" " ── \n" "    \n" "    \n"
)


class Highstate:
    def __init__(self, result) -> Table:
        self.event = result
        self.mainTable = Table(
            show_header=True, box=box.ROUNDED, show_lines=True, expand=True
        )
        self.mainTable.add_column("Minion/Master")
        self.mainTable.add_column("Highstate")

    def _yaml(self, renderable):
        yaml_output = yaml.dump(renderable)
        return yaml_output

    @group()
    def build_lowstate_core(self, id, lowstate):
        module, id, name, fun = id.split("_|-")
        ident = Table(expand=True, show_header=False)
        setstyle = "green" if lowstate["result"] else "red"
        ident.add_column("name", ratio=18, style=setstyle)
        ident.add_column("function", ratio=4, style=setstyle)
        ident.add_column("result", ratio=1)
        lowresult = (
            Text("✔", style="green") if lowstate["result"] else Text("✘", style="red")
        )
        ident.add_row(name, f"{module}.{fun}", lowresult)
        yield ident
        if lowstate["comment"] and lowstate["comment"] != "Success!":
            comment = Text(lowstate.get("comment", ""), style=f"bold {setstyle}")
            yield comment
        if lowstate["changes"] and "out" in lowstate["changes"]:
            hsreturn = Highstate(lowstate["changes"]["ret"])
            hsreturn.build_highstate()
            yield hsreturn
        elif lowstate["changes"]:
            changes = self._yaml(lowstate.get("changes", ""))
            yield changes

    @group()
    def build_lowstate(self, results):
        for id, lowstate in results.items():
            _, stateid, _, _ = id.split("_|-")
            yield Panel(
                self.build_lowstate_core(id, lowstate),
                box=HIGHSTATE,
                title=f"{stateid}",
                title_align="left",
            )

    def build_highstate(self):
        for minion, returned in self.event.items():
            # this is what happens because salt doesn't have standard returns.
            if "return" in returned:
                if "return" in returned["return"]:
                    vexed = returned["return"]["return"]["data"][minion]
                else:
                    vexed = returned["return"]
            else:
                vexed = returned
            self.mainTable.add_row(minion, self.build_lowstate(vexed))

    def __rich__(self):
        return self.mainTable


async def render(event: dict[str, Any], console: Console):
    output = Highstate(event["info"][0]["Result"])
    output.build_highstate()
    nonreturns = await guajillo.outputs.non_returns(event, console)
    return Group(output, nonreturns)
