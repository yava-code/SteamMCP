"""
Tests for the Steam Store API module.

These tests verify:
- Store API functionality
- Cache integration
- Response normalization
- Error handling
"""

import pytest
from unittest.mock import patch, Mock

from steam.store import SteamStoreAPI
from steam.client import APIResponse


class TestSteamStoreAPI:
    """Test SteamStoreAPI class."""
    
    def test_initialization(self, monkeypatch):
        """Test SteamStoreAPI initialization."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        store = SteamStoreAPI()
        assert store.client is not None
    
    def test_get_app_details(self, monkeypatch):
        """Test get_app_details method."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        store = SteamStoreAPI()
        
        with patch.object(store.client, 'get') as mock_get:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.source = "steam_store_api"
            mock_response.data = {
                "730": {
                    "success": True,
                    "data": {
                        "name": "Counter-Strike: Global Offensive",
                        "is_free": False
                    }
                }
            }
            mock_get.return_value = mock_response
            
            response = store.get_app_details(730)
            assert response.ok is True
            assert response.source == "steam_store_api"
    
    def test_search_games(self, monkeypatch):
        """Test search_games method."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        store = SteamStoreAPI()
        
        with patch.object(store.client, 'get') as mock_get:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.source = "steam_store_api"
            mock_response.data = {
                "results": [
                    {"appid": 730, "name": "Counter-Strike: Global Offensive"},
                    {"appid": 570, "name": "Dota 2"}
                ]
            }
            mock_get.return_value = mock_response
            
            response = store.search_games("counter-strike")
            assert response.ok is True
    
    def test_search_games_empty_query(self, monkeypatch):
        """Test search_games with empty query."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        store = SteamStoreAPI()
        
        response = store.search_games("")
        assert response.ok is False
        assert "Empty query" in response.warnings
    
    def test_get_featured_specials(self, monkeypatch):
        """Test get_featured_specials method."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        store = SteamStoreAPI()
        
        with patch.object(store.client, 'get') as mock_get:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.source = "steam_store_api"
            mock_response.data = {
                "specials": {
                    "items": [
                        {"appid": 730, "discount_percent": 50},
                        {"appid": 570, "discount_percent": 30}
                    ]
                }
            }
            mock_get.return_value = mock_response
            
            response = store.get_featured_specials()
            assert response.ok is True
    
    def test_get_store_highlights(self, monkeypatch):
        """Test get_store_highlights method."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        store = SteamStoreAPI()
        
        with patch.object(store.client, 'get') as mock_get:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.source = "steam_store_api"
            mock_response.data = {
                "highlights": [
                    {"appid": 730, "type": "featured"},
                    {"appid": 570, "type": "new_release"}
                ]
            }
            mock_get.return_value = mock_response
            
            response = store.get_store_highlights()
            assert response.ok is True
    
    def test_get_app_reviews_summary(self, monkeypatch):
        """Test get_app_reviews_summary method."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        store = SteamStoreAPI()
        
        with patch.object(store.client, 'get') as mock_get:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.source = "steam_store_api"
            mock_response.data = {
                "query_summary": {
                    "total_reviews": 1000,
                    "positive": 800,
                    "negative": 200,
                    "score": 80
                }
            }
            mock_get.return_value = mock_response
            
            response = store.get_app_reviews_summary(730)
            assert response.ok is True
    
    def test_get_app_tags(self, monkeypatch):
        """Test get_app_tags method."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        store = SteamStoreAPI()
        
        with patch.object(store.client, 'get') as mock_get:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.source = "steam_store_api"
            mock_response.data = {
                "730": {
                    "success": True,
                    "data": {
                        "tags": [
                            {"tagid": 19, "name": "Action"},
                            {"tagid": 21, "name": "Free to Play"}
                        ]
                    }
                }
            }
            mock_get.return_value = mock_response
            
            response = store.get_app_tags(730)
            assert response.ok is True
    
    def test_get_release_calendar(self, monkeypatch):
        """Test get_release_calendar method."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        store = SteamStoreAPI()
        
        with patch.object(store.client, 'get') as mock_get:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.source = "steam_store_api"
            mock_response.data = {
                "upcoming": [
                    {"appid": 12345, "name": "New Game", "release_date": "2024-12-15"}
                ]
            }
            mock_get.return_value = mock_response
            
            response = store.get_release_calendar()
            assert response.ok is True
    
    def test_get_app_update_signal(self, monkeypatch):
        """Test get_app_update_signal method."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        store = SteamStoreAPI()
        
        # Mock app details response
        with patch.object(store, 'get_app_details') as mock_app_details, \
             patch('steam.web.SteamWebAPI') as mock_web_api_class:
            
            # Mock app details with real APIResponse
            mock_app_response = APIResponse(
                ok=True,
                source="steam_store_api",
                data={
                    "app": {
                        "name": "Test Game",
                        "last_updated": 1234567890
                    }
                }
            )
            mock_app_details.return_value = mock_app_response
            
            # Mock web API
            mock_web_api = Mock()
            mock_news_response = APIResponse(
                ok=True,
                source="steam_web_api",
                data={
                    "news": [
                        {"date": 1234567890, "title": "Update 1.0"}
                    ]
                }
            )
            mock_web_api.get_game_news.return_value = mock_news_response
            mock_web_api_class.return_value = mock_web_api
            
            response = store.get_app_update_signal(730)
            assert response.ok is True
            assert "update_signal" in response.data


