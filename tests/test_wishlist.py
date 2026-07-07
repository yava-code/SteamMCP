"""
Tests for the Wishlist module.

These tests verify:
- Wishlist data structures
- Wishlist parsing
- Wishlist operations
- Error handling
"""

import pytest
from unittest.mock import patch, Mock

from steam.wishlist import WishlistManager, Wishlist, WishlistItem
from steam.client import APIResponse


class TestWishlistItem:
    """Test WishlistItem dataclass."""
    
    def test_wishlist_item_creation(self):
        """Test WishlistItem creation from API data."""
        data = {
            "appid": 730,
            "name": "Counter-Strike 2",
            "capsule": "https://capsule.com/730.jpg",
            "logo": "https://logo.com/730.jpg",
            "price_overview": {
                "initial": 1999,
                "final": 999,
                "discount_percent": 50,
                "currency": "USD"
            },
            "priority": 3,
            "added_date": 1234567890
        }
        
        item = WishlistItem.from_api_data(data)
        
        assert item.appid == 730
        assert item.name == "Counter-Strike 2"
        assert item.capsule == "https://capsule.com/730.jpg"
        assert item.logo == "https://logo.com/730.jpg"
        assert item.price == 9.99
        assert item.currency == "USD"
        assert item.is_free is False
        assert item.priority == 3
        assert item.added_date == 1234567890
        assert item.is_on_sale is True
        assert item.discount_percent == 50
    
    def test_wishlist_item_free_game(self):
        """Test WishlistItem for free game."""
        data = {
            "appid": 570,
            "name": "Dota 2",
            "price_overview": {
                "initial": 0,
                "final": 0,
                "discount_percent": 0,
                "currency": "USD"
            }
        }
        
        item = WishlistItem.from_api_data(data)
        
        assert item.is_free is True
        assert item.price == 0.0
        assert item.is_on_sale is False
    
    def test_wishlist_item_to_dict(self):
        """Test WishlistItem serialization."""
        data = {
            "appid": 730,
            "name": "CS2",
            "price_overview": {
                "initial": 1999,
                "final": 999,
                "discount_percent": 50,
                "currency": "USD"
            }
        }
        
        item = WishlistItem.from_api_data(data)
        item_dict = item.to_dict()
        
        assert item_dict["appid"] == 730
        assert item_dict["name"] == "CS2"
        assert item_dict["price"] == 9.99
        assert item_dict["currency"] == "USD"
        assert item_dict["is_on_sale"] is True


