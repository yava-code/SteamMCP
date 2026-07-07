from fastmcp import FastMCP
import logging

# Import from new steam package
from steam.adapters import (
    fetch_steam_profile,
    fetch_friend_list,
    fetch_player_achievements,
    fetch_user_stats_for_game,
    fetch_owned_games,
    fetch_recently_played_games,
    fetch_game_news,
    fetch_game_schema,
    fetch_app_details,
    resolve_vanity_url,
    fetch_user_level,
    fetch_user_badges,
    fetch_global_achievement_percentages,
    fetch_player_bans,
)
from steam.adapters import (
    fetch_top_market,
    search_market,
    fetch_item_price_history,
    fetch_item_price_overview,
    fetch_market_popular_items,
    fetch_market_recent_activity,
    fetch_item_listings,
    fetch_item_orders_histogram,
)
from steam.adapters import (
    search_games,
    get_featured_specials,
    get_store_highlights,
    get_app_reviews_summary,
    get_app_tags,
    get_release_calendar,
    get_app_update_signal,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

mcp = FastMCP(name="steamcp")


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


@mcp.tool()
def get_friends(steam_id: str) -> dict:
    """
    Fetch friend list for a Steam user

    Args:
        steam_id: Steam ID of the user

    Returns:
        Dict containing friend list information
    """
    logger.info(f"Fetching friend list for Steam ID: {steam_id}")
    return fetch_friend_list(steam_id)


@mcp.tool()
def resolve_vanity_url_name(vanity_url_name: str) -> dict:
    """
    Resolve a vanity URL name to a Steam ID

    Args:
        vanity_url_name: The vanity URL name to resolve

    Returns:
        Dict containing the resolved Steam ID
    """
    logger.info(f"Resolving vanity URL name: {vanity_url_name}")
    return resolve_vanity_url(vanity_url_name)


@mcp.tool()
def get_player_achievements(steam_id: str, app_id: int) -> dict:
    """
    Fetch achievements for a player in a specific game

    Args:
        steam_id: Steam ID of the player
        app_id: Application ID of the game

    Returns:
        Dict containing achievement information
    """
    logger.info(f"Fetching achievements for Steam ID: {steam_id}, App ID: {app_id}")
    return fetch_player_achievements(steam_id, app_id)


@mcp.tool()
def get_user_stats(steam_id: str, app_id: int) -> dict:
    """
    Fetch stats for a player in a specific game

    Args:
        steam_id: Steam ID of the player
        app_id: Application ID of the game

    Returns:
        Dict containing player stats
    """
    logger.info(f"Fetching stats for Steam ID: {steam_id}, App ID: {app_id}")
    return fetch_user_stats_for_game(steam_id, app_id)


@mcp.tool()
def get_owned_games(steam_id: str, include_appinfo: bool = True, include_played_free_games: bool = True) -> dict:
    """
    Fetch owned games for a Steam user

    Args:
        steam_id: Steam ID of the user
        include_appinfo: Include game name and icon information
        include_played_free_games: Include free games that the user has played

    Returns:
        Dict containing owned games information
    """
    logger.info(f"Fetching owned games for Steam ID: {steam_id}")
    return fetch_owned_games(steam_id, include_appinfo, include_played_free_games)


@mcp.tool()
def get_recently_played_games(steam_id: str, count: int = 10) -> dict:
    """
    Fetch recently played games for a Steam user

    Args:
        steam_id: Steam ID of the user
        count: Number of games to return

    Returns:
        Dict containing recently played games information
    """
    logger.info(f"Fetching recently played games for Steam ID: {steam_id}")
    return fetch_recently_played_games(steam_id, count)


@mcp.tool()
def get_game_news(app_id: int) -> dict:
    """
    Fetch news articles for a specific game

    Args:
        app_id: Application ID of the game

    Returns:
        Dict containing game news articles
    """
    logger.info(f"Fetching game news for App ID: {app_id}")
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
    if count <= 0 or count > 100:
        raise ValueError("Count must be between 1 and 100")
    logger.info(f"Fetching top market items, count: {count}, sort: {sort_column}")
    return fetch_top_market(count, start, sort_column, sort_dir)


@mcp.tool()
def search_market_items(query: str, app_id: int | None = None, count: int = 100, start: int = 0) -> dict:
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
    if count <= 0 or count > 100:
        raise ValueError("Count must be between 1 and 100")
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
    if count <= 0 or count > 100:
        raise ValueError("Count must be between 1 and 100")
    logger.info(f"Fetching popular market items, count: {count}")
    return fetch_market_popular_items(count)


@mcp.tool()
def get_recent_market_activity(app_id: int | None = None, count: int = 10) -> dict:
    """
    Fetch recent activity from the Steam Community Market

    Args:
        app_id: Filter by app ID (optional)
        count: Number of items to return (max 100)

    Returns:
        Dict containing recent market activity data
    """
    if count <= 0 or count > 100:
        raise ValueError("Count must be between 1 and 100")
    logger.info(f"Fetching recent market activity, count: {count}")
    return fetch_market_recent_activity(app_id, count)


# ============ New Tools from Stage 1 ============

@mcp.tool()
def get_user_level(steam_id: str) -> dict:
    """
    Fetch Steam user level

    Args:
        steam_id: Steam ID of the user

    Returns:
        Dict containing user level data
    """
    logger.info(f"Fetching user level for Steam ID: {steam_id}")
    return fetch_user_level(steam_id)


@mcp.tool()
def get_user_badges(steam_id: str) -> dict:
    """
    Fetch badges owned by a Steam user

    Args:
        steam_id: Steam ID of the user

    Returns:
        Dict containing user badges data
    """
    logger.info(f"Fetching user badges for Steam ID: {steam_id}")
    return fetch_user_badges(steam_id)


@mcp.tool()
def get_player_bans(steam_id: str) -> dict:
    """
    Fetch player bans information

    Args:
        steam_id: Steam ID of the user

    Returns:
        Dict containing player bans data
    """
    logger.info(f"Fetching player bans for Steam ID: {steam_id}")
    # Import here to avoid circular dependency
    from steam.adapters import fetch_player_bans
    return fetch_player_bans(steam_id)


@mcp.tool()
def get_current_players(app_id: int) -> dict:
    """
    Fetch current player count for a game

    Args:
        app_id: Application ID of the game

    Returns:
        Dict containing current player count data
    """
    logger.info(f"Fetching current players for App ID: {app_id}")
    # Import here to avoid circular dependency
    from steam.web import SteamWebAPI
    web = SteamWebAPI()
    response = web.get_current_players(app_id)
    return response.to_dict()


@mcp.tool()
def get_global_achievement_percentages(app_id: int) -> dict:
    """
    Fetch global achievement completion percentages for a game

    Args:
        app_id: Application ID of the game

    Returns:
        Dict containing global achievement percentages data
    """
    logger.info(f"Fetching global achievement percentages for App ID: {app_id}")
    return fetch_global_achievement_percentages(app_id)


# ============ Stage 2: Store & Discovery Tools ============

@mcp.tool()
def search_games(query: str, country_code: str = "US", language: str = "english", limit: int = 20) -> dict:
    """
    Search for games in the Steam Store

    Args:
        query: Search query
        country_code: Country code for localized content (default: US)
        language: Language for localized content (default: english)
        limit: Maximum number of results to return (default: 20)

    Returns:
        Dict containing search results
    """
    logger.info(f"Searching games with query: {query}")
    return search_games(query, country_code, language, limit)


@mcp.tool()
def get_featured_specials(country_code: str = "US", language: str = "english") -> dict:
    """
    Get featured specials (sales) from the Steam Store

    Args:
        country_code: Country code for localized content (default: US)
        language: Language for localized content (default: english)

    Returns:
        Dict containing featured specials data
    """
    logger.info("Fetching featured specials")
    return get_featured_specials(country_code, language)


@mcp.tool()
def get_store_highlights(country_code: str = "US", language: str = "english") -> dict:
    """
    Get store highlights (featured content) from the Steam Store

    Args:
        country_code: Country code for localized content (default: US)
        language: Language for localized content (default: english)

    Returns:
        Dict containing store highlights data
    """
    logger.info("Fetching store highlights")
    return get_store_highlights(country_code, language)


@mcp.tool()
def get_app_reviews_summary(app_id: int, country_code: str = "US", language: str = "english") -> dict:
    """
    Get reviews summary for a specific app

    Args:
        app_id: Application ID
        country_code: Country code for localized content (default: US)
        language: Language for localized content (default: english)

    Returns:
        Dict containing reviews summary data
    """
    logger.info(f"Fetching reviews summary for App ID: {app_id}")
    return get_app_reviews_summary(app_id, country_code, language)


@mcp.tool()
def get_app_tags(app_id: int, country_code: str = "US", language: str = "english") -> dict:
    """
    Get tags for a specific app

    Args:
        app_id: Application ID
        country_code: Country code for localized content (default: US)
        language: Language for localized content (default: english)

    Returns:
        Dict containing app tags data
    """
    logger.info(f"Fetching tags for App ID: {app_id}")
    return get_app_tags(app_id, country_code, language)


@mcp.tool()
def get_release_calendar(country_code: str = "US", language: str = "english", 
                         start_date: str | None = None, end_date: str | None = None) -> dict:
    """
    Get release calendar from the Steam Store

    Args:
        country_code: Country code for localized content (default: US)
        language: Language for localized content (default: english)
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)

    Returns:
        Dict containing release calendar data
    """
    logger.info("Fetching release calendar")
    return get_release_calendar(country_code, language, start_date, end_date)


@mcp.tool()
def get_app_update_signal(app_id: int) -> dict:
    """
    Get update signal for a specific app (detect if recently updated)

    This tool checks multiple sources to detect if an app has been recently updated:
    - App details (change number)
    - News items (recent announcements)
    - Build ID changes

    Args:
        app_id: Application ID

    Returns:
        Dict containing update signal data with:
        - has_recent_news: Boolean indicating recent news
        - recent_news_count: Number of recent news items
        - last_news_date: Date of last news item
        - app_name: Name of the app
        - last_updated: Last update timestamp
    """
    logger.info(f"Fetching update signal for App ID: {app_id}")
    return get_app_update_signal(app_id)


if __name__ == "__main__":
    logger.info("Starting Steam MCP server")
    mcp.run()