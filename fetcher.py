from dotenv import load_dotenv
import os
import requests
import logging
from typing import Dict, List, Optional, Union, Any
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv("STEAM_API_KEY")

if not api_key:
    logger.error("STEAM_API_KEY not found in environment variables")
    raise ValueError("STEAM_API_KEY not found in environment variables")

# Base API URLs
STEAM_API_BASE = "http://api.steampowered.com"
STEAM_STORE_API_BASE = "https://store.steampowered.com/api"

class SteamAPIError(Exception):
    """Custom exception for Steam API errors"""
    def __init__(self, status_code: int, message: str = None):
        self.status_code = status_code
        self.message = message or f"Steam API returned status code {status_code}"
        super().__init__(self.message)

def _make_request(url: str, params: Dict = None, retries: int = 3, backoff_factor: float = 0.5) -> Dict:
    """
    Make a request to the Steam API with retry logic and error handling
    
    Args:
        url: The API endpoint URL
        params: Query parameters for the request
        retries: Number of retry attempts
        backoff_factor: Backoff factor for retries
        
    Returns:
        Dict: JSON response from the API
        
    Raises:
        SteamAPIError: If the API returns an error status code
    """
    attempt = 0
    while attempt < retries:
        try:
            logger.debug(f"Making request to {url} with params {params}")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limited, wait and retry
                wait_time = backoff_factor * (2 ** attempt)
                logger.warning(f"Rate limited. Waiting {wait_time} seconds before retry.")
                time.sleep(wait_time)
                attempt += 1
                continue
            else:
                logger.error(f"API request failed with status code {response.status_code}: {response.text}")
                raise SteamAPIError(response.status_code, response.text)
        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            if attempt < retries - 1:
                wait_time = backoff_factor * (2 ** attempt)
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                attempt += 1
            else:
                raise SteamAPIError(500, f"Request failed after {retries} attempts: {str(e)}")
    
    raise SteamAPIError(500, f"Request failed after {retries} attempts")

def validate_steam_id(steam_id: str) -> str:
    """
    Validate Steam ID format
    
    Args:
        steam_id: Steam ID to validate
        
    Returns:
        str: Validated Steam ID
        
    Raises:
        ValueError: If Steam ID is invalid
    """
    if not steam_id or not isinstance(steam_id, str):
        raise ValueError("Steam ID must be a non-empty string")
    
    # Basic validation - Steam IDs are typically 17 digits
    if len(steam_id) != 17 or not steam_id.isdigit():
        logger.warning(f"Steam ID {steam_id} may not be valid (should be 17 digits)")
    
    return steam_id

def validate_app_id(app_id: Union[str, int]) -> int:
    """
    Validate app ID format
    
    Args:
        app_id: App ID to validate
        
    Returns:
        int: Validated app ID
        
    Raises:
        ValueError: If app ID is invalid
    """
    if isinstance(app_id, str):
        if not app_id.isdigit():
            raise ValueError("App ID must be a numeric string")
        app_id = int(app_id)
    
    if not isinstance(app_id, int) or app_id <= 0:
        raise ValueError("App ID must be a positive integer")
    
    return app_id

def fetch_steam_profile(steam_id: str) -> Dict:
    """
    Fetch Steam user profile information
    
    Args:
        steam_id: Steam ID of the user
        
    Returns:
        Dict: User profile data
    """
    steam_id = validate_steam_id(steam_id)
    
    url = f"{STEAM_API_BASE}/ISteamUser/GetPlayerSummaries/v0002/"
    params = {
        "key": api_key,
        "steamids": steam_id
    }
    
    return _make_request(url, params)

def fetch_friend_list(steam_id: str, relationship: str = "friend") -> Dict:
    """
    Fetch a user's friend list
    
    Args:
        steam_id: Steam ID of the user
        relationship: Relationship filter (friend, all)
        
    Returns:
        Dict: Friend list data
    """
    steam_id = validate_steam_id(steam_id)
    
    if relationship not in ["friend", "all"]:
        raise ValueError("Relationship must be 'friend' or 'all'")
    
    url = f"{STEAM_API_BASE}/ISteamUser/GetFriendList/v0001/"
    params = {
        "key": api_key,
        "steamid": steam_id,
        "relationship": relationship
    }
    
    return _make_request(url, params)

def fetch_player_achievements(steam_id: str, app_id: Union[str, int], language: str = "english") -> Dict:
    """
    Fetch player achievements for a specific game
    
    Args:
        steam_id: Steam ID of the user
        app_id: Application ID of the game
        language: Language for achievement names and descriptions
        
    Returns:
        Dict: Player achievements data
    """
    steam_id = validate_steam_id(steam_id)
    app_id = validate_app_id(app_id)
    
    url = f"{STEAM_API_BASE}/ISteamUserStats/GetPlayerAchievements/v0001/"
    params = {
        "key": api_key,
        "steamid": steam_id,
        "appid": app_id,
        "l": language
    }
    
    return _make_request(url, params)

def fetch_user_stats_for_game(steam_id: str, app_id: Union[str, int]) -> Dict:
    """
    Fetch user stats for a specific game
    
    Args:
        steam_id: Steam ID of the user
        app_id: Application ID of the game
        
    Returns:
        Dict: User game stats data
    """
    steam_id = validate_steam_id(steam_id)
    app_id = validate_app_id(app_id)
    
    url = f"{STEAM_API_BASE}/ISteamUserStats/GetUserStatsForGame/v0002/"
    params = {
        "key": api_key,
        "steamid": steam_id,
        "appid": app_id
    }
    
    return _make_request(url, params)

