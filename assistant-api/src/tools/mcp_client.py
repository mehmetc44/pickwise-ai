import os
import sys
from pathlib import Path
from langchain_core.tools import BaseTool

from core.config import settings


def _get_mcp_server_path() -> str:
    repo_root = Path(__file__).resolve().parents[3]
    server_path = repo_root / "mcp-server" / "server.py"
    if not server_path.exists():
        raise FileNotFoundError(f"MCP server dosyası bulunamadı: {server_path}")
    return str(server_path)


async def load_mcp_tools() -> dict[str, BaseTool]:
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
    except ImportError as exc:
        raise ImportError(
            "MCP bağlantısı için 'mcp' ve 'langchain-mcp-adapters' paketleri gerekli. "
            "Lütfen 'uv sync' çalıştırın."
        ) from exc

    mcp_url = os.getenv("MCP_SERVER_URL", "").strip()

    if mcp_url:
        connections = {
            "commerce": {
                "transport": "streamable_http",
                "url": mcp_url,
            }
        }
    else:
        connections = {
            "commerce": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [_get_mcp_server_path()],
                "env": {
                    **os.environ,
                    "CATALOG_API_URL": settings.CATALOG_API_URL,
                },
            }
        }

    client = MultiServerMCPClient(connections)
    tools = await client.get_tools()
    return {tool.name: tool for tool in tools}
