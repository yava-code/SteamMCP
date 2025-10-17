# server.py
from fastmcp import FastMCP

from fetcher import fetch_steam_profile
from market import fetch_top_market

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


@mcp.tool()
def get_profile_info(id: str) -> dict:
    """
    Fetch top 10 market items

    Args:



    """
    return fetch_top_market()



if __name__ == "__main__":
    mcp.run()