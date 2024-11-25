from rich.console import Group
from rich.text import Text


async def render(event, console):
    output = event["info"][0]["Result"]
    items = event["info"][0]["Minions"]
    nonreturned = [x for x in items if x not in output]
    if len(nonreturned) > 0:
        header = Text("[red]Minions that did not return[/red]\n")
        minions = Text(
            ", ".join(list(map(lambda item: f"[red]✘ {item}[/red]", nonreturned)))
        )
        return Group(header, minions)
    return Text("All minions returned")
