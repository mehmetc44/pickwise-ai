from mcp.server.fastmcp import FastMCP

from config import settings
from tools.catalog_tools import (
    compare_products,
    get_closest_products,
    get_product_details,
    get_product_reviews,
)
from tools.web_tools import web_search

mcp = FastMCP("AgenticCommerceMCP")

mcp.tool()(get_closest_products)
mcp.tool()(get_product_details)
mcp.tool()(compare_products)
mcp.tool()(get_product_reviews)
mcp.tool()(web_search)


if __name__ == "__main__":
    mcp.run(transport=settings.MCP_TRANSPORT)
