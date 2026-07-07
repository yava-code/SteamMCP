"""
Steam Wishlist integration.

This module provides functionality for:
- Managing user wishlists
- Adding/removing games from wishlist
- Checking wishlist status
- Getting wishlist details
- Prioritizing wishlist items
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from steam.client import SteamClient, APIResponse
from steam.schemas import AppID, SteamID
from steam.cache import app_cache

logger = logging.getLogger(__name__)


@dataclass
class WishlistItem:
    """Represents an item in a Steam wishlist."""
    appid: int
    name: str
    capsule: Optional[str] = None
    logo: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    is_free: bool = False
    priority: int = 0  # 0 = none, 1 = low, 2 = medium, 3 = high
    added_date: Optional[int] = None
    is_on_sale: bool = False
    discount_percent: Optional[int] = None
    
    @classmethod
    def from_api_data(cls, data: Dict[str, Any]) -> 'WishlistItem':
        """Create WishlistItem from Steam API data."""
        appid = data.get("appid", 0)
        price_overview = data.get("price_overview", {})
        
        # Handle price - if final is 0 and initial is 0, it's free
        final_price = price_overview.get("final", 0)
        initial_price = price_overview.get("initial", 0)
        
        # Price is in cents, convert to dollars
        price = (final_price / 100.0) if final_price is not None and final_price > 0 else 0.0
        is_free = initial_price == 0 if price_overview else False
        
        return cls(
            appid=appid,
            name=data.get("name", f"App {appid}"),
            capsule=data.get("capsule"),
            logo=data.get("logo"),
            price=price,
            currency=price_overview.get("currency", "USD"),
            is_free=is_free,
            priority=data.get("priority", 0),
            added_date=data.get("added_date", 0),
            is_on_sale=price_overview.get("discount_percent", 0) > 0 if price_overview else False,
            discount_percent=price_overview.get("discount_percent")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "appid": self.appid,
            "name": self.name,
            "capsule": self.capsule,
            "logo": self.logo,
            "price": self.price,
            "currency": self.currency,
            "is_free": self.is_free,
            "priority": self.priority,
            "added_date": self.added_date,
            "is_on_sale": self.is_on_sale,
            "discount_percent": self.discount_percent
        }


@dataclass
class Wishlist:
    """Represents a Steam user's wishlist."""
    steamid: str
    items: List[WishlistItem] = field(default_factory=list)
    total_items: int = 0
    total_price: float = 0.0
    currency: str = "USD"
    
    def add_item(self, item: WishlistItem) -> None:
        """Add an item to the wishlist."""
        # Remove existing item with same appid
        self.items = [i for i in self.items if i.appid != item.appid]
        self.items.append(item)
        self._update_stats()
    
    def remove_item(self, appid: int) -> bool:
        """Remove an item from the wishlist."""
        initial_count = len(self.items)
        self.items = [i for i in self.items if i.appid != appid]
        self._update_stats()
        return len(self.items) < initial_count
    
    def get_item(self, appid: int) -> Optional[WishlistItem]:
        """Get a specific item from the wishlist."""
        for item in self.items:
            if item.appid == appid:
                return item
        return None
    
    def has_item(self, appid: int) -> bool:
        """Check if an app is in the wishlist."""
        return self.get_item(appid) is not None
    
    def get_on_sale_items(self) -> List[WishlistItem]:
        """Get items that are currently on sale."""
        return [item for item in self.items if item.is_on_sale]
    
    def get_by_priority(self, priority: int) -> List[WishlistItem]:
        """Get items by priority level."""
        return [item for item in self.items if item.priority == priority]
    
    def _update_stats(self) -> None:
        """Update wishlist statistics."""
        self.total_items = len(self.items)
        self.total_price = sum(
            item.price for item in self.items if item.price is not None
        )
        # Determine dominant currency
        currencies = [item.currency for item in self.items if item.currency]
        if currencies:
            self.currency = currencies[0]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "steamid": self.steamid,
            "total_items": self.total_items,
            "total_price": self.total_price,
            "currency": self.currency,
            "items": [item.to_dict() for item in self.items],
            "on_sale_count": len(self.get_on_sale_items())
        }


