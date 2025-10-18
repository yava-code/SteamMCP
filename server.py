from fastmcp import FastMCP

<<<<<<< Updated upstream
from fetcher import fetch_steam_profile
from market import fetch_top_market

=======

from fetcher import (
    fetch_steam_profile, fetch_friend_list, fetch_player_achievements,
    fetch_user_stats_for_game, fetch_owned_games, fetch_recently_played_games,
    fetch_game_news, fetch_game_schema, fetch_app_details, resolve_vanity_url
)
from market import (
    fetch_top_market, search_market, fetch_item_price_history,
    fetch_item_price_overview, fetch_market_popular_items,
    fetch_market_recent_activity
)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


>>>>>>> Stashed changes
mcp = FastMCP(
    name="steamcp"
)


<<<<<<< Updated upstream
=======
@mcp.tool()
def get_profile_info(steam_id: str) -> dict:
    """
    Fetch Steam profile information for a user
    
    Args:
        steam_id: Steam ID or vanity URL name
    
    Returns:
        Dict containing profile information
    """
    logger.info(f"Fetching profile info for Steam ID: {steam_id}")
    return fetch_steam_profile(steam_id)
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
=======

@mcp.tool()
def get_player_achievements(steam_id: str, app_id: int) -> dict:
    """
    Fetch achievements for a player in a specific game
    
>>>>>>> Stashed changes
    Args:



    """
    return fetch_top_market()

<<<<<<< Updated upstream

=======
@mcp.tool()
def get_game_details(app_id: int) -> dict:
    """
    Fetch details for a specific game
    
    Args:
        app_id: Application ID of the game
    
    Returns:
        Dict containing game details
    """
    logger.info(f"Fetching game details for App ID: {app_id}")
    return fetch_game_news(app_id)

@mcp.tool()
def get_game_schema(app_id: int) -> dict:
    """
    Fetch schema for a specific game
    
    Args:
        app_id: Application ID of the game
    
    Returns:
        Dict containing game schema
    """
    logger.info(f"Fetching game schema for App ID: {app_id}")
    return fetch_game_schema(app_id)

@mcp.tool()
def get_app_details(app_id: int) -> dict:
    """
    Fetch detailed information for a specific app from the Steam Store
    
    Args:
        app_id: Application ID
    
    Returns:
        Dict containing app details
    """
    logger.info(f"Fetching app details for App ID: {app_id}")
    return fetch_app_details(app_id)


@mcp.tool()
def get_top_market_items(count: int = 100, start: int = 0, sort_column: str = "popular", sort_dir: str = "desc") -> dict:
    """
    Fetch top items from the Steam Community Market
    
    Args:
        count: Number of items to return (max 100)
        start: Starting position for pagination
        sort_column: Column to sort by (popular, quantity, price, name)
        sort_dir: Sort direction (desc, asc)
    
    Returns:
        Dict containing market search results
    """
    logger.info(f"Fetching top market items, count: {count}, sort: {sort_column}")
    return fetch_top_market(count, start, sort_column, sort_dir)

@mcp.tool()
def search_market_items(query: str, app_id: int = None, count: int = 100, start: int = 0) -> dict:
    """
    Search for items in the Steam Community Market
    
    Args:
        query: Search query
        app_id: Filter by app ID (optional)
        count: Number of items to return (max 100)
        start: Starting position for pagination
    
    Returns:
        Dict containing market search results
    """
    logger.info(f"Searching market items with query: {query}")
    return search_market(query, app_id, count, start)

@mcp.tool()
def get_item_price_history(app_id: int, market_hash_name: str) -> dict:
    """
    Fetch price history for a specific market item
    
    Args:
        app_id: App ID of the game
        market_hash_name: Market hash name of the item
    
    Returns:
        Dict containing item price history data
    """
    logger.info(f"Fetching price history for item: {market_hash_name}")
    return fetch_item_price_history(app_id, market_hash_name)

@mcp.tool()
def get_item_price_overview(app_id: int, market_hash_name: str, currency: int = 1) -> dict:
    """
    Fetch current price overview for a specific market item
    
    Args:
        app_id: App ID of the game
        market_hash_name: Market hash name of the item
        currency: Currency ID (1 = USD, 2 = GBP, 3 = EUR, etc.)
    
    Returns:
        Dict containing item price overview data
    """
    logger.info(f"Fetching price overview for item: {market_hash_name}")
    return fetch_item_price_overview(app_id, market_hash_name, currency)

@mcp.tool()
def get_popular_market_items(count: int = 10) -> dict:
    """
    Fetch popular items from the Steam Community Market
    
    Args:
        count: Number of items to return (max 100)
    
    Returns:
        Dict containing popular market items data
    """
    logger.info(f"Fetching popular market items, count: {count}")
    return fetch_market_popular_items(count)

@mcp.tool()
def get_recent_market_activity(app_id: int = None, count: int = 10) -> dict:
    """
    Fetch recent activity from the Steam Community Market
    
    Args:
        app_id: Filter by app ID (optional)
        count: Number of items to return (max 100)
    
    Returns:
        Dict containing recent market activity data
    """
    logger.info(f"Fetching recent market activity, count: {count}")
    return fetch_market_recent_activity(app_id, count)
>>>>>>> Stashed changes

if __name__ == "__main__":
    mcp.run()