"""
Steam Inventory management.

This module provides functionality for:
- Managing user inventory
- Getting inventory items
- Filtering inventory by type
- Checking item details
- Inventory statistics
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from steam.client import SteamClient, APIResponse
from steam.schemas import AppID, SteamID
from steam.cache import app_cache

logger = logging.getLogger(__name__)


@dataclass
class InventoryItem:
    """Represents an item in a Steam inventory."""
    assetid: str
    appid: int
    contextid: str
    classid: str
    instanceid: str
    amount: int = 1
    name: Optional[str] = None
    type: Optional[str] = None
    market_name: Optional[str] = None
    market_hash_name: Optional[str] = None
    icon_url: Optional[str] = None
    icon_drag_url: Optional[str] = None
    tradable: bool = False
    marketable: bool = False
    commodity: bool = False
    price: Optional[float] = None
    currency: Optional[str] = None
    
    @classmethod
    def from_api_data(cls, data: Dict[str, Any], appid: int) -> 'InventoryItem':
        """Create InventoryItem from Steam API data."""
        # Extract price from market data if available
        price_data = data.get("price_data", {})
        price = None
        currency = None
        
        if price_data:
            # Price might be in different formats
            if isinstance(price_data, dict):
                price_cents = price_data.get("price_in_cents") or price_data.get("price")
                if price_cents:
                    price = float(price_cents) / 100.0
                currency = price_data.get("currency", "USD")
        
        # Get tradable/marketable from tags
        tags = data.get("tags", [])
        tradable = any(tag.get("tag") == "tradable" for tag in tags if isinstance(tag, dict))
        marketable = any(tag.get("tag") == "marketable" for tag in tags if isinstance(tag, dict))
        commodity = any(tag.get("tag") == "commodity" for tag in tags if isinstance(tag, dict))
        
        # Get descriptive data
        descriptions = data.get("descriptions", [])
        name = None
        type_name = None
        market_name = None
        market_hash_name = None
        icon_url = None
        icon_drag_url = None
        
        for desc in descriptions:
            if isinstance(desc, dict):
                if desc.get("type") == "html":
                    # Skip HTML descriptions
                    continue
                desc_name = desc.get("name", "").lower()
                value = desc.get("value", "")
                
                # Check exact name matches first
                if desc_name == "name":
                    name = value
                elif desc_name == "type":
                    type_name = value
                elif desc_name == "market_name":
                    market_name = value
                elif desc_name == "market_hash_name":
                    market_hash_name = value
                elif desc_name == "icon_url":
                    icon_url = value
                elif desc_name == "icon_drag_url":
                    icon_drag_url = value
                # Fallback for name in market_name field
                elif name is None and desc_name == "market_name":
                    name = value
        
        # If no name from descriptions, try to get from app data
        if not name and "name" in data:
            name = data["name"]
        
        return cls(
            assetid=data.get("assetid", ""),
            appid=appid,
            contextid=data.get("contextid", ""),
            classid=data.get("classid", ""),
            instanceid=data.get("instanceid", ""),
            amount=data.get("amount", 1),
            name=name,
            type=type_name,
            market_name=market_name,
            market_hash_name=market_hash_name,
            icon_url=icon_url,
            icon_drag_url=icon_drag_url,
            tradable=tradable,
            marketable=marketable,
            commodity=commodity,
            price=price,
            currency=currency
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "assetid": self.assetid,
            "appid": self.appid,
            "contextid": self.contextid,
            "classid": self.classid,
            "instanceid": self.instanceid,
            "amount": self.amount,
            "name": self.name,
            "type": self.type,
            "market_name": self.market_name,
            "market_hash_name": self.market_hash_name,
            "icon_url": self.icon_url,
            "icon_drag_url": self.icon_drag_url,
            "tradable": self.tradable,
            "marketable": self.marketable,
            "commodity": self.commodity,
            "price": self.price,
            "currency": self.currency
        }


@dataclass
class Inventory:
    """Represents a Steam user's inventory for a specific app."""
    steamid: str
    appid: int
    items: List[InventoryItem] = field(default_factory=list)
    total_items: int = 0
    total_value: float = 0.0
    currency: str = "USD"
    
    def add_item(self, item: InventoryItem) -> None:
        """Add an item to the inventory."""
        # Check if item already exists (by assetid)
        existing = next((i for i in self.items if i.assetid == item.assetid), None)
        if existing:
            existing.amount = item.amount
        else:
            self.items.append(item)
        self._update_stats()
    
    def remove_item(self, assetid: str) -> bool:
        """Remove an item from the inventory."""
        initial_count = len(self.items)
        self.items = [i for i in self.items if i.assetid != assetid]
        self._update_stats()
        return len(self.items) < initial_count
    
    def get_item(self, assetid: str) -> Optional[InventoryItem]:
        """Get a specific item from the inventory."""
        for item in self.items:
            if item.assetid == assetid:
                return item
        return None
    
    def get_by_appid(self, appid: int) -> List[InventoryItem]:
        """Get all items for a specific app."""
        return [item for item in self.items if item.appid == appid]
    
    def get_tradable(self) -> List[InventoryItem]:
        """Get all tradable items."""
        return [item for item in self.items if item.tradable]
    
    def get_marketable(self) -> List[InventoryItem]:
        """Get all marketable items."""
        return [item for item in self.items if item.marketable]
    
    def get_by_type(self, item_type: str) -> List[InventoryItem]:
        """Get items by type."""
        return [item for item in self.items if item.type and item_type.lower() in item.type.lower()]
    
    def _update_stats(self) -> None:
        """Update inventory statistics."""
        self.total_items = sum(item.amount for item in self.items)
        self.total_value = sum(
            (item.price or 0) * item.amount for item in self.items
        )
        # Determine dominant currency
        currencies = [item.currency for item in self.items if item.currency]
        if currencies:
            self.currency = currencies[0]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "steamid": self.steamid,
            "appid": self.appid,
            "total_items": self.total_items,
            "total_value": self.total_value,
            "currency": self.currency,
            "items": [item.to_dict() for item in self.items],
            "tradable_count": len(self.get_tradable()),
            "marketable_count": len(self.get_marketable())
        }


