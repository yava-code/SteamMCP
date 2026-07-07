"""
Tests for the Price Tracker module.

These tests verify:
- Price tracking functionality
- Price history management
- Discount detection
- Regional price comparison
- Error handling
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timezone, timedelta

from steam.price_tracker import PriceTracker, PricePoint, PriceHistory
from steam.client import APIResponse


class TestPricePoint:
    """Test PricePoint dataclass."""
    
    def test_price_point_creation(self):
        """Test PricePoint creation from API data."""
        price_data = {
            "initial": 1999,
            "final": 999,
            "discount_percent": 50,
            "currency": "USD"
        }
        
        point = PricePoint.from_api_data(730, price_data, "USD")
        
        assert point.appid == 730
        assert point.currency == "USD"
        assert point.initial_price == 19.99
        assert point.final_price == 9.99
        assert point.discount_percent == 50
        assert point.is_on_sale is True
        assert point.timestamp is not None
    
    def test_price_point_not_on_sale(self):
        """Test PricePoint when not on sale."""
        price_data = {
            "initial": 1999,
            "final": 1999,
            "discount_percent": 0
        }
        
        point = PricePoint.from_api_data(730, price_data, "USD")
        
        assert point.is_on_sale is False
    
    def test_price_point_to_dict(self):
        """Test PricePoint serialization."""
        price_data = {
            "initial": 1000,
            "final": 500,
            "discount_percent": 50
        }
        
        point = PricePoint.from_api_data(730, price_data, "USD")
        data = point.to_dict()
        
        assert data["appid"] == 730
        assert data["currency"] == "USD"
        assert data["initial_price"] == 10.0
        assert data["final_price"] == 5.0
        assert data["discount_percent"] == 50
        assert "timestamp" in data


class TestPriceHistory:
    """Test PriceHistory dataclass."""
    
    def test_price_history_creation(self):
        """Test PriceHistory creation."""
        history = PriceHistory(appid=730, currency="USD")
        
        assert history.appid == 730
        assert history.currency == "USD"
        assert len(history.price_points) == 0
        assert history.current_price is None
    
    def test_add_price_point(self):
        """Test adding price points to history."""
        history = PriceHistory(appid=730, currency="USD")
        
        point1 = PricePoint(
            appid=730,
            currency="USD",
            initial_price=20.0,
            final_price=20.0,
            discount_percent=0,
            timestamp=datetime.now(timezone.utc) - timedelta(days=1)
        )
        
        point2 = PricePoint(
            appid=730,
            currency="USD",
            initial_price=20.0,
            final_price=10.0,
            discount_percent=50,
            timestamp=datetime.now(timezone.utc)
        )
        
        history.add_price_point(point1)
        history.add_price_point(point2)
        
        assert len(history.price_points) == 2
        assert history.current_price == point2
        assert history.lowest_price == 10.0
        assert history.highest_price == 20.0
    
    def test_get_price_change(self):
        """Test price change detection."""
        history = PriceHistory(appid=730, currency="USD")
        
        now = datetime.now(timezone.utc)
        point1 = PricePoint(730, "USD", 20.0, 20.0, 0, now - timedelta(days=1))
        point2 = PricePoint(730, "USD", 20.0, 10.0, 50, now)
        
        history.add_price_point(point1)
        history.add_price_point(point2)
        
        change = history.get_price_change()
        
        assert change is not None
        assert change["old_price"] == 20.0
        assert change["new_price"] == 10.0
        assert change["change"] == -10.0
        assert change["change_percent"] == -50.0
        assert change["is_decrease"] is True
    
    def test_is_on_sale_now(self):
        """Test current sale detection."""
        history = PriceHistory(appid=730, currency="USD")
        
        point = PricePoint(730, "USD", 20.0, 10.0, 50, datetime.now(timezone.utc), is_on_sale=True)
        history.add_price_point(point)
        
        assert history.is_on_sale_now() is True
        
        point2 = PricePoint(730, "USD", 20.0, 20.0, 0, datetime.now(timezone.utc), is_on_sale=False)
        history.add_price_point(point2)
        
        assert history.is_on_sale_now() is False
    
    def test_to_dict(self):
        """Test PriceHistory serialization."""
        history = PriceHistory(appid=730, currency="USD")
        point = PricePoint(730, "USD", 20.0, 10.0, 50, datetime.now(timezone.utc), is_on_sale=True)
        history.add_price_point(point)
        
        data = history.to_dict()
        
        assert data["appid"] == 730
        assert data["currency"] == "USD"
        assert data["current_price"] is not None
        assert data["is_on_sale_now"] is True


class TestPriceTracker:
    """Test PriceTracker class."""
    
    def test_initialization(self, monkeypatch):
        """Test PriceTracker initialization."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        tracker = PriceTracker()
        
        assert tracker.client is not None
        assert len(tracker._tracked_apps) == 0
    
    def test_track_app(self, monkeypatch):
        """Test tracking a new app."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        tracker = PriceTracker()
        
        with patch.object(tracker.client, 'get') as mock_get, \
             patch('steam.price_tracker.app_cache') as mock_cache:
            
            # Mock API response with price data
            mock_response = Mock()
            mock_response.ok = True
            mock_response.source = "steam_store_api"
            mock_response.data = {
                "730": {
                    "success": True,
                    "data": {
                        "price_overview": {
                            "initial": 1999,
                            "final": 999,
                            "discount_percent": 50,
                            "currency": "USD"
                        }
                    }
                }
            }
            mock_get.return_value = mock_response
            mock_cache.get.return_value = None
            
            response = tracker.track_app(730, "USD")
            
            assert response.ok is True
            assert "price_history" in response.data
            assert 730 in tracker._tracked_apps
    
    def test_get_price_history(self, monkeypatch):
        """Test getting price history for an app."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        tracker = PriceTracker()
        
        # First track the app
        with patch.object(tracker.client, 'get') as mock_get, \
             patch('steam.price_tracker.app_cache') as mock_cache:
            
            mock_response = Mock()
            mock_response.ok = True
            mock_response.data = {
                "730": {
                    "success": True,
                    "data": {
                        "price_overview": {
                            "initial": 1999,
                            "final": 999,
                            "discount_percent": 50,
                            "currency": "USD"
                        }
                    }
                }
            }
            mock_get.return_value = mock_response
            mock_cache.get.return_value = None
            
            tracker.track_app(730, "USD")
        
        # Now get history
        response = tracker.get_price_history(730, "USD", days=30)
        
        assert response.ok is True
        assert "price_history" in response.data
    
    def test_check_discounts(self, monkeypatch):
        """Test checking discounts for multiple apps."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        tracker = PriceTracker()
        
        with patch.object(tracker.client, 'get') as mock_get, \
             patch('steam.price_tracker.app_cache') as mock_cache:
            
            # Mock response for app on sale
            mock_response_on_sale = Mock()
            mock_response_on_sale.ok = True
            mock_response_on_sale.data = {
                "730": {
                    "success": True,
                    "data": {
                        "price_overview": {
                            "initial": 1999,
                            "final": 999,
                            "discount_percent": 50,
                            "currency": "USD"
                        }
                    }
                }
            }
            
            # Mock response for app not on sale
            mock_response_normal = Mock()
            mock_response_normal.ok = True
            mock_response_normal.data = {
                "570": {
                    "success": True,
                    "data": {
                        "price_overview": {
                            "initial": 0,
                            "final": 0,
                            "discount_percent": 0,
                            "currency": "USD"
                        }
                    }
                }
            }
            
            # Set up side effect to return different responses
            mock_get.side_effect = [mock_response_on_sale, mock_response_normal]
            mock_cache.get.return_value = None
            
            response = tracker.check_discounts([730, 570], "USD")
            
            assert response.ok is True
            assert "on_sale" in response.data
            assert "not_on_sale" in response.data
    
    def test_compare_regions(self, monkeypatch):
        """Test comparing prices across regions."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        tracker = PriceTracker()
        
        with patch.object(tracker.client, 'get') as mock_get:
            # Mock responses for different regions
            # The _get_current_price method expects response.data to contain:
            # {"730": {"success": True, "data": {"price_overview": {...}}}}
            mock_response_us = Mock()
            mock_response_us.ok = True
            mock_response_us.data = {
                "730": {
                    "success": True,
                    "data": {
                        "price_overview": {
                            "initial": 1999,
                            "final": 1999,
                            "discount_percent": 0,
                            "currency": "USD"
                        }
                    }
                }
            }
            
            mock_response_eu = Mock()
            mock_response_eu.ok = True
            mock_response_eu.data = {
                "730": {
                    "success": True,
                    "data": {
                        "price_overview": {
                            "initial": 1799,
                            "final": 1799,
                            "discount_percent": 0,
                            "currency": "EUR"
                        }
                    }
                }
            }
            
            mock_get.side_effect = [mock_response_us, mock_response_eu]
            
            response = tracker.compare_regions(730, regions=["US", "EU"])
            
            assert response.ok is True
            assert "regional_prices" in response.data
            assert "best_deal" in response.data
            assert len(response.data["regional_prices"]) == 2