class WishlistManager:
    """
    Manage Steam user wishlists.
    
    Features:
    - Get user wishlist
    - Add/remove items from wishlist
    - Check if app is in wishlist
    - Get wishlist statistics
    - Filter wishlist by priority or sale status
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the wishlist manager."""
        self.client = SteamClient(api_key=api_key)
        self._wishlists: Dict[str, Wishlist] = {}
        self._cache_ttl = 1800  # 30 minutes cache
    
    def get_wishlist(self, steam_id: str) -> APIResponse:
        """
        Get a user's wishlist.
        
        Args:
            steam_id: Steam ID or vanity URL
            
        Returns:
            APIResponse with wishlist data
        """
        steam_id = SteamID.validate(steam_id).steamid
        cache_key = f"wishlist:{steam_id}"
        
        # Check cache
        cached = app_cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Get wishlist from Steam
        url = f"{self.client.STEAM_STORE_API_BASE}/wishlist"
        params = {"steamid": steam_id, "l": "english"}
        
        response = self.client.get(url, params=params)
        
        if response.ok:
            wishlist_data = response.data
            wishlist = self._parse_wishlist_data(steam_id, wishlist_data)
            response.data = {"wishlist": wishlist.to_dict()}
            response.summary = f"Wishlist for {steam_id}: {wishlist.total_items} items"
            
            # Cache
            app_cache.set(cache_key, response, ttl=self._cache_ttl)
        
        return response
    
    def _parse_wishlist_data(self, steam_id: str, data: Dict[str, Any]) -> Wishlist:
        """Parse wishlist data from Steam API response."""
        wishlist = Wishlist(steamid=steam_id)
        
        # Steam wishlist data structure can vary
        # Try different possible structures
        items_data = []
        
        # Structure 1: Direct list of items
        if isinstance(data, list):
            items_data = data
        # Structure 2: Nested in "items" or "wishlist" key
        elif isinstance(data, dict):
            if "items" in data:
                items_data = data["items"]
            elif "wishlist" in data:
                items_data = data["wishlist"]
            elif "response" in data and "items" in data["response"]:
                items_data = data["response"]["items"]
        
        # Parse items
        for item_data in items_data:
            if isinstance(item_data, dict):
                try:
                    item = WishlistItem.from_api_data(item_data)
                    wishlist.add_item(item)
                except Exception as e:
                    logger.warning(f"Failed to parse wishlist item: {e}")
        
        return wishlist
    
    def add_to_wishlist(self, steam_id: str, app_id: Union[str, int]) -> APIResponse:
        """
        Add an app to a user's wishlist.
        
        Note: This requires the user to be logged in with a session cookie.
        For public use, this may not work without proper authentication.
        
        Args:
            steam_id: Steam ID
            app_id: Application ID to add
            
        Returns:
            APIResponse with operation result
        """
        steam_id = SteamID.validate(steam_id).steamid
        app_id = AppID.validate(app_id).appid
        
        # Note: Adding to wishlist requires POST request with session
        # This is a placeholder - actual implementation would need session handling
        
        return APIResponse(
            ok=False,
            source="wishlist_manager",
            data={},
            warnings=["Adding to wishlist requires authenticated session"],
            error={"message": "Not implemented - requires Steam session"}
        )
    
    def remove_from_wishlist(self, steam_id: str, app_id: Union[str, int]) -> APIResponse:
        """
        Remove an app from a user's wishlist.
        
        Note: This requires the user to be logged in with a session cookie.
        
        Args:
            steam_id: Steam ID
            app_id: Application ID to remove
            
        Returns:
            APIResponse with operation result
        """
        steam_id = SteamID.validate(steam_id).steamid
        app_id = AppID.validate(app_id).appid
        
        # Note: Removing from wishlist requires POST request with session
        
        return APIResponse(
            ok=False,
            source="wishlist_manager",
            data={},
            warnings=["Removing from wishlist requires authenticated session"],
            error={"message": "Not implemented - requires Steam session"}
        )
    
    def check_in_wishlist(self, steam_id: str, app_id: Union[str, int]) -> APIResponse:
        """
        Check if an app is in a user's wishlist.
        
        Args:
            steam_id: Steam ID
            app_id: Application ID to check
            
        Returns:
            APIResponse with boolean result
        """
        steam_id = SteamID.validate(steam_id).steamid
        app_id = AppID.validate(app_id).appid
        
        # Get wishlist first
        wishlist_response = self.get_wishlist(steam_id)
        
        if not wishlist_response.ok:
            return wishlist_response
        
        wishlist_data = wishlist_response.data.get("wishlist", {})
        items = wishlist_data.get("items", [])
        
        is_in_wishlist = any(item.get("appid") == app_id for item in items)
        
        response = APIResponse(
            ok=True,
            source="wishlist_manager",
            data={"in_wishlist": is_in_wishlist, "appid": app_id},
            summary=f"App {app_id} {'is' if is_in_wishlist else 'is not'} in {steam_id}'s wishlist"
        )
        
        return response
    
    def get_wishlist_stats(self, steam_id: str) -> APIResponse:
        """
        Get statistics about a user's wishlist.
        
        Args:
            steam_id: Steam ID
            
        Returns:
            APIResponse with wishlist statistics
        """
        steam_id = SteamID.validate(steam_id).steamid
        
        wishlist_response = self.get_wishlist(steam_id)
        
        if not wishlist_response.ok:
            return wishlist_response
        
        wishlist_data = wishlist_response.data.get("wishlist", {})
        items = wishlist_data.get("items", [])
        
        total_items = len(items)
        total_price = sum(item.get("price", 0) for item in items if item.get("price"))
        on_sale_count = sum(1 for item in items if item.get("is_on_sale", False))
        
        # Count by priority
        priorities = {0: 0, 1: 0, 2: 0, 3: 0}
        for item in items:
            priority = item.get("priority", 0)
            priorities[priority] = priorities.get(priority, 0) + 1
        
        response = APIResponse(
            ok=True,
            source="wishlist_manager",
            data={
                "total_items": total_items,
                "total_price": total_price,
                "currency": wishlist_data.get("currency", "USD"),
                "on_sale_count": on_sale_count,
                "priority_distribution": priorities
            },
            summary=f"Wishlist stats: {total_items} items, {on_sale_count} on sale"
        )
        
        return response
    
    def get_wishlist_on_sale(self, steam_id: str) -> APIResponse:
        """
        Get items from a user's wishlist that are currently on sale.
        
        Args:
            steam_id: Steam ID
            
        Returns:
            APIResponse with list of on-sale items
        """
        steam_id = SteamID.validate(steam_id).steamid
        
        wishlist_response = self.get_wishlist(steam_id)
        
        if not wishlist_response.ok:
            return wishlist_response
        
        wishlist_data = wishlist_response.data.get("wishlist", {})
        items = wishlist_data.get("items", [])
        
        on_sale_items = [item for item in items if item.get("is_on_sale", False)]
        
        # Sort by discount percent (highest first)
        on_sale_items.sort(key=lambda x: x.get("discount_percent", 0), reverse=True)
        
        response = APIResponse(
            ok=True,
            source="wishlist_manager",
            data={
                "steamid": steam_id,
                "on_sale_items": on_sale_items,
                "count": len(on_sale_items)
            },
            summary=f"{len(on_sale_items)} items on sale in {steam_id}'s wishlist"
        )
        
        return response
