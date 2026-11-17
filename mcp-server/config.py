import os
from pathlib import Path
from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_REPO_ROOT / ".env")
load_dotenv(_REPO_ROOT / "assistant-api" / ".env")


class MCPSettings:
    CATALOG_API_URL: str = os.getenv("CATALOG_API_URL", "http://localhost:8001").rstrip("/")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "").strip()
    MCP_TRANSPORT: str = os.getenv("MCP_TRANSPORT", "stdio")


settings = MCPSettings()