class TestWishlist:
    """Test Wishlist dataclass."""
    
    def test_wishlist_creation(self):
        """Test Wishlist creation."""
        wishlist = Wishlist(steamid="76561198006409530")
        
        assert wishlist.steamid == "76561198006409530"
        assert len(wishlist.items) == 0
        assert wishlist.total_items == 0
        assert wishlist.total_price == 0.0
    
    def test_add_item(self):
        """Test adding items to wishlist."""
        wishlist = Wishlist(steamid="76561198006409530")
        
        item1 = WishlistItem(
            appid=730,
            name="CS2",
            price=9.99,
            currency="USD",
            is_on_sale=True,
            discount_percent=50
        )
        
        item2 = WishlistItem(
            appid=570,
            name="Dota 2",
            price=0.0,
            currency="USD",
            is_free=True
        )
        
        wishlist.add_item(item1)
        wishlist.add_item(item2)
        
        assert wishlist.total_items == 2
        assert wishlist.total_price == 9.99
        assert wishlist.currency == "USD"
    
    def test_remove_item(self):
        """Test removing items from wishlist."""
        wishlist = Wishlist(steamid="76561198006409530")
        
        item = WishlistItem(appid=730, name="CS2", price=9.99)
        wishlist.add_item(item)
        
        assert wishlist.total_items == 1
        
        removed = wishlist.remove_item(730)
        assert removed is True
        assert wishlist.total_items == 0
        
        # Try to remove non-existent item
        removed = wishlist.remove_item(999)
        assert removed is False
    
    def test_get_item(self):
        """Test getting specific item from wishlist."""
        wishlist = Wishlist(steamid="76561198006409530")
        
        item = WishlistItem(appid=730, name="CS2", price=9.99)
        wishlist.add_item(item)
        
        retrieved = wishlist.get_item(730)
        assert retrieved is not None
        assert retrieved.appid == 730
        
        not_found = wishlist.get_item(999)
        assert not_found is None
    
    def test_has_item(self):
        """Test checking if item is in wishlist."""
        wishlist = Wishlist(steamid="76561198006409530")
        
        item = WishlistItem(appid=730, name="CS2", price=9.99)
        wishlist.add_item(item)
        
        assert wishlist.has_item(730) is True
        assert wishlist.has_item(999) is False
    
    def test_get_on_sale_items(self):
        """Test filtering on-sale items."""
        wishlist = Wishlist(steamid="76561198006409530")
        
        item1 = WishlistItem(appid=730, name="CS2", price=9.99, is_on_sale=True, discount_percent=50)
        item2 = WishlistItem(appid=570, name="Dota 2", price=0.0, is_on_sale=False)
        item3 = WishlistItem(appid=440, name="TL2", price=4.99, is_on_sale=True, discount_percent=75)
        
        wishlist.add_item(item1)
        wishlist.add_item(item2)
        wishlist.add_item(item3)
        
        on_sale = wishlist.get_on_sale_items()
        assert len(on_sale) == 2
        assert all(item.is_on_sale for item in on_sale)
    
    def test_get_by_priority(self):
        """Test filtering by priority."""
        wishlist = Wishlist(steamid="76561198006409530")
        
        item1 = WishlistItem(appid=730, name="CS2", priority=3)
        item2 = WishlistItem(appid=570, name="Dota 2", priority=1)
        item3 = WishlistItem(appid=440, name="TL2", priority=3)
        
        wishlist.add_item(item1)
        wishlist.add_item(item2)
        wishlist.add_item(item3)
        
        high_priority = wishlist.get_by_priority(3)
        assert len(high_priority) == 2
        
        low_priority = wishlist.get_by_priority(1)
        assert len(low_priority) == 1
    
    def test_to_dict(self):
        """Test Wishlist serialization."""
        wishlist = Wishlist(steamid="76561198006409530")
        
        item = WishlistItem(
            appid=730,
            name="CS2",
            price=9.99,
            currency="USD",
            is_on_sale=True,
            discount_percent=50
        )
        wishlist.add_item(item)
        
        data = wishlist.to_dict()
        
        assert data["steamid"] == "76561198006409530"
        assert data["total_items"] == 1
        assert data["total_price"] == 9.99
        assert data["currency"] == "USD"
        assert len(data["items"]) == 1
        assert data["on_sale_count"] == 1