class InventoryManager:
    """
    Manage Steam user inventories.
    
    Features:
    - Get user inventory for specific apps
    - List all inventory apps
    - Filter inventory items
    - Get inventory statistics
    - Search inventory
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the inventory manager."""
        self.client = SteamClient(api_key=api_key)
        self._inventories: Dict[str, Dict[int, Inventory]] = {}  # steamid -> {appid -> Inventory}
        self._cache_ttl = 300  # 5 minutes cache for inventory data
    
    def get_inventory(self, steam_id: str, app_id: Union[str, int], 
                     context_id: Optional[str] = None) -> APIResponse:
        """
        Get a user's inventory for a specific app.
        
        Args:
            steam_id: Steam ID
            app_id: Application ID
            context_id: Optional context ID (default: 2 for most games)
            
        Returns:
            APIResponse with inventory data
        """
        steam_id = SteamID.validate(steam_id).steamid
        app_id = AppID.validate(app_id).appid
        
        if context_id is None:
            context_id = "2"  # Default context for most games
        
        cache_key = f"inventory:{steam_id}:{app_id}:{context_id}"
        
        # Check cache
        cached = app_cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Get inventory from Steam
        url = f"{self.client.STEAM_API_BASE}/ISteamEconomy/GetInventory/v1/"
        params = {
            "key": self.client.api_key,
            "steamid": steam_id,
            "appid": app_id,
            "contextid": context_id,
            "l": "english",
            "count": 5000  # Max items per request
        }
        
        response = self.client.get(url, params=params)
        
        if response.ok:
            inventory_data = response.data
            inventory = self._parse_inventory_data(steam_id, app_id, inventory_data)
            response.data = {"inventory": inventory.to_dict()}
            response.summary = f"Inventory for {steam_id}: App {app_id}, {inventory.total_items} items"
            
            # Cache
            app_cache.set(cache_key, response, ttl=self._cache_ttl)
        
        return response
    
    def _parse_inventory_data(self, steam_id: str, app_id: int, data: Dict[str, Any]) -> Inventory:
        """Parse inventory data from Steam API response."""
        inventory = Inventory(steamid=steam_id, appid=app_id)
        
        # Steam inventory response structure
        # {"assets": [...], "descriptions": [...], "total_inventory_count": N}
        
        assets = data.get("assets", [])
        descriptions = data.get("descriptions", [])
        
        # Create lookup for descriptions by classid+instanceid
        desc_lookup = {}
        for desc in descriptions:
            if isinstance(desc, dict):
                key = f"{desc.get('classid')}_{desc.get('instanceid')}"
                desc_lookup[key] = desc
        
        # Parse assets
        for asset in assets:
            if isinstance(asset, dict):
                classid = asset.get("classid", "")
                instanceid = asset.get("instanceid", "")
                key = f"{classid}_{instanceid}"
                
                # Get description for this asset
                desc = desc_lookup.get(key, {})
                
                # Merge asset and description data
                item_data = {**asset, **desc}
                
                try:
                    item = InventoryItem.from_api_data(item_data, app_id)
                    inventory.add_item(item)
                except Exception as e:
                    logger.warning(f"Failed to parse inventory item: {e}")
        
        return inventory
    
    def list_inventory_apps(self, steam_id: str) -> APIResponse:
        """
        List all apps for which a user has inventory.
        
        Note: This requires the user's profile to be public or authenticated access.
        
        Args:
            steam_id: Steam ID
            
        Returns:
            APIResponse with list of app IDs
        """
        steam_id = SteamID.validate(steam_id).steamid
        
        # Note: Steam doesn't provide a direct endpoint to list all inventory apps
        # This is a placeholder - would require iterating through known apps
        # or using the Steam Community API
        
        # For now, return common apps with inventory
        common_inventory_apps = [
            730,    # CS:GO
            570,    # Dota 2
            440,    # Team Fortress 2
            753,    # Steam
        ]
        
        return APIResponse(
            ok=True,
            source="inventory_manager",
            data={
                "steamid": steam_id,
                "inventory_apps": common_inventory_apps,
                "note": "This is a placeholder - full inventory app listing requires additional API access"
            },
            summary=f"Common inventory apps for {steam_id}"
        )
    
    def get_inventory_stats(self, steam_id: str, app_id: Union[str, int]) -> APIResponse:
        """
        Get statistics about a user's inventory for a specific app.
        
        Args:
            steam_id: Steam ID
            app_id: Application ID
            
        Returns:
            APIResponse with inventory statistics
        """
        steam_id = SteamID.validate(steam_id).steamid
        app_id = AppID.validate(app_id).appid
        
        inventory_response = self.get_inventory(steam_id, app_id)
        
        if not inventory_response.ok:
            return inventory_response
        
        inventory_data = inventory_response.data.get("inventory", {})
        items = inventory_data.get("items", [])
        
        total_items = inventory_data.get("total_items", 0)
        total_value = inventory_data.get("total_value", 0.0)
        tradable_count = inventory_data.get("tradable_count", 0)
        marketable_count = inventory_data.get("marketable_count", 0)
        
        # Count by type
        type_distribution = {}
        for item in items:
            item_type = item.get("type", "Unknown")
            type_distribution[item_type] = type_distribution.get(item_type, 0) + item.get("amount", 1)
        
        response = APIResponse(
            ok=True,
            source="inventory_manager",
            data={
                "steamid": steam_id,
                "appid": app_id,
                "total_items": total_items,
                "total_value": total_value,
                "currency": inventory_data.get("currency", "USD"),
                "tradable_count": tradable_count,
                "marketable_count": marketable_count,
                "type_distribution": type_distribution
            },
            summary=f"Inventory stats: {total_items} items, ${total_value:.2f} value"
        )
        
        return response
    
    def search_inventory(self, steam_id: str, app_id: Union[str, int], 
                        search_term: str) -> APIResponse:
        """
        Search a user's inventory for items matching a term.
        
        Args:
            steam_id: Steam ID
            app_id: Application ID
            search_term: Term to search for in item names
            
        Returns:
            APIResponse with matching items
        """
        steam_id = SteamID.validate(steam_id).steamid
        app_id = AppID.validate(app_id).appid
        
        inventory_response = self.get_inventory(steam_id, app_id)
        
        if not inventory_response.ok:
            return inventory_response
        
        inventory_data = inventory_response.data.get("inventory", {})
        items = inventory_data.get("items", [])
        
        # Search in item names
        matching_items = []
        for item in items:
            if isinstance(item, dict):
                name = item.get("name", "").lower()
                market_name = item.get("market_name", "").lower()
                if search_term.lower() in name or search_term.lower() in market_name:
                    matching_items.append(item)
        
        response = APIResponse(
            ok=True,
            source="inventory_manager",
            data={
                "steamid": steam_id,
                "appid": app_id,
                "search_term": search_term,
                "matching_items": matching_items,
                "count": len(matching_items)
            },
            summary=f"Found {len(matching_items)} items matching '{search_term}'"
        )
        
        return response
    
    def get_tradable_items(self, steam_id: str, app_id: Union[str, int]) -> APIResponse:
        """
        Get all tradable items from a user's inventory.
        
        Args:
            steam_id: Steam ID
            app_id: Application ID
            
        Returns:
            APIResponse with tradable items
        """
        steam_id = SteamID.validate(steam_id).steamid
        app_id = AppID.validate(app_id).appid
        
        inventory_response = self.get_inventory(steam_id, app_id)
        
        if not inventory_response.ok:
            return inventory_response
        
        inventory_data = inventory_response.data.get("inventory", {})
        items = inventory_data.get("items", [])
        
        tradable_items = [item for item in items if item.get("tradable", False)]
        
        response = APIResponse(
            ok=True,
            source="inventory_manager",
            data={
                "steamid": steam_id,
                "appid": app_id,
                "tradable_items": tradable_items,
                "count": len(tradable_items)
            },
            summary=f"{len(tradable_items)} tradable items in inventory"
        )
        
        return response
