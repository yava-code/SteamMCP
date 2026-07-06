"""
Data schemas and models for Steam API responses.

This module provides:
- Dataclasses for normalized API responses
- Type hints for common Steam data structures
- Validation utilities
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


@dataclass
class SteamID:
    """Represents a Steam ID."""
    steamid: str
    
    @classmethod
    def validate(cls, steamid: str) -> 'SteamID':
        """Validate and create a SteamID instance."""
        if not steamid or not isinstance(steamid, str):
            raise ValueError("Steam ID must be a non-empty string")
        
        # Basic validation: usually 17 digits
        if len(steamid) != 17 or not steamid.isdigit():
            # Allow non-standard formats but warn
            pass
        
        return cls(steamid=steamid)


@dataclass
class AppID:
    """Represents a Steam App ID."""
    appid: int
    
    @classmethod
    def validate(cls, appid: Union[str, int]) -> 'AppID':
        """Validate and create an AppID instance."""
        if isinstance(appid, str):
            if not appid.isdigit():
                raise ValueError("App ID must be a numeric string")
            appid = int(appid)
        
        if not isinstance(appid, int) or appid <= 0:
            raise ValueError("App ID must be a positive integer")
        
        return cls(appid=appid)


@dataclass
class SteamProfile:
    """Normalized Steam user profile data."""
    steamid: str
    personaname: str
    profileurl: Optional[str] = None
    personastate: Optional[int] = None
    communityvisibilitystate: Optional[int] = None
    profilestate: Optional[int] = None
    lastlogoff: Optional[int] = None
    commentpermission: Optional[int] = None
    realname: Optional[str] = None
    primaryclanid: Optional[str] = None
    timecreated: Optional[int] = None
    gameid: Optional[int] = None
    gameserverip: Optional[str] = None
    gameextrainfo: Optional[str] = None
    cityid: Optional[int] = None
    loccountrycode: Optional[str] = None
    locstatecode: Optional[str] = None
    loccityid: Optional[int] = None
    avatar: Optional[str] = None
    avatarmedium: Optional[str] = None
    avatarfull: Optional[str] = None
    avatarhash: Optional[str] = None
    laststeamid: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'SteamProfile':
        """Create a SteamProfile from Steam API response."""
        response = data.get("response", {})
        players = response.get("players", [])
        
        if not players:
            raise ValueError("No player data in response")
        
        player = players[0]
        return cls(
            steamid=player.get("steamid", ""),
            personaname=player.get("personaname", ""),
            profileurl=player.get("profileurl"),
            personastate=player.get("personastate"),
            communityvisibilitystate=player.get("communityvisibilitystate"),
            profilestate=player.get("profilestate"),
            lastlogoff=player.get("lastlogoff"),
            commentpermission=player.get("commentpermission"),
            realname=player.get("realname"),
            primaryclanid=player.get("primaryclanid"),
            timecreated=player.get("timecreated"),
            gameid=player.get("gameid"),
            gameserverip=player.get("gameserverip"),
            gameextrainfo=player.get("gameextrainfo"),
            cityid=player.get("cityid"),
            loccountrycode=player.get("loccountrycode"),
            locstatecode=player.get("locstatecode"),
            loccityid=player.get("loccityid"),
            avatar=player.get("avatar"),
            avatarmedium=player.get("avatarmedium"),
            avatarfull=player.get("avatarfull"),
            avatarhash=player.get("avatarhash"),
            laststeamid=player.get("laststeamid"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "steamid": self.steamid,
            "personaname": self.personaname,
            "profileurl": self.profileurl,
            "personastate": self.personastate,
            "communityvisibilitystate": self.communityvisibilitystate,
            "profilestate": self.profilestate,
            "lastlogoff": self.lastlogoff,
            "commentpermission": self.commentpermission,
            "realname": self.realname,
            "primaryclanid": self.primaryclanid,
            "timecreated": self.timecreated,
            "gameid": self.gameid,
            "gameserverip": self.gameserverip,
            "gameextrainfo": self.gameextrainfo,
            "cityid": self.cityid,
            "loccountrycode": self.loccountrycode,
            "locstatecode": self.locstatecode,
            "loccityid": self.loccityid,
            "avatar": self.avatar,
            "avatarmedium": self.avatarmedium,
            "avatarfull": self.avatarfull,
            "avatarhash": self.avatarhash,
            "laststeamid": self.laststeamid,
        }


@dataclass
class Friend:
    """Represents a Steam friend relationship."""
    steamid: str
    relationship: str
    friend_since: int
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> List['Friend']:
        """Create Friend list from Steam API response."""
        friends_list = data.get("friendslist", {}).get("friends", [])
        return [
            cls(
                steamid=f.get("steamid", ""),
                relationship=f.get("relationship", ""),
                friend_since=f.get("friend_since", 0)
            )
            for f in friends_list
        ]


@dataclass
class Game:
    """Represents a Steam game."""
    appid: int
    name: str
    playtime_forever: int = 0
    img_icon_url: Optional[str] = None
    img_logo_url: Optional[str] = None
    has_community_visible_stats: bool = False
    playtime_windows_forever: Optional[Dict[str, int]] = None
    playtime_2weeks: Optional[int] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> List['Game']:
        """Create Game list from Steam API response."""
        games = data.get("response", {}).get("games", [])
        return [
            cls(
                appid=g.get("appid", 0),
                name=g.get("name", ""),
                playtime_forever=g.get("playtime_forever", 0),
                img_icon_url=g.get("img_icon_url"),
                img_logo_url=g.get("img_logo_url"),
                has_community_visible_stats=g.get("has_community_visible_stats", False),
                playtime_windows_forever=g.get("playtime_windows_forever"),
                playtime_2weeks=g.get("playtime_2weeks"),
            )
            for g in games
        ]


@dataclass
class Achievement:
    """Represents a Steam achievement."""
    apiname: str
    achieved: bool
    unlocktime: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> List['Achievement']:
        """Create Achievement list from Steam API response."""
        achievements = data.get("playerstats", {}).get("achievements", [])
        return [
            cls(
                apiname=a.get("apiname", ""),
                achieved=a.get("achieved", False),
                unlocktime=a.get("unlocktime"),
                name=a.get("name"),
                description=a.get("description"),
            )
            for a in achievements
        ]


@dataclass
class GameNews:
    """Represents a Steam game news item."""
    gid: str
    title: str
    url: str
    is_external_url: bool
    author: str
    contents: str
    feedlabel: str
    date: int
    feedname: str
    feed_type: int
    appid: Optional[int] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> List['GameNews']:
        """Create GameNews list from Steam API response."""
        news_items = data.get("appnews", {}).get("newsitems", [])
        return [
            cls(
                gid=n.get("gid", ""),
                title=n.get("title", ""),
                url=n.get("url", ""),
                is_external_url=n.get("is_external_url", False),
                author=n.get("author", ""),
                contents=n.get("contents", ""),
                feedlabel=n.get("feedlabel", ""),
                date=n.get("date", 0),
                feedname=n.get("feedname", ""),
                feed_type=n.get("feed_type", 0),
                appid=n.get("appid"),
            )
            for n in news_items
        ]


@dataclass
class AppDetails:
    """Represents Steam Store app details."""
    appid: int
    name: Optional[str] = None
    is_free: bool = False
    price_overview: Optional[Dict[str, Any]] = None
    header_image: Optional[str] = None
    capsule_image: Optional[str] = None
    capsule_imagev5: Optional[str] = None
    short_description: Optional[str] = None
    detailed_description: Optional[str] = None
    about_the_game: Optional[str] = None
    supported_languages: Optional[str] = None
    reviews: Optional[str] = None
    header_image: Optional[str] = None
    website: Optional[str] = None
    pc_requirements: Optional[Dict[str, str]] = None
    mac_requirements: Optional[Dict[str, str]] = None
    linux_requirements: Optional[Dict[str, str]] = None
    developers: Optional[List[str]] = None
    publishers: Optional[List[str]] = None
    demo: Optional[Dict[str, Any]] = None
    release_date: Optional[Dict[str, str]] = None
    support_info: Optional[Dict[str, Any]] = None
    background: Optional[str] = None
    background_raw: Optional[str] = None
    content_descriptors: Optional[Dict[str, Any]] = None
    screenshots: Optional[List[Dict[str, Any]]] = None
    movies: Optional[List[Dict[str, Any]]] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any], appid: int) -> 'AppDetails':
        """Create AppDetails from Steam Store API response."""
        app_data = data.get(str(appid), {})
        if not app_data.get("success", False):
            raise ValueError(f"Failed to get app details for appid {appid}")
        
        app_info = app_data.get("data", {})
        return cls(
            appid=appid,
            name=app_info.get("name"),
            is_free=app_info.get("is_free", False),
            price_overview=app_info.get("price_overview"),
            header_image=app_info.get("header_image"),
            capsule_image=app_info.get("capsule_image"),
            capsule_imagev5=app_info.get("capsule_imagev5"),
            short_description=app_info.get("short_description"),
            detailed_description=app_info.get("detailed_description"),
            about_the_game=app_info.get("about_the_game"),
            supported_languages=app_info.get("supported_languages"),
            reviews=app_info.get("reviews"),
            website=app_info.get("website"),
            pc_requirements=app_info.get("pc_requirements"),
            mac_requirements=app_info.get("mac_requirements"),
            linux_requirements=app_info.get("linux_requirements"),
            developers=app_info.get("developers"),
            publishers=app_info.get("publishers"),
            demo=app_info.get("demo"),
            release_date=app_info.get("release_date"),
            support_info=app_info.get("support_info"),
            background=app_info.get("background"),
            background_raw=app_info.get("background_raw"),
            content_descriptors=app_info.get("content_descriptors"),
            screenshots=app_info.get("screenshots"),
            movies=app_info.get("movies"),
        )


@dataclass
class PlayerCount:
    """Represents current player count for a game."""
    appid: int
    current_players: int
    current_24h_peak: int
    current_all_time_peak: int
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any], appid: int) -> 'PlayerCount':
        """Create PlayerCount from Steam API response."""
        response = data.get("response", {})
        return cls(
            appid=appid,
            current_players=response.get("player_count", 0),
            current_24h_peak=response.get("result_cache", {}).get("24hour", {}).get("peak", 0),
            current_all_time_peak=response.get("result_cache", {}).get("alltime", {}).get("peak", 0),
        )


@dataclass
class UserStats:
    """Represents user game statistics."""
    steamid: str
    game_name: str
    stats: Dict[str, Any] = field(default_factory=dict)
    achievements: List[Achievement] = field(default_factory=list)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any], steamid: str, appid: int) -> 'UserStats':
        """Create UserStats from Steam API response."""
        player_stats = data.get("playerstats", {})
        return cls(
            steamid=steamid,
            game_name=player_stats.get("gameName", ""),
            stats=player_stats.get("stats", {}),
            achievements=Achievement.from_api_response(data)
        )


@dataclass
class MarketItem:
    """Represents a Steam Community Market item."""
    name: str
    hash_name: str
    sell_price: Optional[float] = None
    sell_price_text: Optional[str] = None
    app_name: Optional[str] = None
    type: Optional[str] = None
    market_name: Optional[str] = None
    appid: Optional[int] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> List['MarketItem']:
        """Create MarketItem list from Steam Market API response."""
        results = data.get("results", [])
        return [
            cls(
                name=r.get("name", ""),
                hash_name=r.get("hash_name", ""),
                sell_price=r.get("sell_price"),
                sell_price_text=r.get("sell_price_text"),
                app_name=r.get("app_name"),
                type=r.get("type"),
                market_name=r.get("market_name"),
                appid=r.get("appid"),
            )
            for r in results
        ]


@dataclass
class PriceOverview:
    """Represents price overview for a market item."""
    success: bool
    lowest_price: Optional[str] = None
    median_price: Optional[str] = None
    volume: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'PriceOverview':
        """Create PriceOverview from Steam Market API response."""
        return cls(
            success=data.get("success", False),
            lowest_price=data.get("lowest_price"),
            median_price=data.get("median_price"),
            volume=data.get("volume"),
        )


@dataclass
class PriceHistory:
    """Represents price history for a market item."""
    success: bool
    price_prefix: Optional[str] = None
    price_suffix: Optional[str] = None
    prices: List[List[Any]] = field(default_factory=list)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'PriceHistory':
        """Create PriceHistory from Steam Market API response."""
        return cls(
            success=data.get("success", False),
            price_prefix=data.get("price_prefix"),
            price_suffix=data.get("price_suffix"),
            prices=data.get("prices", []),
        )
