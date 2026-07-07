"""
Steam Web API functions.

This module provides functions for interacting with the Steam Web API:
- User profiles and information
- Friends lists
- Game achievements and stats
- Owned games
- News and updates
- Vanity URL resolution
"""

import logging
from typing import Any, Dict, List, Optional, Union

from steam.client import SteamClient, APIResponse
from steam.schemas import (
    SteamProfile, AppID, SteamID, Friend, Game, Achievement, GameNews, UserStats
)

logger = logging.getLogger(__name__)


class SteamWebAPI:
    """
    Client for Steam Web API operations.
    
    This class provides a high-level interface for Steam Web API endpoints
    with normalized responses and error handling.
    
    Usage:
        web = SteamWebAPI(api_key="your_key")
        profile = web.get_profile_info("76561198006409530")
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Steam Web API client.
        
        Args:
            api_key: Steam Web API key (optional, can also use STEAM_API_KEY env var)
        """
        self.client = SteamClient(api_key=api_key)
    
    def get_profile_info(self, steam_id: str) -> APIResponse:
        """
        Get Steam profile information for a user.
        
        Args:
            steam_id: Steam ID or vanity URL name
            
        Returns:
            APIResponse with profile data or error
        """
        SteamID.validate(steam_id)
        
        url = f"{self.client.STEAM_API_BASE}/ISteamUser/GetPlayerSummaries/v0002/"
        params = {"steamids": steam_id}
        
        response = self.client.get(url, params=params)
        
        # Normalize the response
        if response.ok and response.data.get("response", {}).get("players"):
            try:
                profile = SteamProfile.from_api_response(response.data)
                response.data = {"profile": profile.to_dict()}
            except Exception as e:
                logger.warning(f"Failed to parse profile: {e}")
        
        return response
    
    def get_friends(self, steam_id: str, relationship: str = "friend") -> APIResponse:
        """
        Get friend list for a Steam user.
        
        Args:
            steam_id: Steam ID of the user
            relationship: Relationship filter (friend, all)
            
        Returns:
            APIResponse with friends list or error
        """
        SteamID.validate(steam_id)
        
        if relationship not in ["friend", "all"]:
            return APIResponse(
                ok=False,
                source="steam_web_api",
                data={},
                warnings=["Invalid relationship parameter"],
                error={"message": "Relationship must be 'friend' or 'all'"}
            )
        
        url = f"{self.client.STEAM_API_BASE}/ISteamUser/GetFriendList/v0001/"
        params = {"steamid": steam_id, "relationship": relationship}
        
        response = self.client.get(url, params=params)
        
        # Normalize the response
        if response.ok:
            try:
                friends = Friend.from_api_response(response.data)
                response.data = {"friends": [f.to_dict() for f in friends]}
            except Exception as e:
                logger.warning(f"Failed to parse friends: {e}")
        
        return response
    
    def resolve_vanity_url(self, vanity_url_name: str) -> APIResponse:
        """
        Resolve a vanity URL to a Steam ID.
        
        Args:
            vanity_url_name: The vanity URL name to resolve
            
        Returns:
            APIResponse with resolved Steam ID or error
        """
        if not vanity_url_name or not isinstance(vanity_url_name, str):
            return APIResponse(
                ok=False,
                source="steam_web_api",
                data={},
                warnings=["Invalid vanity URL name"],
                error={"message": "Vanity URL name must be a non-empty string"}
            )
        
        url = f"{self.client.STEAM_API_BASE}/ISteamUser/ResolveVanityURL/v0001/"
        params = {"vanityurl": vanity_url_name}
        
        response = self.client.get(url, params=params)
        
        # Normalize the response
        if response.ok and response.data.get("response", {}).get("steamid"):
            steam_id = response.data["response"]["steamid"]
            response.data = {"steamid": steam_id}
        
        return response
    
    def get_player_achievements(self, steam_id: str, app_id: Union[str, int], 
                                language: str = "english") -> APIResponse:
        """
        Get player achievements for a specific game.
        
        Args:
            steam_id: Steam ID of the user
            app_id: Application ID of the game
            language: Language for achievement names and descriptions
            
        Returns:
            APIResponse with achievements data or error
        """
        SteamID.validate(steam_id)
        app_id = AppID.validate(app_id).appid
        
        url = f"{self.client.STEAM_API_BASE}/ISteamUserStats/GetPlayerAchievements/v0001/"
        params = {"steamid": steam_id, "appid": app_id, "l": language}
        
        response = self.client.get(url, params=params)
        
        # Normalize the response
        if response.ok:
            try:
                achievements = Achievement.from_api_response(response.data)
                response.data = {"achievements": [a.to_dict() for a in achievements]}
            except Exception as e:
                logger.warning(f"Failed to parse achievements: {e}")
        
        return response
    
    def get_user_stats_for_game(self, steam_id: str, app_id: Union[str, int]) -> APIResponse:
        """
        Get user stats for a specific game.
        
        Args:
            steam_id: Steam ID of the user
            app_id: Application ID of the game
            
        Returns:
            APIResponse with user stats data or error
        """
        SteamID.validate(steam_id)
        app_id = AppID.validate(app_id).appid
        
        url = f"{self.client.STEAM_API_BASE}/ISteamUserStats/GetUserStatsForGame/v0002/"
        params = {"steamid": steam_id, "appid": app_id}
        
        response = self.client.get(url, params=params)
        
        # Normalize the response
        if response.ok:
            try:
                user_stats = UserStats.from_api_response(response.data, steam_id, app_id)
                response.data = {"stats": user_stats.to_dict()}
            except Exception as e:
                logger.warning(f"Failed to parse user stats: {e}")
        
        return response
    
    def get_owned_games(self, steam_id: str, include_appinfo: bool = True, 
                       include_played_free_games: bool = True) -> APIResponse:
        """
        Get list of games owned by a user.
        
        Args:
            steam_id: Steam ID of the user
            include_appinfo: Include game name and other info
            include_played_free_games: Include free games that the user has played
            
        Returns:
            APIResponse with owned games data or error
        """
        SteamID.validate(steam_id)
        
        url = f"{self.client.STEAM_API_BASE}/IPlayerService/GetOwnedGames/v0001/"
        params = {
            "steamid": steam_id,
            "format": "json",
            "include_appinfo": int(include_appinfo),
            "include_played_free_games": int(include_played_free_games),
        }
        
        response = self.client.get(url, params=params)
        
        # Normalize the response
        if response.ok:
            try:
                games = Game.from_api_response(response.data)
                response.data = {"games": [g.to_dict() for g in games]}
            except Exception as e:
                logger.warning(f"Failed to parse owned games: {e}")
        
        return response
    
    def get_recently_played_games(self, steam_id: str, count: int = 10) -> APIResponse:
        """
        Get recently played games for a user.
        
        Args:
            steam_id: Steam ID of the user
            count: Number of games to return
            
        Returns:
            APIResponse with recently played games data or error
        """
        SteamID.validate(steam_id)
        
        if count <= 0 or count > 100:
            return APIResponse(
                ok=False,
                source="steam_web_api",
                data={},
                warnings=["Invalid count parameter"],
                error={"message": "Count must be between 1 and 100"}
            )
        
        url = f"{self.client.STEAM_API_BASE}/IPlayerService/GetRecentlyPlayedGames/v0001/"
        params = {"steamid": steam_id, "format": "json", "count": count}
        
        response = self.client.get(url, params=params)
        
        # Normalize the response
        if response.ok:
            try:
                games = Game.from_api_response(response.data)
                response.data = {"games": [g.to_dict() for g in games]}
            except Exception as e:
                logger.warning(f"Failed to parse recently played games: {e}")
        
        return response
    
    def get_game_news(self, app_id: Union[str, int], count: int = 3, 
                      maxlength: int = 300, feed_name: Optional[str] = None) -> APIResponse:
        """
        Get news articles for a game.
        
        Args:
            app_id: Application ID of the game
            count: Number of news items to return
            maxlength: Maximum length of each news item
            feed_name: Name of the feed to get news from
            
        Returns:
            APIResponse with game news data or error
        """
        app_id = AppID.validate(app_id).appid
        
        if count <= 0:
            return APIResponse(
                ok=False,
                source="steam_web_api",
                data={},
                warnings=["Invalid count parameter"],
                error={"message": "Count must be positive"}
            )
        
        url = f"{self.client.STEAM_API_BASE}/ISteamNews/GetNewsForApp/v0002/"
        params = {"appid": app_id, "count": count, "maxlength": maxlength, "format": "json"}
        
        if feed_name:
            params["feedname"] = feed_name
        
        response = self.client.get(url, params=params)
        
        # Normalize the response
        if response.ok:
            try:
                news = GameNews.from_api_response(response.data)
                response.data = {"news": [n.to_dict() for n in news]}
            except Exception as e:
                logger.warning(f"Failed to parse game news: {e}")
        
        return response
    
    def get_game_schema(self, app_id: Union[str, int], language: str = "english") -> APIResponse:
        """
        Get schema for a specific game (achievements and stats).
        
        Args:
            app_id: Application ID of the game
            language: Language for achievement names and descriptions
            
        Returns:
            APIResponse with game schema data or error
        """
        app_id = AppID.validate(app_id).appid
        
        url = f"{self.client.STEAM_API_BASE}/ISteamUserStats/GetSchemaForGame/v2/"
        params = {"appid": app_id, "l": language}
        
        response = self.client.get(url, params=params)
        return response
    
    def get_app_details(self, app_id: Union[str, int], country_code: str = "US") -> APIResponse:
        """
        Get detailed information about a game from the Steam Store API.
        
        Args:
            app_id: Application ID
            country_code: Country code for pricing and availability
            
        Returns:
            APIResponse with app details data or error
        """
        app_id = AppID.validate(app_id).appid
        
        url = f"{self.client.STEAM_STORE_API_BASE}/appdetails"
        params = {"appids": app_id, "cc": country_code, "l": "english"}
        
        response = self.client.get(url, params=params)
        
        # Normalize the response
        if response.ok:
            try:
                from steam.schemas import AppDetails
                app_details = AppDetails.from_api_response(response.data, app_id)
                response.data = {"app": app_details.to_dict()}
            except Exception as e:
                logger.warning(f"Failed to parse app details: {e}")
        
        return response
    
    def get_global_achievement_percentages(self, app_id: Union[str, int]) -> APIResponse:
        """
        Get global achievement completion percentages for a game.
        
        Args:
            app_id: Application ID of the game
            
        Returns:
            APIResponse with global achievement percentages data or error
        """
        app_id = AppID.validate(app_id).appid
        
        url = f"{self.client.STEAM_API_BASE}/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/"
        params = {"gameid": app_id, "format": "json"}
        
        response = self.client.get(url, params=params)
        return response
    
    def get_user_level(self, steam_id: str) -> APIResponse:
        """
        Get Steam user level.
        
        Args:
            steam_id: Steam ID of the user
            
        Returns:
            APIResponse with user level data or error
        """
        SteamID.validate(steam_id)
        
        url = f"{self.client.STEAM_API_BASE}/IPlayerService/GetSteamLevel/v1/"
        params = {"steamid": steam_id}
        
        response = self.client.get(url, params=params)
        return response
    
    def get_user_badges(self, steam_id: str) -> APIResponse:
        """
        Get badges owned by a Steam user.
        
        Args:
            steam_id: Steam ID of the user
            
        Returns:
            APIResponse with user badges data or error
        """
        SteamID.validate(steam_id)
        
        url = f"{self.client.STEAM_API_BASE}/IPlayerService/GetBadges/v1/"
        params = {"steamid": steam_id}
        
        response = self.client.get(url, params=params)
        return response
    
    def get_player_bans(self, steam_id: str) -> APIResponse:
        """
        Get player bans information.
        
        Args:
            steam_id: Steam ID of the user
            
        Returns:
            APIResponse with player bans data or error
        """
        SteamID.validate(steam_id)
        
        url = f"{self.client.STEAM_API_BASE}/ISteamUser/GetPlayerBans/v1/"
        params = {"steamids": steam_id}
        
        response = self.client.get(url, params=params)
        return response
    
    def get_player_summaries(self, steam_ids: List[str]) -> APIResponse:
        """
        Get summaries for multiple Steam users.
        
        Args:
            steam_ids: List of Steam IDs
            
        Returns:
            APIResponse with player summaries data or error
        """
        if not steam_ids:
            return APIResponse(
                ok=False,
                source="steam_web_api",
                data={},
                warnings=["Empty steam_ids list"],
                error={"message": "steam_ids must be a non-empty list"}
            )
        
        url = f"{self.client.STEAM_API_BASE}/ISteamUser/GetPlayerSummaries/v0002/"
        params = {"steamids": ",".join(steam_ids)}
        
        response = self.client.get(url, params=params)
        return response
    
    def get_current_players(self, app_id: Union[str, int]) -> APIResponse:
        """
        Get current player count for a game.
        
        Args:
            app_id: Application ID of the game
            
        Returns:
            APIResponse with current player count data or error
        """
        app_id = AppID.validate(app_id).appid
        
        url = f"{self.client.STEAM_API_BASE}/ISteamUserStats/GetNumberOfCurrentPlayers/v0001/"
        params = {"appid": app_id}
        
        response = self.client.get(url, params=params)
        
        # Normalize the response
        if response.ok:
            try:
                from steam.schemas import PlayerCount
                player_count = PlayerCount.from_api_response(response.data, app_id)
                response.data = {"player_count": player_count.to_dict()}
            except Exception as e:
                logger.warning(f"Failed to parse player count: {e}")
        
        return response
