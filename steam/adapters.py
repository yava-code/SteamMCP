"""
Adapters for backward compatibility with old fetcher.py and market.py modules.

This module provides wrapper functions that use the new SteamClient
but maintain the same interface as the old modules.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from steam.client import SteamClient, APIResponse
from steam.web import SteamWebAPI
from steam.market import SteamMarketAPI

logger = logging.getLogger(__name__)

# Create singleton instances
_web_api: Optional[SteamWebAPI] = None
_market_api: Optional[SteamMarketAPI] = None


def _get_web_api() -> SteamWebAPI:
    """Get or create singleton SteamWebAPI instance."""
    global _web_api
    if _web_api is None:
        _web_api = SteamWebAPI()
    return _web_api


def _get_market_api() -> SteamMarketAPI:
    """Get or create singleton SteamMarketAPI instance."""
    global _market_api
    if _market_api is None:
        _market_api = SteamMarketAPI()
    return _market_api


# ============ Fetcher Adapters ============

def fetch_steam_profile(steam_id: str) -> Dict[str, Any]:
    """Adapter for old fetch_steam_profile function."""
    web = _get_web_api()
    response = web.get_profile_info(steam_id)
    return response.to_dict()


def fetch_friend_list(steam_id: str, relationship: str = "friend") -> Dict[str, Any]:
    """Adapter for old fetch_friend_list function."""
    web = _get_web_api()
    response = web.get_friends(steam_id, relationship)
    return response.to_dict()


def fetch_player_achievements(steam_id: str, app_id: Union[str, int], language: str = "english") -> Dict[str, Any]:
    """Adapter for old fetch_player_achievements function."""
    web = _get_web_api()
    response = web.get_player_achievements(steam_id, app_id, language)
    return response.to_dict()


def fetch_user_stats_for_game(steam_id: str, app_id: Union[str, int]) -> Dict[str, Any]:
    """Adapter for old fetch_user_stats_for_game function."""
    web = _get_web_api()
    response = web.get_user_stats_for_game(steam_id, app_id)
    return response.to_dict()


def fetch_owned_games(steam_id: str, include_appinfo: bool = True, include_played_free_games: bool = True) -> Dict[str, Any]:
    """Adapter for old fetch_owned_games function."""
    web = _get_web_api()
    response = web.get_owned_games(steam_id, include_appinfo, include_played_free_games)
    return response.to_dict()


def fetch_recently_played_games(steam_id: str, count: int = 10) -> Dict[str, Any]:
    """Adapter for old fetch_recently_played_games function."""
    web = _get_web_api()
    response = web.get_recently_played_games(steam_id, count)
    return response.to_dict()


def fetch_game_news(app_id: Union[str, int], count: int = 3, maxlength: int = 300, feed_name: Optional[str] = None) -> Dict[str, Any]:
    """Adapter for old fetch_game_news function."""
    web = _get_web_api()
    response = web.get_game_news(app_id, count, maxlength, feed_name)
    return response.to_dict()


def fetch_game_schema(app_id: Union[str, int], language: str = "english") -> Dict[str, Any]:
    """Adapter for old fetch_game_schema function."""
    web = _get_web_api()
    response = web.get_game_schema(app_id, language)
    return response.to_dict()


def fetch_app_details(app_id: Union[str, int], country_code: str = "US") -> Dict[str, Any]:
    """Adapter for old fetch_app_details function."""
    web = _get_web_api()
    response = web.get_app_details(app_id, country_code)
    return response.to_dict()


def fetch_global_achievement_percentages(app_id: Union[str, int]) -> Dict[str, Any]:
    """Adapter for old fetch_global_achievement_percentages function."""
    web = _get_web_api()
    response = web.get_global_achievement_percentages(app_id)
    return response.to_dict()


def fetch_user_level(steam_id: str) -> Dict[str, Any]:
    """Adapter for old fetch_user_level function."""
    web = _get_web_api()
    response = web.get_user_level(steam_id)
    return response.to_dict()


def fetch_user_badges(steam_id: str) -> Dict[str, Any]:
    """Adapter for old fetch_user_badges function."""
    web = _get_web_api()
    response = web.get_user_badges(steam_id)
    return response.to_dict()


def resolve_vanity_url(vanity_url_name: str) -> Dict[str, Any]:
    """Adapter for old resolve_vanity_url function."""
    web = _get_web_api()
    response = web.resolve_vanity_url(vanity_url_name)
    return response.to_dict()


def fetch_player_bans(steam_id: str) -> Dict[str, Any]:
    """Adapter for fetch_player_bans function."""
    web = _get_web_api()
    response = web.get_player_bans(steam_id)
    return response.to_dict()


# ============ Market Adapters ============

def fetch_top_market(count: int = 100, start: int = 0, sort_column: str = "popular", sort_dir: str = "desc") -> Dict[str, Any]:
    """Adapter for old fetch_top_market function."""
    market = _get_market_api()
    response = market.get_top_items(count, start, sort_column, sort_dir)
    return response.to_dict()


def search_market(query: str, appid: Optional[int] = None, count: int = 100, start: int = 0) -> Dict[str, Any]:
    """Adapter for old search_market function."""
    market = _get_market_api()
    response = market.search_items(query, appid, count, start)
    return response.to_dict()


def fetch_item_price_history(appid: int, market_hash_name: str) -> Dict[str, Any]:
    """Adapter for old fetch_item_price_history function."""
    market = _get_market_api()
    response = market.get_item_price_history(appid, market_hash_name)
    return response.to_dict()


def fetch_item_price_overview(appid: int, market_hash_name: str, currency: int = 1) -> Dict[str, Any]:
    """Adapter for old fetch_item_price_overview function."""
    market = _get_market_api()
    response = market.get_item_price_overview(appid, market_hash_name, currency)
    return response.to_dict()


def fetch_market_popular_items(count: int = 10) -> Dict[str, Any]:
    """Adapter for old fetch_market_popular_items function."""
    market = _get_market_api()
    response = market.get_popular_items(count)
    return response.to_dict()


def fetch_market_recent_activity(appid: Optional[int] = None, count: int = 10) -> Dict[str, Any]:
    """Adapter for old fetch_market_recent_activity function."""
    market = _get_market_api()
    response = market.get_recent_activity(appid, count)
    return response.to_dict()


def fetch_item_listings(appid: int, market_hash_name: str, currency: int = 1, start: int = 0, count: int = 10) -> Dict[str, Any]:
    """Adapter for old fetch_item_listings function."""
    market = _get_market_api()
    response = market.get_item_listings(appid, market_hash_name, currency, start, count)
    return response.to_dict()


def fetch_item_orders_histogram(item_nameid: str, currency: int = 1) -> Dict[str, Any]:
    """Adapter for old fetch_item_orders_histogram function."""
    market = _get_market_api()
    response = market.get_item_orders_histogram(item_nameid, currency)
    return response.to_dict()


# ============ Store Adapters ============

def search_games(query: str, country_code: str = "US", language: str = "english", limit: int = 20) -> Dict[str, Any]:
    """Adapter for search_games function."""
    from steam.store import SteamStoreAPI
    store = SteamStoreAPI()
    response = store.search_games(query, country_code, language, limit)
    return response.to_dict()


def get_featured_specials(country_code: str = "US", language: str = "english") -> Dict[str, Any]:
    """Adapter for get_featured_specials function."""
    from steam.store import SteamStoreAPI
    store = SteamStoreAPI()
    response = store.get_featured_specials(country_code, language)
    return response.to_dict()


def get_store_highlights(country_code: str = "US", language: str = "english") -> Dict[str, Any]:
    """Adapter for get_store_highlights function."""
    from steam.store import SteamStoreAPI
    store = SteamStoreAPI()
    response = store.get_store_highlights(country_code, language)
    return response.to_dict()


def get_app_reviews_summary(app_id: Union[str, int], country_code: str = "US", language: str = "english") -> Dict[str, Any]:
    """Adapter for get_app_reviews_summary function."""
    from steam.store import SteamStoreAPI
    store = SteamStoreAPI()
    response = store.get_app_reviews_summary(app_id, country_code, language)
    return response.to_dict()


def get_app_tags(app_id: Union[str, int], country_code: str = "US", language: str = "english") -> Dict[str, Any]:
    """Adapter for get_app_tags function."""
    from steam.store import SteamStoreAPI
    store = SteamStoreAPI()
    response = store.get_app_tags(app_id, country_code, language)
    return response.to_dict()


def get_release_calendar(country_code: str = "US", language: str = "english", 
                         start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """Adapter for get_release_calendar function."""
    from steam.store import SteamStoreAPI
    store = SteamStoreAPI()
    response = store.get_release_calendar(country_code, language, start_date, end_date)
    return response.to_dict()


def get_app_update_signal(app_id: Union[str, int]) -> Dict[str, Any]:
    """Adapter for get_app_update_signal function."""
    from steam.store import SteamStoreAPI
    store = SteamStoreAPI()
    response = store.get_app_update_signal(app_id)
    return response.to_dict()


# ============ Price Tracker Adapters ============

_price_tracker: Optional[Any] = None


def _get_price_tracker() -> Any:
    """Get or create singleton PriceTracker instance."""
    global _price_tracker
    if _price_tracker is None:
        from steam.price_tracker import PriceTracker
        _price_tracker = PriceTracker()
    return _price_tracker


def track_app_price(app_id: Union[str, int], currency: str = "USD") -> Dict[str, Any]:
    """Adapter for track_app_price function."""
    tracker = _get_price_tracker()
    response = tracker.track_app(app_id, currency)
    return response.to_dict()


def get_price_history(app_id: Union[str, int], currency: str = "USD", days: int = 30) -> Dict[str, Any]:
    """Adapter for get_price_history function."""
    tracker = _get_price_tracker()
    response = tracker.get_price_history(app_id, currency, days)
    return response.to_dict()


def check_discounts(app_ids: List[Union[str, int]], currency: str = "USD") -> Dict[str, Any]:
    """Adapter for check_discounts function."""
    tracker = _get_price_tracker()
    response = tracker.check_discounts(app_ids, currency)
    return response.to_dict()


def compare_regional_prices(app_id: Union[str, int], regions: List[str] = None) -> Dict[str, Any]:
    """Adapter for compare_regional_prices function."""
    tracker = _get_price_tracker()
    if regions is None:
        regions = ["US", "EU", "RU"]
    response = tracker.compare_regions(app_id, regions)
    return response.to_dict()


# ============ Wishlist Adapters ============

_wishlist_manager: Optional[Any] = None


def _get_wishlist_manager() -> Any:
    """Get or create singleton WishlistManager instance."""
    global _wishlist_manager
    if _wishlist_manager is None:
        from steam.wishlist import WishlistManager
        _wishlist_manager = WishlistManager()
    return _wishlist_manager


def get_wishlist(steam_id: str) -> Dict[str, Any]:
    """Adapter for get_wishlist function."""
    manager = _get_wishlist_manager()
    response = manager.get_wishlist(steam_id)
    return response.to_dict()


def check_in_wishlist(steam_id: str, app_id: Union[str, int]) -> Dict[str, Any]:
    """Adapter for check_in_wishlist function."""
    manager = _get_wishlist_manager()
    response = manager.check_in_wishlist(steam_id, app_id)
    return response.to_dict()


def get_wishlist_stats(steam_id: str) -> Dict[str, Any]:
    """Adapter for get_wishlist_stats function."""
    manager = _get_wishlist_manager()
    response = manager.get_wishlist_stats(steam_id)
    return response.to_dict()


def get_wishlist_on_sale(steam_id: str) -> Dict[str, Any]:
    """Adapter for get_wishlist_on_sale function."""
    manager = _get_wishlist_manager()
    response = manager.get_wishlist_on_sale(steam_id)
    return response.to_dict()
