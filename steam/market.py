"""
Steam Community Market functions.

This module provides functions for interacting with the Steam Community Market:
- Search and browse items
- Get price history and overviews
- Get popular and recent items
- Get market activity
"""

import logging
import urllib.parse
from typing import Any, Dict, List, Optional, Union

from steam.client import SteamClient, APIResponse, MarketAPIError
from steam.schemas import AppID, MarketItem, PriceOverview, PriceHistory

logger = logging.getLogger(__name__)


class SteamMarketAPI:
    """
    Client for Steam Community Market operations.
    
    This class provides a high-level interface for Steam Community Market endpoints
    with normalized responses and error handling.
    
    Note: Steam Community Market endpoints are unofficial and may be rate-limited.
    
    Usage:
        market = SteamMarketAPI()
        items = market.search_items("AK-47", appid=730)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Steam Market API client.
        
        Args:
            api_key: Steam Web API key (optional, can also use STEAM_API_KEY env var)
        """
        self.client = SteamClient(api_key=api_key)
    
    def search_items(self, query: str, appid: Optional[int] = None, 
                     count: int = 100, start: int = 0) -> APIResponse:
        """
        Search for items in the Steam Community Market.
        
        Args:
            query: Search query
            appid: Filter by app ID (optional)
            count: Number of items to return (max 100)
            start: Starting position for pagination
            
        Returns:
            APIResponse with search results or error
        """
        if not query:
            return APIResponse(
                ok=False,
                source="steam_community",
                data={},
                warnings=["Empty query"],
                error={"message": "Search query cannot be empty"}
            )
        
        if count <= 0 or count > 100:
            return APIResponse(
                ok=False,
                source="steam_community",
                data={},
                warnings=["Invalid count"],
                error={"message": "Count must be between 1 and 100"}
            )
        
        url = f"{self.client.STEAM_COMMUNITY_BASE}/market/search/render"
        params = {"norender": 1, "query": query, "start": start, "count": count}
        
        if appid is not None:
            params["appid"] = appid
        
        response = self.client.get(url, params=params)
        
        # Normalize the response
        if response.ok:
            try:
                items = MarketItem.from_api_response(response.data)
                response.data = {"items": [i.to_dict() for i in items]}
            except Exception as e:
                logger.warning(f"Failed to parse market items: {e}")
        
        return response
    
    def get_top_items(self, count: int = 100, start: int = 0, 
                      sort_column: str = "popular", sort_dir: str = "desc") -> APIResponse:
        """
        Get top items from the Steam Community Market.
        
        Args:
            count: Number of items to return (max 100)
            start: Starting position for pagination
            sort_column: Column to sort by (popular, quantity, price, name)
            sort_dir: Sort direction (desc, asc)
            
        Returns:
            APIResponse with top items or error
        """
        if count <= 0 or count > 100:
            return APIResponse(
                ok=False,
                source="steam_community",
                data={},
                warnings=["Invalid count"],
                error={"message": "Count must be between 1 and 100"}
            )
        
        if sort_column not in ["popular", "quantity", "price", "name"]:
            return APIResponse(
                ok=False,
                source="steam_community",
                data={},
                warnings=["Invalid sort column"],
                error={"message": "Sort column must be one of: popular, quantity, price, name"}
            )
        
        if sort_dir not in ["desc", "asc"]:
            return APIResponse(
                ok=False,
                source="steam_community",
                data={},
                warnings=["Invalid sort direction"],
                error={"message": "Sort direction must be one of: desc, asc"}
            )
        
        url = f"{self.client.STEAM_COMMUNITY_BASE}/market/search/render"
        params = {
            "norender": 1,
            "start": start,
            "count": count,
            "sort_column": sort_column,
            "sort_dir": sort_dir,
        }
        
        response = self.client.get(url, params=params)
        
        # Normalize the response
        if response.ok:
            try:
                items = MarketItem.from_api_response(response.data)
                response.data = {"items": [i.to_dict() for i in items]}
            except Exception as e:
                logger.warning(f"Failed to parse top items: {e}")
        
        return response
    
    def get_item_price_history(self, appid: Union[str, int], market_hash_name: str) -> APIResponse:
        """
        Get price history for a specific market item.
        
        Args:
            appid: App ID of the game
            market_hash_name: Market hash name of the item
            
        Returns:
            APIResponse with price history data or error
        """
        appid = AppID.validate(appid).appid
        
        if not market_hash_name:
            return APIResponse(
                ok=False,
                source="steam_community",
                data={},
                warnings=["Empty market hash name"],
                error={"message": "Market hash name cannot be empty"}
            )
        
        # URL encode the market hash name
        encoded_name = urllib.parse.quote(market_hash_name)
        
        url = f"{self.client.STEAM_COMMUNITY_BASE}/market/pricehistory"
        params = {"appid": appid, "market_hash_name": encoded_name}
        
        response = self.client.get(url, params=params)
        
        # Normalize the response
        if response.ok:
            try:
                price_history = PriceHistory.from_api_response(response.data)
                response.data = {"price_history": price_history.to_dict()}
            except Exception as e:
                logger.warning(f"Failed to parse price history: {e}")
        
        return response
    
    def get_item_price_overview(self, appid: Union[str, int], market_hash_name: str,
                                currency: int = 1) -> APIResponse:
        """
        Get current price overview for a specific market item.
        
        Args:
            appid: App ID of the game
            market_hash_name: Market hash name of the item
            currency: Currency ID (1 = USD, 2 = GBP, 3 = EUR, etc.)
            
        Returns:
            APIResponse with price overview data or error
        """
        appid = AppID.validate(appid).appid
        
        if not market_hash_name:
            return APIResponse(
                ok=False,
                source="steam_community",
                data={},
                warnings=["Empty market hash name"],
                error={"message": "Market hash name cannot be empty"}
            )
        
        # URL encode the market hash name
        encoded_name = urllib.parse.quote(market_hash_name)
        
        url = f"{self.client.STEAM_COMMUNITY_BASE}/market/priceoverview"
        params = {"appid": appid, "currency": currency, "market_hash_name": encoded_name}
        
        response = self.client.get(url, params=params)
        
        # Normalize the response
        if response.ok:
            try:
                price_overview = PriceOverview.from_api_response(response.data)
                response.data = {"price_overview": price_overview.to_dict()}
            except Exception as e:
                logger.warning(f"Failed to parse price overview: {e}")
        
        return response
    
    def get_popular_items(self, count: int = 10) -> APIResponse:
        """
        Get popular items from the Steam Community Market.
        
        Args:
            count: Number of items to return (max 100)
            
        Returns:
            APIResponse with popular items data or error
        """
        if count <= 0 or count > 100:
            return APIResponse(
                ok=False,
                source="steam_community",
                data={},
                warnings=["Invalid count"],
                error={"message": "Count must be between 1 and 100"}
            )
        
        url = f"{self.client.STEAM_COMMUNITY_BASE}/market/popular"
        params = {"count": count, "language": "english", "currency": 1, "format": "json"}
        
        response = self.client.get(url, params=params)
        
        # Normalize the response
        if response.ok:
            try:
                items = MarketItem.from_api_response(response.data)
                response.data = {"items": [i.to_dict() for i in items]}
            except Exception as e:
                logger.warning(f"Failed to parse popular items: {e}")
        
        return response
    
    def get_recent_activity(self, appid: Optional[int] = None, count: int = 10) -> APIResponse:
        """
        Get recent activity from the Steam Community Market.
        
        Args:
            appid: Filter by app ID (optional)
            count: Number of items to return (max 100)
            
        Returns:
            APIResponse with recent activity data or error
        """
        if count <= 0 or count > 100:
            return APIResponse(
                ok=False,
                source="steam_community",
                data={},
                warnings=["Invalid count"],
                error={"message": "Count must be between 1 and 100"}
            )
        
        url = f"{self.client.STEAM_COMMUNITY_BASE}/market/recent"
        params = {"count": count, "language": "english", "currency": 1, "format": "json"}
        
        if appid is not None:
            params["appid"] = appid
        
        response = self.client.get(url, params=params)
        return response
    
    def get_item_listings(self, appid: Union[str, int], market_hash_name: str,
                         currency: int = 1, start: int = 0, count: int = 10) -> APIResponse:
        """
        Get current listings for a specific market item.
        
        Args:
            appid: App ID of the game
            market_hash_name: Market hash name of the item
            currency: Currency ID (1 = USD, 2 = GBP, 3 = EUR, etc.)
            start: Starting position for pagination
            count: Number of listings to return
            
        Returns:
            APIResponse with item listings data or error
        """
        appid = AppID.validate(appid).appid
        
        if not market_hash_name:
            return APIResponse(
                ok=False,
                source="steam_community",
                data={},
                warnings=["Empty market hash name"],
                error={"message": "Market hash name cannot be empty"}
            )
        
        if count <= 0 or count > 100:
            return APIResponse(
                ok=False,
                source="steam_community",
                data={},
                warnings=["Invalid count"],
                error={"message": "Count must be between 1 and 100"}
            )
        
        # URL encode the market hash name
        encoded_name = urllib.parse.quote(market_hash_name)
        
        url = f"{self.client.STEAM_COMMUNITY_BASE}/market/listings/{appid}/{encoded_name}/render"
        params = {"currency": currency, "start": start, "count": count}
        
        response = self.client.get(url, params=params)
        return response
    
    def get_item_orders_histogram(self, item_nameid: str, currency: int = 1) -> APIResponse:
        """
        Get buy and sell order histogram for a specific market item.
        
        Args:
            item_nameid: Internal name ID of the item
            currency: Currency ID (1 = USD, 2 = GBP, 3 = EUR, etc.)
            
        Returns:
            APIResponse with orders histogram data or error
        """
        if not item_nameid or not isinstance(item_nameid, str):
            return APIResponse(
                ok=False,
                source="steam_community",
                data={},
                warnings=["Invalid item name ID"],
                error={"message": "Item name ID must be a non-empty string"}
            )
        
        url = f"{self.client.STEAM_COMMUNITY_BASE}/market/itemordershistogram"
        params = {
            "country": "US",
            "language": "english",
            "currency": currency,
            "item_nameid": item_nameid,
            "two_factor": 0,
        }
        
        response = self.client.get(url, params=params)
        return response
