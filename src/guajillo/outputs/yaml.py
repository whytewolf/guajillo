from typing import Any

import yaml
from rich.syntax import Syntax


async def render(event: dict[str, Any], console) -> None:
    yaml_output = yaml.dump(event["return"][0])
    return Syntax(yaml_output, "yaml")
