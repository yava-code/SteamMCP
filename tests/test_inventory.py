"""
Tests for the Inventory module.

These tests verify:
- Inventory data structures
- Inventory parsing
- Inventory operations
- Error handling
"""

import pytest
from unittest.mock import patch, Mock

from steam.inventory import InventoryManager, Inventory, InventoryItem
from steam.client import APIResponse


class TestInventoryItem:
    """Test InventoryItem dataclass."""
    
    def test_inventory_item_creation(self):
        """Test InventoryItem creation from API data."""
        # Steam API returns descriptions as a list of dicts with name/value
        data = {
            "assetid": "1234567890",
            "classid": "100",
            "instanceid": "0",
            "contextid": "2",
            "amount": 1,
            "tags": [
                {"tag": "tradable"},
                {"tag": "marketable"}
            ],
            "price_data": {
                "price_in_cents": 1500,
                "currency": "USD"
            },
            "descriptions": [
                {"name": "name", "value": "AK-47 | Vulcan (Minimal Wear)", "type": "text"},
                {"name": "type", "value": "Covert Rifle", "type": "text"},
                {"name": "market_name", "value": "AK-47 | Vulcan (Minimal Wear)", "type": "text"},
                {"name": "market_hash_name", "value": "AK-47 | Vulcan (Minimal Wear)", "type": "text"},
                {"name": "icon_url", "value": "https://icon.url", "type": "text"},
                {"name": "icon_drag_url", "value": "https://drag.url", "type": "text"}
            ]
        }
        
        item = InventoryItem.from_api_data(data, 730)
        
        assert item.assetid == "1234567890"
        assert item.appid == 730
        assert item.contextid == "2"
        assert item.classid == "100"
        assert item.instanceid == "0"
        assert item.amount == 1
        assert item.name == "AK-47 | Vulcan (Minimal Wear)"
        assert item.type == "Covert Rifle"
        assert item.market_name == "AK-47 | Vulcan (Minimal Wear)"
        assert item.market_hash_name == "AK-47 | Vulcan (Minimal Wear)"
        assert item.icon_url == "https://icon.url"
        assert item.icon_drag_url == "https://drag.url"
        assert item.tradable is True
        assert item.marketable is True
        assert item.commodity is False
        assert item.price == 15.0
        assert item.currency == "USD"
    
    def test_inventory_item_non_tradable(self):
        """Test InventoryItem for non-tradable item."""
        data = {
            "assetid": "1234567891",
            "classid": "101",
            "instanceid": "0",
            "tags": [
                {"tag": "non_tradable"}
            ]
        }
        
        item = InventoryItem.from_api_data(data, 730)
        
        assert item.tradable is False
        assert item.marketable is False
    
    def test_inventory_item_commodity(self):
        """Test InventoryItem for commodity item."""
        data = {
            "assetid": "1234567892",
            "classid": "102",
            "instanceid": "0",
            "tags": [
                {"tag": "commodity"}
            ]
        }
        
        item = InventoryItem.from_api_data(data, 730)
        
        assert item.commodity is True
    
    def test_inventory_item_to_dict(self):
        """Test InventoryItem serialization."""
        data = {
            "assetid": "1234567890",
            "classid": "100",
            "instanceid": "0",
            "contextid": "2",
            "descriptions": [
                {"name": "name", "value": "Test Item", "type": "text"},
                {"name": "type", "value": "Test Type", "type": "text"}
            ]
        }
        
        item = InventoryItem.from_api_data(data, 730)
        item_dict = item.to_dict()
        
        assert item_dict["assetid"] == "1234567890"
        assert item_dict["appid"] == 730
        assert item_dict["name"] == "Test Item"
        assert item_dict["type"] == "Test Type"