def fetch_owned_games(steam_id: str, include_appinfo: bool = True, include_played_free_games: bool = True) -> Dict:
    """
    Fetch a list of games owned by the user
    
    Args:
        steam_id: Steam ID of the user
        include_appinfo: Include game name and other info
        include_played_free_games: Include free games that the user has played
        
    Returns:
        Dict: Owned games data
    """
    steam_id = validate_steam_id(steam_id)
    
    url = f"{STEAM_API_BASE}/IPlayerService/GetOwnedGames/v0001/"
    params = {
        "key": api_key,
        "steamid": steam_id,
        "format": "json",
        "include_appinfo": int(include_appinfo),
        "include_played_free_games": int(include_played_free_games)
    }
    
    return _make_request(url, params)

def fetch_recently_played_games(steam_id: str, count: int = 10) -> Dict:
    """
    Fetch recently played games for a user
    
    Args:
        steam_id: Steam ID of the user
        count: Number of games to return
        
    Returns:
        Dict: Recently played games data
    """
    steam_id = validate_steam_id(steam_id)
    
    if count <= 0 or count > 100:
        raise ValueError("Count must be between 1 and 100")
    
    url = f"{STEAM_API_BASE}/IPlayerService/GetRecentlyPlayedGames/v0001/"
    params = {
        "key": api_key,
        "steamid": steam_id,
        "format": "json",
        "count": count
    }
    
    return _make_request(url, params)

def fetch_game_news(app_id: Union[str, int], count: int = 3, max_length: int = 300, feed_name: str = None) -> Dict:
    """
    Fetch news articles for a game
    
    Args:
        app_id: Application ID of the game
        count: Number of news items to return
        max_length: Maximum length of each news item
        feed_name: Name of the feed to get news from
        
    Returns:
        Dict: Game news data
    """
    app_id = validate_app_id(app_id)
    
    if count <= 0:
        raise ValueError("Count must be positive")
    
    url = f"{STEAM_API_BASE}/ISteamNews/GetNewsForApp/v0002/"
    params = {
        "appid": app_id,
        "count": count,
        "maxlength": max_length,
        "format": "json"
    }
    
    if feed_name:
        params["feedname"] = feed_name
    
    return _make_request(url, params)

def fetch_game_schema(app_id: Union[str, int], language: str = "english") -> Dict:
    """
    Fetch game schema including achievements and stats
    
    Args:
        app_id: Application ID of the game
        language: Language for achievement names and descriptions
        
    Returns:
        Dict: Game schema data
    """
    app_id = validate_app_id(app_id)
    
    url = f"{STEAM_API_BASE}/ISteamUserStats/GetSchemaForGame/v2/"
    params = {
        "key": api_key,
        "appid": app_id,
        "l": language
    }
    
    return _make_request(url, params)

def fetch_app_details(app_id: Union[str, int], country_code: str = "US") -> Dict:
    """
    Fetch detailed information about a game from the Steam Store API
    
    Args:
        app_id: Application ID of the game
        country_code: Country code for pricing and availability
        
    Returns:
        Dict: App details data
    """
    app_id = validate_app_id(app_id)
    
    url = f"{STEAM_STORE_API_BASE}/appdetails"
    params = {
        "appids": app_id,
        "cc": country_code,
        "l": "english"
    }
    
    return _make_request(url, params)

def fetch_global_achievement_percentages(app_id: Union[str, int]) -> Dict:
    """
    Fetch global achievement completion percentages for a game
    
    Args:
        app_id: Application ID of the game
        
    Returns:
        Dict: Global achievement percentages data
    """
    app_id = validate_app_id(app_id)
    
    url = f"{STEAM_API_BASE}/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/"
    params = {
        "gameid": app_id,
        "format": "json"
    }
    
    return _make_request(url, params)

def fetch_user_level(steam_id: str) -> Dict:
    """
    Fetch Steam user level
    
    Args:
        steam_id: Steam ID of the user
        
    Returns:
        Dict: User level data
    """
    steam_id = validate_steam_id(steam_id)
    
    url = f"{STEAM_API_BASE}/IPlayerService/GetSteamLevel/v1/"
    params = {
        "key": api_key,
        "steamid": steam_id
    }
    
    return _make_request(url, params)

def fetch_user_badges(steam_id: str) -> Dict:
    """
    Fetch badges owned by a Steam user
    
    Args:
        steam_id: Steam ID of the user
        
    Returns:
        Dict: User badges data
    """
    steam_id = validate_steam_id(steam_id)
    
    url = f"{STEAM_API_BASE}/IPlayerService/GetBadges/v1/"
    params = {
        "key": api_key,
        "steamid": steam_id
    }
    
    return _make_request(url, params)

def resolve_vanity_url(vanity_url_name: str) -> Dict:
    """
    Resolve a vanity URL to a Steam ID
    
    Args:
        vanity_url_name: The vanity URL name to resolve
        
    Returns:
        Dict: Resolution data including steamid if successful
    """
    if not vanity_url_name or not isinstance(vanity_url_name, str):
        raise ValueError("Vanity URL name must be a non-empty string")
    
    url = f"{STEAM_API_BASE}/ISteamUser/ResolveVanityURL/v0001/"
    params = {
        "key": api_key,
        "vanityurl": vanity_url_name
    }
    
    return _make_request(url, params)
