from typing import Any

from rich.console import Group
from rich.table import Table
from rich.text import Text

import guajillo.outputs


async def render(event: dict[str, Any], console) -> None:
    output = event["info"][0]["Result"]
    if "Minions" in event["info"][0]:
        isMinion = True
    minions = Table(title="minion highstate", show_header=True)
    minions.add_column("Minion", style="cyan")
    minions.add_column("Highstate")
    for minion, returned in output.items():
        highstate = Table(expand=True)
        highstate.add_column("id", style="magenta")
        highstate.add_column("name", style="magenta")
        highstate.add_column("function", style="magenta")
        highstate.add_column("result", style="magenta")
        highstate.add_column("changes", style="magenta")
        for id, results in returned["return"].items():
            module, id, name, fun = id.split("_|-")
            if results["result"]:
                label = Text("✔", style="green")
            else:
                label = Text("✘", style="red")
            changes = await guajillo.outputs.yaml(
                {"return": [results.get("changes", "")]}, console
            )
            highstate.add_row(
                id,
                name,
                f"{module}.{fun}",
                label,
                changes,
            )
        minions.add_row(minion, highstate)

    nonreturned = await guajillo.outputs.non_returns(event, console)
    return Group(minions, nonreturned)
