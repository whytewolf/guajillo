from typing import Any

from rich.console import Group
from rich.table import Table

import guajillo.outputs


async def render(event: dict[str, Any], console) -> None:
    result = Table(title="Results")
    result.add_column("Minion")
    result.add_column("Result")
    for item in event["info"][0]["Result"]:
        if (
            "success" in event["info"][0]["Result"][item]
            and event["info"][0]["Result"][item]["success"]
        ) or (
            "success" in event["info"][0]["Result"][item]["return"]
            and event["info"][0]["Result"][item]["return"]["success"]
        ):
            result.add_row(item, "[green]✔[/green]")
        else:
            result.add_row(item, "[red]✘[/red]")
    unknown = await guajillo.outputs.non_returns(event, console)
    return Group(result, unknown)
