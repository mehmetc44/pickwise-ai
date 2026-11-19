import json
from typing import Any


def parse_mcp_tool_output(raw: Any) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    def _collect(obj: Any):
        if isinstance(obj, dict):
            if obj.get("type") == "text" and isinstance(obj.get("text"), str):
                try:
                    _collect(json.loads(obj["text"]))
                except json.JSONDecodeError:
                    pass
            else:
                items.append(obj)
        elif isinstance(obj, list):
            for el in obj:
                _collect(el)
        elif isinstance(obj, str):
            try:
                _collect(json.loads(obj))
            except json.JSONDecodeError:
                pass

    _collect(raw)
    return items
