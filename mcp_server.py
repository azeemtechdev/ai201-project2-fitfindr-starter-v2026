"""
Your MCP server. ← UNIT 4, MILESTONE 1
"""

from mcp.server.fastmcp import FastMCP

from tools import search_listings as _search_listings_impl

# log_level="WARNING" keeps the server from printing an INFO line for every request.
mcp = FastMCP("fitfindr", log_level="WARNING")


# ── Register search_listings ──────────────────────────────────────────────────

@mcp.tool()
def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search second-hand thrift listings for items matching description keywords,
    an optional clothing/shoe size, and an optional maximum price in USD.
    Returns a ranked list of matching listing dicts, or an empty list if no matches are found.
    """
    return _search_listings_impl(description, size, max_price)


if __name__ == "__main__":
    mcp.run()