class TestInventory:
    """Test Inventory dataclass."""
    
    def test_inventory_creation(self):
        """Test Inventory creation."""
        inventory = Inventory(steamid="76561198006409530", appid=730)
        
        assert inventory.steamid == "76561198006409530"
        assert inventory.appid == 730
        assert len(inventory.items) == 0
        assert inventory.total_items == 0
        assert inventory.total_value == 0.0
    
    def test_add_item(self):
        """Test adding items to inventory."""
        inventory = Inventory(steamid="76561198006409530", appid=730)
        
        item1 = InventoryItem(
            assetid="1234567890",
            appid=730,
            contextid="2",
            classid="100",
            instanceid="0",
            amount=1,
            name="Item 1",
            price=10.0,
            currency="USD"
        )
        
        item2 = InventoryItem(
            assetid="1234567891",
            appid=730,
            contextid="2",
            classid="101",
            instanceid="0",
            amount=2,
            name="Item 2",
            price=5.0,
            currency="USD"
        )
        
        inventory.add_item(item1)
        inventory.add_item(item2)
        
        assert inventory.total_items == 3  # 1 + 2
        assert inventory.total_value == 20.0  # 10 + 5*2
        assert inventory.currency == "USD"
    
    def test_remove_item(self):
        """Test removing items from inventory."""
        inventory = Inventory(steamid="76561198006409530", appid=730)
        
        item = InventoryItem(
            assetid="1234567890",
            appid=730,
            contextid="2",
            classid="100",
            instanceid="0",
            amount=1,
            name="Item 1",
            price=10.0
        )
        inventory.add_item(item)
        
        assert inventory.total_items == 1
        
        removed = inventory.remove_item("1234567890")
        assert removed is True
        assert inventory.total_items == 0
        
        # Try to remove non-existent item
        removed = inventory.remove_item("9999999999")
        assert removed is False
    
    def test_get_item(self):
        """Test getting specific item from inventory."""
        inventory = Inventory(steamid="76561198006409530", appid=730)
        
        item = InventoryItem(
            assetid="1234567890",
            appid=730,
            contextid="2",
            classid="100",
            instanceid="0",
            name="Item 1"
        )
        inventory.add_item(item)
        
        retrieved = inventory.get_item("1234567890")
        assert retrieved is not None
        assert retrieved.assetid == "1234567890"
        
        not_found = inventory.get_item("9999999999")
        assert not_found is None
    
    def test_get_tradable(self):
        """Test filtering tradable items."""
        inventory = Inventory(steamid="76561198006409530", appid=730)
        
        item1 = InventoryItem(
            assetid="1234567890",
            appid=730,
            contextid="2",
            classid="100",
            instanceid="0",
            tradable=True
        )
        
        item2 = InventoryItem(
            assetid="1234567891",
            appid=730,
            contextid="2",
            classid="101",
            instanceid="0",
            tradable=False
        )
        
        inventory.add_item(item1)
        inventory.add_item(item2)
        
        tradable = inventory.get_tradable()
        assert len(tradable) == 1
        assert tradable[0].tradable is True
    
    def test_get_marketable(self):
        """Test filtering marketable items."""
        inventory = Inventory(steamid="76561198006409530", appid=730)
        
        item1 = InventoryItem(
            assetid="1234567890",
            appid=730,
            contextid="2",
            classid="100",
            instanceid="0",
            marketable=True
        )
        
        item2 = InventoryItem(
            assetid="1234567891",
            appid=730,
            contextid="2",
            classid="101",
            instanceid="0",
            marketable=False
        )
        
        inventory.add_item(item1)
        inventory.add_item(item2)
        
        marketable = inventory.get_marketable()
        assert len(marketable) == 1
        assert marketable[0].marketable is True
    
    def test_get_by_type(self):
        """Test filtering by type."""
        inventory = Inventory(steamid="76561198006409530", appid=730)
        
        item1 = InventoryItem(
            assetid="1234567890",
            appid=730,
            contextid="2",
            classid="100",
            instanceid="0",
            type="Rifle"
        )
        
        item2 = InventoryItem(
            assetid="1234567891",
            appid=730,
            contextid="2",
            classid="101",
            instanceid="0",
            type="Pistol"
        )
        
        item3 = InventoryItem(
            assetid="1234567892",
            appid=730,
            contextid="2",
            classid="102",
            instanceid="0",
            type="Rifle"
        )
        
        inventory.add_item(item1)
        inventory.add_item(item2)
        inventory.add_item(item3)
        
        rifles = inventory.get_by_type("Rifle")
        assert len(rifles) == 2
        
        pistols = inventory.get_by_type("Pistol")
        assert len(pistols) == 1
    
    def test_to_dict(self):
        """Test Inventory serialization."""
        inventory = Inventory(steamid="76561198006409530", appid=730)
        
        item = InventoryItem(
            assetid="1234567890",
            appid=730,
            contextid="2",
            classid="100",
            instanceid="0",
            amount=1,
            name="Test Item",
            price=10.0,
            currency="USD",
            tradable=True,
            marketable=True
        )
        inventory.add_item(item)
        
        data = inventory.to_dict()
        
        assert data["steamid"] == "76561198006409530"
        assert data["appid"] == 730
        assert data["total_items"] == 1
        assert data["total_value"] == 10.0
        assert data["currency"] == "USD"
        assert len(data["items"]) == 1
        assert data["tradable_count"] == 1
        assert data["marketable_count"] == 1


