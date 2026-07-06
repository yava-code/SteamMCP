"""
Steam Store API functions.

This module provides functions for interacting with the Steam Store API:
- App details
- Featured items
- Special offers
- Store highlights
"""

import logging
from typing import Any, Dict, List, Optional, Union

from steam.client import SteamClient, APIResponse
from steam.schemas import AppID

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
