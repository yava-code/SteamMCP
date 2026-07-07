"""
Unified HTTP client for Steam API with retry logic, rate limiting, and error handling.

This module provides a centralized HTTP client that:
- Handles retries with exponential backoff
- Manages rate limiting (429 responses)
- Redacts secrets from error messages
- Provides consistent timeout handling
- Supports host allowlisting for security
"""

import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Union
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


class SteamAPIError(Exception):
    """Custom exception for Steam API errors."""
    
    def __init__(self, status_code: int, message: str | None = None, 
                 endpoint: str | None = None, source: str = "unknown"):
        self.status_code = status_code
        self.message = message or f"Steam API returned status code {status_code}"
        self.endpoint = endpoint
        self.source = source
        self.timestamp = datetime.now(timezone.utc).isoformat()
        
        # Redact any potential secrets from the message
        safe_message = self._redact_secrets(self.message)
        super().__init__(safe_message)
    
    @staticmethod
    def _redact_secrets(message: str) -> str:
        """Redact potential API keys from error messages."""
        import re
        # Redact anything that looks like an API key (32 hex chars)
        return re.sub(r'[A-Fa-f0-9]{32}', '[REDACTED]', message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON serialization."""
        return {
            "error": True,
            "status_code": self.status_code,
            "message": self.message,
            "endpoint": self.endpoint,
            "source": self.source,
            "timestamp": self.timestamp,
        }


class MarketAPIError(SteamAPIError):
    """Custom exception for Steam Market API errors."""
    
    def __init__(self, status_code: int, message: str | None = None,
                 endpoint: str | None = None):
        super().__init__(status_code, message, endpoint, source="market")


@dataclass
class APIResponse:
    """Normalized API response structure."""
    ok: bool
    source: str
    data: Dict[str, Any]
    warnings: List[str] = field(default_factory=list)
    fetched_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    rate_limit_hint: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "ok": self.ok,
            "source": self.source,
            "data": self.data,
            "warnings": self.warnings,
            "fetched_at": self.fetched_at,
        }
        if self.rate_limit_hint:
            result["rate_limit_hint"] = self.rate_limit_hint
        if self.error:
            result["error"] = self.error
        if self.summary:
            result["summary"] = self.summary
        return result


@dataclass
class RateLimitInfo:
    """Rate limit information from API responses."""
    remaining: Optional[int] = None
    reset_at: Optional[datetime] = None
    retry_after: Optional[int] = None
    limited: bool = False


class SteamClient:
    """
    Unified HTTP client for Steam API with retry logic and rate limiting.
    
    Features:
    - Configurable timeout
    - Exponential backoff for retries
    - Rate limit detection and handling
    - Host allowlisting for security
    - Secret redaction in error messages
    - Consistent response normalization
    
    Usage:
        client = SteamClient(api_key="your_key", timeout=10, max_retries=3)
        response = client.get("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/",
                              params={"steamids": "76561198006409530"})
    """
    
    # Default Steam API endpoints
    STEAM_API_BASE = "https://api.steampowered.com"
    STEAM_STORE_API_BASE = "https://store.steampowered.com/api"
    STEAM_COMMUNITY_BASE = "https://steamcommunity.com"
    
    # Allowed hosts for security
    ALLOWED_HOSTS = {
        "api.steampowered.com",
        "store.steampowered.com",
        "steamcommunity.com",
    }
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 10,
                 max_retries: int = 3, backoff_factor: float = 0.5,
                 allowed_hosts: Optional[Set[str]] = None):
        """
        Initialize the Steam client.
        
        Args:
            api_key: Steam Web API key (can also be set via STEAM_API_KEY env var)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff factor for exponential backoff
            allowed_hosts: Set of allowed hostnames (defaults to Steam endpoints)
        """
        self.api_key = api_key or os.getenv("STEAM_API_KEY")
        if not self.api_key:
            raise ValueError("STEAM_API_KEY is required. Set via constructor or STEAM_API_KEY environment variable.")
        
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.allowed_hosts = allowed_hosts or self.ALLOWED_HOSTS
        self._rate_limit_info: Dict[str, RateLimitInfo] = {}
        
        logger.info(f"SteamClient initialized with timeout={timeout}, max_retries={max_retries}")
    
    def _validate_host(self, url: str) -> None:
        """Validate that the URL host is in the allowlist."""
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        
        if host not in self.allowed_hosts:
            raise ValueError(f"Host {host} is not in the allowlist. Allowed hosts: {self.allowed_hosts}")
    
    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate backoff time using exponential backoff."""
        return self.backoff_factor * (2 ** attempt)
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make an HTTP request with retry logic and error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments for requests.request()
            
        Returns:
            requests.Response object
            
        Raises:
            SteamAPIError: If the request fails after all retries
        """
        self._validate_host(url)
        
        attempt = 0
        last_exception = None
        
        while attempt <= self.max_retries:
            try:
                # Add API key to params if it's a GET request
                if method.upper() == "GET" and "params" not in kwargs:
                    kwargs["params"] = {}
                if method.upper() == "GET" and "key" not in kwargs["params"]:
                    kwargs["params"]["key"] = self.api_key
                
                response = requests.request(method, url, timeout=self.timeout, **kwargs)
                
                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    wait_time = self._calculate_backoff(attempt)
                    actual_wait = max(wait_time, retry_after)
                    
                    logger.warning(f"Rate limited (429) for {url}. Waiting {actual_wait}s before retry (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(actual_wait)
                    attempt += 1
                    continue
                
                # Check for other rate limit indicators
                if response.status_code >= 500:
                    wait_time = self._calculate_backoff(attempt)
                    logger.warning(f"Server error ({response.status_code}) for {url}. Waiting {wait_time}s before retry (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                    attempt += 1
                    continue
                
                return response
                
            except requests.Timeout as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = self._calculate_backoff(attempt)
                    logger.warning(f"Timeout for {url}. Waiting {wait_time}s before retry (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                attempt += 1
                
            except requests.RequestException as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = self._calculate_backoff(attempt)
                    logger.warning(f"Request failed for {url}: {str(e)}. Waiting {wait_time}s before retry (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                attempt += 1
        
        # All retries exhausted
        if last_exception:
            raise SteamAPIError(500, f"Request failed after {self.max_retries} attempts: {str(last_exception)}")
        else:
            raise SteamAPIError(500, "Request failed after all retries")
    
    def get(self, url: str, **kwargs) -> APIResponse:
        """
        Make a GET request and return a normalized APIResponse.
        
        Args:
            url: Request URL
            **kwargs: Additional arguments for requests.get()
            
        Returns:
            APIResponse with normalized structure
        """
        try:
            response = self._make_request("GET", url, **kwargs)
            return self._normalize_response(response, url)
        except SteamAPIError as e:
            return APIResponse(
                ok=False,
                source=url,
                data={},
                warnings=[f"API error: {e.message}"],
                error=e.to_dict()
            )
    
    def post(self, url: str, **kwargs) -> APIResponse:
        """
        Make a POST request and return a normalized APIResponse.
        
        Args:
            url: Request URL
            **kwargs: Additional arguments for requests.post()
            
        Returns:
            APIResponse with normalized structure
        """
        try:
            response = self._make_request("POST", url, **kwargs)
            return self._normalize_response(response, url)
        except SteamAPIError as e:
            return APIResponse(
                ok=False,
                source=url,
                data={},
                warnings=[f"API error: {e.message}"],
                error=e.to_dict()
            )
    
    def _normalize_response(self, response: requests.Response, url: str) -> APIResponse:
        """
        Normalize a response into a consistent APIResponse structure.
        
        Args:
            response: requests.Response object
            url: Original request URL
            
        Returns:
            APIResponse with normalized structure
        """
        try:
            data = response.json()
        except Exception:
            data = {"raw_text": response.text}
        
        # Determine source from URL
        source = self._get_source_from_url(url)
        
        # Check for rate limit hints
        rate_limit_hint = self._extract_rate_limit_info(response)
        
        # Check for warnings
        warnings = self._extract_warnings(data, response)
        
        # Determine if response is OK
        # For Steam API, 200 with "ok": true means success
        is_ok = (response.status_code == 200 and 
                (isinstance(data, dict) and data.get("ok", False)))
        
        # For market endpoints, check different success indicators
        if "steamcommunity.com" in url:
            is_ok = response.status_code == 200
        
        return APIResponse(
            ok=is_ok,
            source=source,
            data=data,
            warnings=warnings,
            rate_limit_hint=rate_limit_hint.to_dict() if rate_limit_hint else None,
            error=None if is_ok else {
                "status_code": response.status_code,
                "message": response.text[:500]  # Limit error message size
            }
        )
    
    def _get_source_from_url(self, url: str) -> str:
        """Determine the source from the URL."""
        if "api.steampowered.com" in url:
            return "steam_web_api"
        elif "store.steampowered.com" in url:
            return "steam_store_api"
        elif "steamcommunity.com" in url:
            return "steam_community"
        return "unknown"
    
    def _extract_rate_limit_info(self, response: requests.Response) -> Optional[RateLimitInfo]:
        """Extract rate limit information from response headers."""
        if response.status_code != 429:
            return None
        
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                retry_after_int = int(retry_after)
            except ValueError:
                retry_after_int = None
        else:
            retry_after_int = None
        
        return RateLimitInfo(
            remaining=0,
            reset_at=None,
            retry_after=retry_after_int,
            limited=True
        )
    
    def _extract_warnings(self, data: Dict[str, Any], response: requests.Response) -> List[str]:
        """Extract warnings from response data."""
        warnings = []
        
        # Check for Steam API warnings
        if isinstance(data, dict):
            if not data.get("ok", True):
                warnings.append(f"API returned ok=false")
        
        # Check for rate limit warnings
        if response.status_code == 429:
            warnings.append("Rate limit encountered")
        
        return warnings


# Singleton client instance (optional usage)
_client: Optional[SteamClient] = None


def get_client(api_key: Optional[str] = None) -> SteamClient:
    """Get or create a singleton SteamClient instance."""
    global _client
    if _client is None:
        _client = SteamClient(api_key=api_key)
    return _client
