# server.py
from fastmcp import FastMCP

from fetcher import fetch_steam_profile

mcp = FastMCP(
    name="steamcp"
)



@mcp.tool()
def get_profile_info(id: str) -> dict:
    """
    Fetch steam profile base info

    Args:
        id: Steam ID
    """
    return fetch_steam_profile(id)



if __name__ == "__main__":
    mcp.run()