class TestInventoryManager:
    """Test InventoryManager class."""
    
    def test_initialization(self, monkeypatch):
        """Test InventoryManager initialization."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        manager = InventoryManager()
        
        assert manager.client is not None
        assert len(manager._inventories) == 0
    
    def test_get_inventory(self, monkeypatch):
        """Test getting a user's inventory."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        manager = InventoryManager()
        
        with patch.object(manager.client, 'get') as mock_get, \
             patch('steam.inventory.app_cache') as mock_cache:
            
            # Mock API response with inventory data
            mock_response = Mock()
            mock_response.ok = True
            mock_response.source = "steam_api"
            mock_response.data = {
                "assets": [
                    {
                        "assetid": "1234567890",
                        "classid": "100",
                        "instanceid": "0",
                        "contextid": "2",
                        "amount": 1
                    },
                    {
                        "assetid": "1234567891",
                        "classid": "101",
                        "instanceid": "0",
                        "contextid": "2",
                        "amount": 1
                    }
                ],
                "descriptions": [
                    {
                        "classid": "100",
                        "instanceid": "0",
                        "name": "Item 1",
                        "type": "Rifle",
                        "market_name": "Item 1",
                        "market_hash_name": "Item 1",
                        "icon_url": "https://icon.url",
                        "icon_drag_url": "https://drag.url",
                        "tags": [
                            {"tag": "tradable"},
                            {"tag": "marketable"}
                        ],
                        "price_data": {
                            "price_in_cents": 1000,
                            "currency": "USD"
                        }
                    },
                    {
                        "classid": "101",
                        "instanceid": "0",
                        "name": "Item 2",
                        "type": "Pistol",
                        "market_name": "Item 2",
                        "market_hash_name": "Item 2",
                        "tags": [
                            {"tag": "tradable"}
                        ]
                    }
                ],
                "total_inventory_count": 2
            }
            mock_get.return_value = mock_response
            mock_cache.get.return_value = None
            
            response = manager.get_inventory("76561198006409530", 730)
            
            assert response.ok is True
            assert "inventory" in response.data
            assert response.data["inventory"]["total_items"] == 2
            assert response.summary is not None
    
    def test_list_inventory_apps(self, monkeypatch):
        """Test listing inventory apps."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        manager = InventoryManager()
        
        response = manager.list_inventory_apps("76561198006409530")
        
        assert response.ok is True
        assert "inventory_apps" in response.data
        assert len(response.data["inventory_apps"]) > 0
    
    def test_get_inventory_stats(self, monkeypatch):
        """Test getting inventory statistics."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        manager = InventoryManager()
        
        with patch.object(manager, 'get_inventory') as mock_get_inventory:
            # Mock inventory response
            mock_response = Mock()
            mock_response.ok = True
            mock_response.data = {
                "inventory": {
                    "steamid": "76561198006409530",
                    "appid": 730,
                    "total_items": 5,
                    "total_value": 50.0,
                    "currency": "USD",
                    "items": [
                        {"name": "Item 1", "type": "Rifle", "tradable": True, "marketable": True, "amount": 1},
                        {"name": "Item 2", "type": "Rifle", "tradable": True, "marketable": True, "amount": 1},
                        {"name": "Item 3", "type": "Pistol", "tradable": False, "marketable": False, "amount": 1},
                        {"name": "Item 4", "type": "Rifle", "tradable": True, "marketable": True, "amount": 1},
                        {"name": "Item 5", "type": "Pistol", "tradable": True, "marketable": True, "amount": 1}
                    ],
                    "tradable_count": 4,
                    "marketable_count": 4
                }
            }
            mock_get_inventory.return_value = mock_response
            
            response = manager.get_inventory_stats("76561198006409530", 730)
            
            assert response.ok is True
            assert response.data["total_items"] == 5
            assert response.data["total_value"] == 50.0
            assert response.data["tradable_count"] == 4
            assert response.data["marketable_count"] == 4
            assert "type_distribution" in response.data
    
    def test_search_inventory(self, monkeypatch):
        """Test searching inventory."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        manager = InventoryManager()
        
        with patch.object(manager, 'get_inventory') as mock_get_inventory:
            # Mock inventory response
            mock_response = Mock()
            mock_response.ok = True
            mock_response.data = {
                "inventory": {
                    "items": [
                        {"name": "AK-47 | Vulcan", "market_name": "AK-47 | Vulcan"},
                        {"name": "M4A4 | Evil Daimyo", "market_name": "M4A4 | Evil Daimyo"},
                        {"name": "Desert Eagle | Hand Cannon", "market_name": "Desert Eagle | Hand Cannon"}
                    ]
                }
            }
            mock_get_inventory.return_value = mock_response
            
            response = manager.search_inventory("76561198006409530", 730, "AK-47")
            
            assert response.ok is True
            assert response.data["count"] == 1
            assert len(response.data["matching_items"]) == 1
            assert "AK-47" in response.data["matching_items"][0]["name"]
    
    def test_get_tradable_items(self, monkeypatch):
        """Test getting tradable items."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        manager = InventoryManager()
        
        with patch.object(manager, 'get_inventory') as mock_get_inventory:
            # Mock inventory response
            mock_response = Mock()
            mock_response.ok = True
            mock_response.data = {
                "inventory": {
                    "items": [
                        {"name": "Item 1", "tradable": True},
                        {"name": "Item 2", "tradable": False},
                        {"name": "Item 3", "tradable": True}
                    ]
                }
            }
            mock_get_inventory.return_value = mock_response
            
            response = manager.get_tradable_items("76561198006409530", 730)
            
            assert response.ok is True
            assert response.data["count"] == 2
            assert len(response.data["tradable_items"]) == 2


class TestInventoryManagerErrors:
    """Test error handling in InventoryManager."""
    
    def test_get_inventory_error(self, monkeypatch):
        """Test getting inventory with error."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        manager = InventoryManager()
        
        with patch.object(manager.client, 'get') as mock_get, \
             patch('steam.inventory.app_cache') as mock_cache:
            
            mock_response = Mock()
            mock_response.ok = False
            mock_response.error = {"message": "Inventory not accessible or private"}
            mock_get.return_value = mock_response
            mock_cache.get.return_value = None
            
            response = manager.get_inventory("76561198006409530", 730)
            
            assert response.ok is False
    
    def test_get_inventory_stats_error(self, monkeypatch):
        """Test getting inventory stats with error."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        manager = InventoryManager()
        
        with patch.object(manager, 'get_inventory') as mock_get_inventory:
            mock_response = Mock()
            mock_response.ok = False
            mock_response.error = {"message": "Inventory not found"}
            mock_get_inventory.return_value = mock_response
            
            response = manager.get_inventory_stats("76561198006409530", 730)
            
            assert response.ok is False