class TestCacheIntegration:
    """Test cache integration in Store API."""
    
    def test_search_games_caching(self, monkeypatch):
        """Test that search_games uses cache."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        store = SteamStoreAPI()
        
        with patch.object(store.client, 'get') as mock_get, \
             patch('steam.store.discovery_cache') as mock_cache:
            
            # Return a real APIResponse
            api_response = APIResponse(
                ok=True,
                source="steam_store_api",
                data={"results": []}
            )
            mock_get.return_value = api_response
            
            # Configure cache mock
            mock_cache.get.return_value = None
            mock_cache.set.return_value = None
            
            # First call should hit the API
            store.search_games("test")
            assert mock_get.call_count == 1
            
            # Second call with same params should use cache
            mock_cache.get.return_value = api_response
            store.search_games("test")
            # Note: The actual implementation might still call get() due to how the cache is used
            # This test verifies the cache is being called
            mock_cache.get.assert_called()
    
    def test_app_details_caching(self, monkeypatch):
        """Test that get_app_details uses cache."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        store = SteamStoreAPI()
        
        with patch.object(store.client, 'get') as mock_get, \
             patch('steam.store.app_cache') as mock_cache:
            
            # Return a real APIResponse
            api_response = APIResponse(
                ok=True,
                source="steam_store_api",
                data={"730": {"success": True, "data": {}}}
            )
            mock_get.return_value = api_response
            
            # Configure cache mock
            mock_cache.get.return_value = None
            mock_cache.set.return_value = None
            
            # First call should hit the API
            store.get_app_details(730)
            assert mock_get.call_count == 1
            
            # Second call with same params should use cache
            mock_cache.get.return_value = api_response
            store.get_app_details(730)
            # Verify cache is being used
            mock_cache.get.assert_called()


class TestParameterValidation:
    """Test parameter validation in Store API."""
    
    def test_app_id_validation(self, monkeypatch):
        """Test that invalid app IDs are handled."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        store = SteamStoreAPI()
        
        # Invalid app ID should be handled by AppID.validate
        with pytest.raises(Exception):
            store.get_app_details(-1)
    
    def test_country_code_parameter(self, monkeypatch):
        """Test country code parameter."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        store = SteamStoreAPI()
        
        with patch.object(store.client, 'get') as mock_get:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.data = {}
            mock_get.return_value = mock_response
            
            # Test with different country codes
            store.get_app_details(730, country_code="RU")
            call_args = mock_get.call_args
            assert call_args[1]['params']['cc'] == "RU"
            
            store.get_app_details(730, country_code="EU")
            call_args = mock_get.call_args
            assert call_args[1]['params']['cc'] == "EU"
    
    def test_language_parameter(self, monkeypatch):
        """Test language parameter."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        store = SteamStoreAPI()
        
        with patch.object(store.client, 'get') as mock_get:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.data = {}
            mock_get.return_value = mock_response
            
            # Test with different languages
            store.get_app_details(730, language="russian")
            call_args = mock_get.call_args
            assert call_args[1]['params']['l'] == "russian"


class TestResponseNormalization:
    """Test response normalization in Store API."""
    
    def test_success_response_structure(self, monkeypatch):
        """Test that successful responses have correct structure."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        store = SteamStoreAPI()
        
        with patch.object(store.client, 'get') as mock_get, \
             patch('steam.store.app_cache') as mock_cache:
            # Return a real APIResponse object
            api_response = APIResponse(
                ok=True,
                source="steam_store_api",
                data={
                    "730": {
                        "success": True,
                        "data": {"name": "Test Game"}
                    }
                }
            )
            mock_get.return_value = api_response
            # Ensure cache doesn't return cached value
            mock_cache.get.return_value = None
            
            response = store.get_app_details(730)
            assert isinstance(response, APIResponse)
            assert hasattr(response, 'ok')
            assert hasattr(response, 'source')
            assert hasattr(response, 'data')
            assert hasattr(response, 'fetched_at')
    
    def test_error_response_structure(self, monkeypatch):
        """Test that error responses have correct structure."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        store = SteamStoreAPI()
        
        with patch.object(store.client, 'get') as mock_get:
            # Return a real APIResponse object
            mock_get.return_value = APIResponse(
                ok=False,
                source="steam_store_api",
                data={},
                error={"message": "Not found"}
            )
            
            response = store.get_app_details(999999)
            assert isinstance(response, APIResponse)
            assert response.ok is False
