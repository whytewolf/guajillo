import json
from typing import Any

from rich.json import JSON


async def render(event: dict["str", Any], console) -> None:
    return JSON(json.dumps(event))
