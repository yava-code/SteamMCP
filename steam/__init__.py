"""
Steam API client modules for SteamMCP.

This package contains:
- steam.client: Unified HTTP client with retry logic and rate limiting
- steam.schemas: Data models and response schemas
- steam.web: Steam Web API functions
- steam.store: Steam Store API functions  
- steam.market: Steam Community Market functions

Usage:
    from steam.client import SteamClient, APIResponse, SteamAPIError
    from steam.web import SteamWebAPI
    from steam.market import SteamMarketAPI
    from steam.store import SteamStoreAPI
    from steam.schemas import SteamProfile, Game, AppDetails, etc.
"""

from steam.client import SteamClient, APIResponse, SteamAPIError, MarketAPIError
from steam.web import SteamWebAPI
from steam.market import SteamMarketAPI
from steam.store import SteamStoreAPI
from steam import schemas

__all__ = [
    'SteamClient',
    'APIResponse', 
    'SteamAPIError',
    'MarketAPIError',
    'SteamWebAPI',
    'SteamMarketAPI',
    'SteamStoreAPI',
    'schemas',
]

# Create a default client instance for convenience
def get_default_client():
    """Get a default SteamClient instance using STEAM_API_KEY from environment."""
    return SteamClient()
