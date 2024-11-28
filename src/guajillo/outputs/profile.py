from typing import Any

from rich.console import Group
from rich.table import Table
from rich.text import Text

import guajillo.outputs


async def render(event: dict[str, Any], console) -> None:
    output = event["info"][0]["Result"]
    isMinion = False
    if "Minions" in event["info"][0]:
        isMinion = True
    for minion, returned in output.items():
        state = Table(title=f"{minion}", width=120, highlight=True)
        state.add_column("State", style="cyan")
        state.add_column("name", style="cyan")
        state.add_column("Function", style="cyan")
        state.add_column("Result")
        state.add_column("Duration", style="magenta")
        total_duration = 0
        good = 0
        bad = 0
        if isMinion:
            vexed = returned["return"]
        else:
            vexed = returned["return"]["return"]["data"][minion]

        for id, results in vexed.items():
            duration = ""
            module, id, name, fun = id.split("_|-")
            if results["result"]:
                result = Text("✔ ", style="green")
                good += 1
            else:
                result = Text("✘", style="red")
                bad += 1
            if "duration" in results:
                duration = Text(
                    f"{results['duration']} ms",
                    style="bold magenta",
                )
                total_duration += results["duration"]
            state.add_row(id, name, f"{module}.{fun}", result, duration)
        state.add_section()
        state.add_row(
            "Final Total",
            "",
            "",
            f"[red]{bad}[/red]/[green]{good}[/green] ({bad + good})",
            f"[bold magenta]{total_duration/1000:.4f} s[/bold magenta]",
        )
    nonreturned = await guajillo.outputs.non_returns(event, console)
    return Group(state, nonreturned)
