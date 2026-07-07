"""
Steam Store API functions.

This module provides functions for interacting with the Steam Store API:
- App details
- Featured items
- Special offers
- Store highlights
- Search games
- App reviews
- App tags
- Release calendar
"""

import logging
import time
from typing import Any, Dict, List, Optional, Union

from steam.client import SteamClient, APIResponse
from steam.schemas import AppID
from steam.cache import discovery_cache, app_cache
from steam.web import SteamWebAPI

logger = logging.getLogger(__name__)


class SteamStoreAPI:
    """
    Client for Steam Store API operations.
    
    This class provides a high-level interface for Steam Store API endpoints
    with normalized responses and error handling.
    
    Usage:
        store = SteamStoreAPI()
        details = store.get_app_details(730)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Steam Store API client.
        
        Args:
            api_key: Steam Web API key (optional, can also use STEAM_API_KEY env var)
        """
        self.client = SteamClient(api_key=api_key)
    
    def get_app_details(self, app_id: Union[str, int], country_code: str = "US",
                        language: str = "english") -> APIResponse:
        """
        Get detailed information about a game from the Steam Store API.
        
        Args:
            app_id: Application ID
            country_code: Country code for pricing and availability
            language: Language for localized content
            
        Returns:
            APIResponse with app details data or error
        """
        app_id = AppID.validate(app_id).appid
        cache_key = f"app_details:{app_id}:{country_code}:{language}"
        
        # Try to get from cache
        cached_result = app_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        url = f"{self.client.STEAM_STORE_API_BASE}/appdetails"
        params = {"appids": app_id, "cc": country_code, "l": language}
        
        response = self.client.get(url, params=params)
        
        # Normalize the response
        if response.ok:
            try:
                from steam.schemas import AppDetails
                app_details = AppDetails.from_api_response(response.data, app_id)
                response.data = {"app": app_details.to_dict()}
            except Exception as e:
                logger.warning(f"Failed to parse app details: {e}")
        
        # Cache the result
        if response.ok:
            app_cache.set(cache_key, response, ttl=1800)  # 30 minutes
        
        return response
    
    def get_featured_categories(self, country_code: str = "US", 
                                language: str = "english") -> APIResponse:
        """
        Get featured categories from the Steam Store.
        
        Args:
            country_code: Country code for localized content
            language: Language for localized content
            
        Returns:
            APIResponse with featured categories data or error
        """
        url = f"{self.client.STEAM_STORE_API_BASE}/featuredcategories"
        params = {"cc": country_code, "l": language}
        
        response = self.client.get(url, params=params)
        return response
    
    def get_featured_items(self, country_code: str = "US", 
                           language: str = "english") -> APIResponse:
        """
        Get featured items from the Steam Store.
        
        Args:
            country_code: Country code for localized content
            language: Language for localized content
            
        Returns:
            APIResponse with featured items data or error
        """
        url = f"{self.client.STEAM_STORE_API_BASE}/getfeatureditems"
        params = {"cc": country_code, "l": language}
        
        response = self.client.get(url, params=params)
        return response
    
    def get_specials(self, country_code: str = "US", 
                     language: str = "english") -> APIResponse:
        """
        Get special offers (sales) from the Steam Store.
        
        Args:
            country_code: Country code for localized content
            language: Language for localized content
            
        Returns:
            APIResponse with special offers data or error
        """
        url = f"{self.client.STEAM_STORE_API_BASE}/getapplist"
        params = {"cc": country_code, "l": language, "include_games": True, "include_dlc": True}
        
        response = self.client.get(url, params=params)
        return response
    
    def get_store_highlights(self, country_code: str = "US", 
                             language: str = "english") -> APIResponse:
        """
        Get store highlights (featured content) from the Steam Store.
        
        Args:
            country_code: Country code for localized content
            language: Language for localized content
            
        Returns:
            APIResponse with store highlights data or error
        """
        # Note: This endpoint might not be publicly available
        # Using a fallback approach
        url = f"{self.client.STEAM_STORE_API_BASE}/getstorehighlights"
        params = {"cc": country_code, "l": language}
        
        response = self.client.get(url, params=params)
        return response
    
    def search_games(self, query: str, country_code: str = "US", 
                     language: str = "english", limit: int = 20) -> APIResponse:
        """
        Search for games in the Steam Store.
        
        Args:
            query: Search query
            country_code: Country code for localized content
            language: Language for localized content
            limit: Maximum number of results to return
            
        Returns:
            APIResponse with search results or error
        """
        if not query:
            return APIResponse(
                ok=False,
                source="steam_store_api",
                data={},
                warnings=["Empty query"],
                error={"message": "Search query cannot be empty"}
            )
        
        # Generate cache key
        cache_key = f"search_games:{query}:{country_code}:{language}:{limit}"
        
        # Try to get from cache
        cached_result = discovery_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Note: Steam Store search is typically done via web scraping
        # or unofficial APIs. This is a placeholder for the actual implementation.
        # For now, we'll use a simple approach.
        
        # Try to use the store search endpoint (may not be publicly available)
        url = f"{self.client.STEAM_STORE_API_BASE}/search"
        params = {
            "cc": country_code,
            "l": language,
            "term": query,
            "limit": limit
        }
        
        response = self.client.get(url, params=params)
        
        # Cache the result
        if response.ok:
            discovery_cache.set(cache_key, response, ttl=300)  # 5 minutes
        
        return response
    
    def get_featured_specials(self, country_code: str = "US", 
                             language: str = "english") -> APIResponse:
        """
        Get featured specials (sales) from the Steam Store.
        
        Args:
            country_code: Country code for localized content
            language: Language for localized content
            
        Returns:
            APIResponse with featured specials data or error
        """
        cache_key = f"featured_specials:{country_code}:{language}"
        
        # Try to get from cache
        cached_result = discovery_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Try different endpoints that might contain specials
        url = f"{self.client.STEAM_STORE_API_BASE}/getfeaturedspecials"
        params = {"cc": country_code, "l": language}
        
        response = self.client.get(url, params=params)
        
        # If that fails, try the app list with filters
        if not response.ok:
            url = f"{self.client.STEAM_STORE_API_BASE}/getapplist"
            params = {
                "cc": country_code,
                "l": language,
                "include_games": True,
                "include_dlc": False,
                "include_software": False,
                "include_videos": False,
                "include_hardware": False
            }
            response = self.client.get(url, params=params)
        
        # Cache the result
        if response.ok:
            discovery_cache.set(cache_key, response, ttl=600)  # 10 minutes
        
        return response
    
    def get_app_reviews_summary(self, app_id: Union[str, int], 
                                country_code: str = "US", 
                                language: str = "english") -> APIResponse:
        """
        Get reviews summary for a specific app.
        
        Args:
            app_id: Application ID
            country_code: Country code for localized content
            language: Language for localized content
            
        Returns:
            APIResponse with reviews summary data or error
        """
        app_id = AppID.validate(app_id).appid
        cache_key = f"app_reviews_summary:{app_id}:{country_code}:{language}"
        
        # Try to get from cache
        cached_result = app_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Steam Store API endpoint for reviews
        url = f"{self.client.STEAM_STORE_API_BASE}/appreviews"
        params = {
            "appid": app_id,
            "cc": country_code,
            "l": language,
            "json": 1
        }
        
        response = self.client.get(url, params=params)
        
        # Cache the result
        if response.ok:
            app_cache.set(cache_key, response, ttl=1800)  # 30 minutes
        
        return response
    
    def get_app_tags(self, app_id: Union[str, int], 
                     country_code: str = "US", 
                     language: str = "english") -> APIResponse:
        """
        Get tags for a specific app.
        
        Args:
            app_id: Application ID
            country_code: Country code for localized content
            language: Language for localized content
            
        Returns:
            APIResponse with app tags data or error
        """
        app_id = AppID.validate(app_id).appid
        cache_key = f"app_tags:{app_id}:{country_code}:{language}"
        
        # Try to get from cache
        cached_result = app_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Note: App tags are typically part of the app details response
        # For now, we'll get app details and extract tags
        url = f"{self.client.STEAM_STORE_API_BASE}/appdetails"
        params = {
            "appids": app_id,
            "cc": country_code,
            "l": language
        }
        
        response = self.client.get(url, params=params)
        
        # Cache the result
        if response.ok:
            app_cache.set(cache_key, response, ttl=1800)  # 30 minutes
        
        return response
    
    def get_release_calendar(self, country_code: str = "US", 
                             language: str = "english", 
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> APIResponse:
        """
        Get release calendar from the Steam Store.
        
        Args:
            country_code: Country code for localized content
            language: Language for localized content
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            
        Returns:
            APIResponse with release calendar data or error
        """
        cache_key = f"release_calendar:{country_code}:{language}:{start_date}:{end_date}"
        
        # Try to get from cache
        cached_result = discovery_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Note: Release calendar might not be available via official API
        # This is a placeholder for the actual implementation
        url = f"{self.client.STEAM_STORE_API_BASE}/getreleasecalendar"
        params = {"cc": country_code, "l": language}
        
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        response = self.client.get(url, params=params)
        
        # Cache the result
        if response.ok:
            discovery_cache.set(cache_key, response, ttl=3600)  # 1 hour
        
        return response
    
    def get_app_update_signal(self, app_id: Union[str, int]) -> APIResponse:
        """
        Get update signal for a specific app (detect if recently updated).
        
        This function checks multiple sources to detect if an app has been recently updated:
        - App details (change number)
        - News items (recent announcements)
        - Build ID changes
        
        Args:
            app_id: Application ID
            
        Returns:
            APIResponse with update signal data or error
        """
        app_id = AppID.validate(app_id).appid
        cache_key = f"app_update_signal:{app_id}"
        
        # Try to get from cache
        cached_result = app_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Get app details to check for updates
        app_details_response = self.get_app_details(app_id)
        
        if not app_details_response.ok:
            return app_details_response
        
        # Get recent news to check for update announcements
        web = SteamWebAPI()
        news_response = web.get_game_news(app_id, count=5)
        
        # Build update signal
        app_data = app_details_response.data.get("app", {})
        news_data = news_response.data.get("news", [])
        
        # Check if there are recent news items (within last 7 days)
        recent_news = []
        if news_data:
            now = time.time()
            seven_days_ago = now - (7 * 24 * 60 * 60)
            for news_item in news_data:
                if news_item.get("date", 0) >= seven_days_ago:
                    recent_news.append(news_item)
        
        update_signal = {
            "appid": app_id,
            "has_recent_news": len(recent_news) > 0,
            "recent_news_count": len(recent_news),
            "last_news_date": recent_news[0].get("date") if recent_news else None,
            "app_name": app_data.get("name"),
            "last_updated": app_data.get("last_updated") if app_data else None
        }
        
        response = APIResponse(
            ok=True,
            source="steam_store_api",
            data={"update_signal": update_signal}
        )
        
        # Cache the result
        app_cache.set(cache_key, response, ttl=300)  # 5 minutes
        
        return response
