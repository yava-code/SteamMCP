"""
Tests for the Steam client module.

These tests verify:
- HTTP client functionality
- Retry logic
- Rate limiting handling
- Response normalization
- Error handling
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timezone

from steam.client import (
    SteamClient, 
    SteamAPIError, 
    MarketAPIError,
    APIResponse,
    RateLimitInfo
)


class TestSteamAPIError:
    """Test SteamAPIError exception."""
    
    def test_basic_error(self):
        """Test basic error creation."""
        error = SteamAPIError(404, "Not found")
        assert error.status_code == 404
        assert "Not found" in str(error)
        assert error.source == "unknown"
    
    def test_error_with_endpoint(self):
        """Test error with endpoint."""
        error = SteamAPIError(500, "Server error", endpoint="/test")
        assert error.endpoint == "/test"
        assert error.source == "unknown"
    
    def test_error_with_source(self):
        """Test error with custom source."""
        error = SteamAPIError(403, "Forbidden", source="steam_web_api")
        assert error.source == "steam_web_api"
    
    def test_secret_redaction(self):
        """Test that API keys are redacted from error messages."""
        api_key = "A" * 32  # 32 hex chars
        error = SteamAPIError(400, f"Invalid key: {api_key}")
        assert api_key not in str(error)
        assert "[REDACTED]" in str(error)
    
    def test_to_dict(self):
        """Test error to_dict method."""
        error = SteamAPIError(404, "Not found", endpoint="/test")
        error_dict = error.to_dict()
        
        assert error_dict["error"] is True
        assert error_dict["status_code"] == 404
        assert error_dict["message"] == "Not found"
        assert error_dict["endpoint"] == "/test"
        assert "timestamp" in error_dict


class TestMarketAPIError:
    """Test MarketAPIError exception."""
    
    def test_market_error(self):
        """Test market error creation."""
        error = MarketAPIError(404, "Not found")
        assert error.source == "market"


class TestAPIResponse:
    """Test APIResponse dataclass."""
    
    def test_success_response(self):
        """Test successful response."""
        response = APIResponse(
            ok=True,
            source="steam_web_api",
            data={"test": "value"}
        )
        assert response.ok is True
        assert response.source == "steam_web_api"
        assert response.data == {"test": "value"}
        assert len(response.warnings) == 0
        assert "fetched_at" in response.to_dict()
    
    def test_error_response(self):
        """Test error response."""
        response = APIResponse(
            ok=False,
            source="steam_web_api",
            data={},
            error={"message": "Not found"}
        )
        assert response.ok is False
        assert response.error["message"] == "Not found"
    
    def test_response_with_warnings(self):
        """Test response with warnings."""
        response = APIResponse(
            ok=True,
            source="steam_web_api",
            data={},
            warnings=["Rate limit approaching"]
        )
        assert len(response.warnings) == 1
        assert "Rate limit approaching" in response.warnings
    
    def test_response_with_rate_limit_hint(self):
        """Test response with rate limit hint."""
        response = APIResponse(
            ok=True,
            source="steam_web_api",
            data={},
            rate_limit_hint={"retry_after": 5}
        )
        assert response.rate_limit_hint["retry_after"] == 5


class TestRateLimitInfo:
    """Test RateLimitInfo dataclass."""
    
    def test_basic_rate_limit_info(self):
        """Test basic rate limit info."""
        info = RateLimitInfo(remaining=10, limited=False)
        assert info.remaining == 10
        assert info.limited is False
    
    def test_limited_rate_limit_info(self):
        """Test limited rate limit info."""
        info = RateLimitInfo(remaining=0, limited=True, retry_after=5)
        assert info.limited is True
        assert info.retry_after == 5


class TestSteamClient:
    """Test SteamClient class."""
    
    def test_client_initialization(self, monkeypatch):
        """Test client initialization with API key."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key_123")
        client = SteamClient()
        assert client.api_key == "test_key_123"
        assert client.timeout == 10
        assert client.max_retries == 3
    
    def test_client_initialization_with_params(self, monkeypatch):
        """Test client initialization with custom parameters."""
        monkeypatch.setenv("STEAM_API_KEY", "")
        client = SteamClient(api_key="custom_key", timeout=30, max_retries=5)
        assert client.api_key == "custom_key"
        assert client.timeout == 30
        assert client.max_retries == 5
    
    def test_client_missing_api_key(self, monkeypatch):
        """Test client initialization without API key."""
        monkeypatch.delenv("STEAM_API_KEY", raising=False)
        with pytest.raises(ValueError, match="STEAM_API_KEY is required"):
            SteamClient()
    
    def test_host_validation(self, monkeypatch):
        """Test host validation."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        client = SteamClient()
        
        # Valid host
        client._validate_host("https://api.steampowered.com/test")
        
        # Invalid host
        with pytest.raises(ValueError, match="not in the allowlist"):
            client._validate_host("https://evil.com/test")
    
    def test_backoff_calculation(self, monkeypatch):
        """Test backoff calculation."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        client = SteamClient(backoff_factor=1.0)
        
        assert client._calculate_backoff(0) == 1.0
        assert client._calculate_backoff(1) == 2.0
        assert client._calculate_backoff(2) == 4.0
    
    def test_get_source_from_url(self, monkeypatch):
        """Test source extraction from URL."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        client = SteamClient()
        
        assert client._get_source_from_url("https://api.steampowered.com/test") == "steam_web_api"
        assert client._get_source_from_url("https://store.steampowered.com/api/test") == "steam_store_api"
        assert client._get_source_from_url("https://steamcommunity.com/test") == "steam_community"
        assert client._get_source_from_url("https://unknown.com/test") == "unknown"
    
    def test_make_request_success(self, monkeypatch):
        """Test successful request."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        client = SteamClient()
        
        with patch('requests.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_request.return_value = mock_response
            
            response = client._make_request("GET", "https://api.steampowered.com/test")
            assert response.status_code == 200
    
    def test_make_request_with_api_key(self, monkeypatch):
        """Test that API key is added to GET requests."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        client = SteamClient()
        
        with patch('requests.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_request.return_value = mock_response
            
            client._make_request("GET", "https://api.steampowered.com/test")
            
            # Check that 'key' was added to params
            call_args = mock_request.call_args
            assert 'key' in call_args[1]['params']
            assert call_args[1]['params']['key'] == "test_key"
    
    def test_make_request_retry_on_429(self, monkeypatch):
        """Test retry on 429 rate limit."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        client = SteamClient(max_retries=2, backoff_factor=0.1)
        
        with patch('requests.request') as mock_request, \
             patch('time.sleep') as mock_sleep:
            # First request returns 429, second returns 200
            mock_response_429 = Mock()
            mock_response_429.status_code = 429
            mock_response_429.headers = {}
            
            mock_response_200 = Mock()
            mock_response_200.status_code = 200
            mock_response_200.json.return_value = {"ok": True}
            
            mock_request.side_effect = [mock_response_429, mock_response_200]
            
            response = client._make_request("GET", "https://api.steampowered.com/test")
            assert response.status_code == 200
            assert mock_request.call_count == 2
            mock_sleep.assert_called_once()
    
    def test_make_request_retry_on_500(self, monkeypatch):
        """Test retry on 500 server error."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        client = SteamClient(max_retries=2, backoff_factor=0.1)
        
        with patch('requests.request') as mock_request, \
             patch('time.sleep') as mock_sleep:
            # First request returns 500, second returns 200
            mock_response_500 = Mock()
            mock_response_500.status_code = 500
            
            mock_response_200 = Mock()
            mock_response_200.status_code = 200
            mock_response_200.json.return_value = {"ok": True}
            
            mock_request.side_effect = [mock_response_500, mock_response_200]
            
            response = client._make_request("GET", "https://api.steampowered.com/test")
            assert response.status_code == 200
            assert mock_request.call_count == 2
    
    def test_make_request_max_retries_exceeded(self, monkeypatch):
        """Test that exception is raised when max retries exceeded."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        client = SteamClient(max_retries=1, backoff_factor=0.1)
        
        with patch('requests.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_request.return_value = mock_response
            
            with pytest.raises(SteamAPIError):
                client._make_request("GET", "https://api.steampowered.com/test")
    
    def test_get_request(self, monkeypatch):
        """Test GET request with normalization."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        client = SteamClient()
        
        with patch('requests.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True, "test": "value"}
            mock_request.return_value = mock_response
            
            response = client.get("https://api.steampowered.com/test")
            assert isinstance(response, APIResponse)
            assert response.ok is True
            assert response.source == "steam_web_api"
    
    def test_get_request_error(self, monkeypatch):
        """Test GET request with error."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        client = SteamClient()
        
        with patch('requests.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Not found"
            mock_response.json.side_effect = Exception("Invalid JSON")
            mock_request.return_value = mock_response
            
            response = client.get("https://api.steampowered.com/test")
            assert isinstance(response, APIResponse)
            assert response.ok is False
            assert response.error is not None


class TestSingletonClient:
    """Test singleton client functionality."""
    
    def test_get_client_singleton(self, monkeypatch):
        """Test that get_client returns the same instance."""
        monkeypatch.setenv("STEAM_API_KEY", "test_key")
        
        from steam.client import get_client
        
        client1 = get_client()
        client2 = get_client()
        
        assert client1 is client2