class TestWishlistManager:
    """Test WishlistManager class."""
    
    def test_initialization(self, monkeypatch):
        """Test WishlistManager initialization."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        manager = WishlistManager()
        
        assert manager.client is not None
        assert len(manager._wishlists) == 0
    
    def test_get_wishlist(self, monkeypatch):
        """Test getting a user's wishlist."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        manager = WishlistManager()
        
        with patch.object(manager.client, 'get') as mock_get, \
             patch('steam.wishlist.app_cache') as mock_cache:
            
            # Mock API response with wishlist data
            mock_response = Mock()
            mock_response.ok = True
            mock_response.source = "steam_store_api"
            mock_response.data = {
                "items": [
                    {
                        "appid": 730,
                        "name": "Counter-Strike 2",
                        "price_overview": {
                            "initial": 1999,
                            "final": 999,
                            "discount_percent": 50,
                            "currency": "USD"
                        },
                        "priority": 3
                    },
                    {
                        "appid": 570,
                        "name": "Dota 2",
                        "price_overview": {
                            "initial": 0,
                            "final": 0,
                            "discount_percent": 0,
                            "currency": "USD"
                        },
                        "priority": 1
                    }
                ]
            }
            mock_get.return_value = mock_response
            mock_cache.get.return_value = None
            
            response = manager.get_wishlist("76561198006409530")
            
            assert response.ok is True
            assert "wishlist" in response.data
            assert response.data["wishlist"]["total_items"] == 2
            assert response.summary is not None
    
    def test_check_in_wishlist(self, monkeypatch):
        """Test checking if app is in wishlist."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        manager = WishlistManager()
        
        with patch.object(manager, 'get_wishlist') as mock_get_wishlist:
            # Mock wishlist response
            mock_response = Mock()
            mock_response.ok = True
            mock_response.data = {
                "wishlist": {
                    "items": [
                        {"appid": 730, "name": "CS2"},
                        {"appid": 570, "name": "Dota 2"}
                    ]
                }
            }
            mock_get_wishlist.return_value = mock_response
            
            response = manager.check_in_wishlist("76561198006409530", 730)
            
            assert response.ok is True
            assert response.data["in_wishlist"] is True
            assert response.data["appid"] == 730
            
            response2 = manager.check_in_wishlist("76561198006409530", 999)
            assert response2.data["in_wishlist"] is False
    
    def test_get_wishlist_stats(self, monkeypatch):
        """Test getting wishlist statistics."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        manager = WishlistManager()
        
        with patch.object(manager, 'get_wishlist') as mock_get_wishlist:
            # Mock wishlist response
            mock_response = Mock()
            mock_response.ok = True
            mock_response.data = {
                "wishlist": {
                    "currency": "USD",
                    "items": [
                        {"appid": 730, "name": "CS2", "price": 9.99, "is_on_sale": True, "priority": 3},
                        {"appid": 570, "name": "Dota 2", "price": 0.0, "is_on_sale": False, "priority": 1},
                        {"appid": 440, "name": "TL2", "price": 4.99, "is_on_sale": True, "priority": 2}
                    ]
                }
            }
            mock_get_wishlist.return_value = mock_response
            
            response = manager.get_wishlist_stats("76561198006409530")
            
            assert response.ok is True
            assert response.data["total_items"] == 3
            assert response.data["total_price"] == 14.98
            assert response.data["on_sale_count"] == 2
            assert response.data["currency"] == "USD"
            assert "priority_distribution" in response.data
    
    def test_get_wishlist_on_sale(self, monkeypatch):
        """Test getting on-sale items from wishlist."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        manager = WishlistManager()
        
        with patch.object(manager, 'get_wishlist') as mock_get_wishlist:
            # Mock wishlist response
            mock_response = Mock()
            mock_response.ok = True
            mock_response.data = {
                "wishlist": {
                    "items": [
                        {"appid": 730, "name": "CS2", "price": 9.99, "is_on_sale": True, "discount_percent": 50},
                        {"appid": 570, "name": "Dota 2", "price": 0.0, "is_on_sale": False},
                        {"appid": 440, "name": "TL2", "price": 4.99, "is_on_sale": True, "discount_percent": 75}
                    ]
                }
            }
            mock_get_wishlist.return_value = mock_response
            
            response = manager.get_wishlist_on_sale("76561198006409530")
            
            assert response.ok is True
            assert response.data["count"] == 2
            assert len(response.data["on_sale_items"]) == 2
            # Should be sorted by discount percent (highest first)
            assert response.data["on_sale_items"][0]["discount_percent"] == 75
            assert response.data["on_sale_items"][1]["discount_percent"] == 50


class TestWishlistManagerErrors:
    """Test error handling in WishlistManager."""
    
    def test_get_wishlist_error(self, monkeypatch):
        """Test getting wishlist with error."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        manager = WishlistManager()
        
        with patch.object(manager.client, 'get') as mock_get, \
             patch('steam.wishlist.app_cache') as mock_cache:
            
            mock_response = Mock()
            mock_response.ok = False
            mock_response.error = {"message": "Wishlist not found or private"}
            mock_get.return_value = mock_response
            mock_cache.get.return_value = None
            
            response = manager.get_wishlist("76561198006409530")
            
            assert response.ok is False
    
    def test_check_in_wishlist_error(self, monkeypatch):
        """Test checking wishlist with error."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        manager = WishlistManager()
        
        with patch.object(manager, 'get_wishlist') as mock_get_wishlist:
            mock_response = Mock()
            mock_response.ok = False
            mock_response.error = {"message": "Wishlist not found"}
            mock_get_wishlist.return_value = mock_response
            
            response = manager.check_in_wishlist("76561198006409530", 730)
            
            assert response.ok is False