class TestPriceTrackerErrors:
    """Test error handling in PriceTracker."""
    
    def test_track_app_not_found(self, monkeypatch):
        """Test tracking a non-existent app."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        tracker = PriceTracker()
        
        with patch.object(tracker.client, 'get') as mock_get, \
             patch('steam.price_tracker.app_cache') as mock_cache:
            
            mock_response = Mock()
            mock_response.ok = False
            mock_response.source = "steam_store_api"
            mock_response.data = {}
            mock_response.error = {"message": "App not found"}
            
            mock_get.return_value = mock_response
            mock_cache.get.return_value = None
            
            response = tracker.track_app(999999, "USD")
            
            assert response.ok is False
    
    def test_get_price_history_untracked_app(self, monkeypatch):
        """Test getting history for untracked app."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        tracker = PriceTracker()
        
        with patch.object(tracker.client, 'get') as mock_get, \
             patch('steam.price_tracker.app_cache') as mock_cache:
            
            # Mock error response - app not found
            mock_response = Mock()
            mock_response.ok = False
            mock_response.data = {"999999": {"success": False}}
            mock_response.error = {"message": "App not found"}
            mock_get.return_value = mock_response
            mock_cache.get.return_value = None
            
            # Try to get history - it will try to track first, which will fail
            response = tracker.get_price_history(999999, "USD")
            
            assert response.ok is False
            # The error will be from the tracking attempt
            assert response.error is not None
    
    def test_check_discounts_with_errors(self, monkeypatch):
        """Test discount checking with some errors."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        tracker = PriceTracker()
        
        with patch.object(tracker.client, 'get') as mock_get, \
             patch('steam.price_tracker.app_cache') as mock_cache:
            
            # Mock error response
            mock_response_error = Mock()
            mock_response_error.ok = False
            mock_response_error.error = {"message": "API error"}
            
            mock_get.return_value = mock_response_error
            mock_cache.get.return_value = None
            
            response = tracker.check_discounts([999999], "USD")
            
            assert response.ok is True  # check_discounts always returns ok
            assert len(response.data["errors"]) == 1
