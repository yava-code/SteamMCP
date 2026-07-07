"""
Real-time price tracking for Steam Store.

This module provides functionality for:
- Tracking price history for apps
- Detecting price changes
- Notifying about discounts
- Comparing prices across regions
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union

from steam.client import SteamClient, APIResponse
from steam.schemas import AppID
from steam.cache import app_cache

logger = logging.getLogger(__name__)


@dataclass
class PricePoint:
    """A single price data point in time."""
    appid: int
    currency: str
    initial_price: float
    final_price: float
    discount_percent: int
    timestamp: datetime
    is_on_sale: bool = False
    
    @classmethod
    def from_api_data(cls, appid: int, price_data: Dict[str, Any], currency: str = "USD") -> 'PricePoint':
        """Create PricePoint from Steam API price data."""
        initial = price_data.get("initial", 0) / 100.0 if price_data.get("initial") else 0
        final = price_data.get("final", 0) / 100.0 if price_data.get("final") else 0
        discount = price_data.get("discount_percent", 0)
        is_on_sale = discount > 0
        
        return cls(
            appid=appid,
            currency=currency,
            initial_price=initial,
            final_price=final,
            discount_percent=discount,
            timestamp=datetime.now(timezone.utc),
            is_on_sale=is_on_sale
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "appid": self.appid,
            "currency": self.currency,
            "initial_price": self.initial_price,
            "final_price": self.final_price,
            "discount_percent": self.discount_percent,
            "timestamp": self.timestamp.isoformat(),
            "is_on_sale": self.is_on_sale
        }


@dataclass
class PriceHistory:
    """Price history for a specific app."""
    appid: int
    currency: str
    price_points: List[PricePoint] = field(default_factory=list)
    current_price: Optional[PricePoint] = None
    lowest_price: Optional[float] = None
    highest_price: Optional[float] = None
    
    def add_price_point(self, price_point: PricePoint) -> None:
        """Add a new price point to the history."""
        self.price_points.append(price_point)
        self.price_points.sort(key=lambda p: p.timestamp)
        
        # Update current price
        if self.current_price is None or price_point.timestamp > self.current_price.timestamp:
            self.current_price = price_point
        
        # Update stats
        prices = [p.final_price for p in self.price_points if p.final_price > 0]
        if prices:
            self.lowest_price = min(prices)
            self.highest_price = max(prices)
    
    def get_price_change(self) -> Optional[Dict[str, Any]]:
        """Get the most recent price change."""
        if len(self.price_points) < 2:
            return None
        
        latest = self.price_points[-1]
        previous = self.price_points[-2]
        
        change = latest.final_price - previous.final_price
        change_percent = (change / previous.final_price * 100) if previous.final_price > 0 else 0
        
        return {
            "old_price": previous.final_price,
            "new_price": latest.final_price,
            "change": change,
            "change_percent": change_percent,
            "is_increase": change > 0,
            "is_decrease": change < 0,
            "timestamp": latest.timestamp.isoformat()
        }
    
    def is_on_sale_now(self) -> bool:
        """Check if the app is currently on sale."""
        return self.current_price.is_on_sale if self.current_price else False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "appid": self.appid,
            "currency": self.currency,
            "current_price": self.current_price.to_dict() if self.current_price else None,
            "lowest_price": self.lowest_price,
            "highest_price": self.highest_price,
            "price_points_count": len(self.price_points),
            "is_on_sale_now": self.is_on_sale_now(),
            "price_change": self.get_price_change()
        }


class PriceTracker:
    """
    Track prices for Steam apps in real-time.
    
    Features:
    - Track price history for multiple apps
    - Detect price changes and discounts
    - Compare prices across regions
    - Cache price data for efficiency
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the price tracker."""
        self.client = SteamClient(api_key=api_key)
        self._tracked_apps: Dict[int, PriceHistory] = {}
        self._cache_ttl = 3600  # 1 hour cache for price data
    
    def track_app(self, app_id: Union[str, int], currency: str = "USD") -> APIResponse:
        """
        Start tracking price for a specific app.
        
        Args:
            app_id: Application ID
            currency: Currency code (USD, EUR, RUB, etc.)
            
        Returns:
            APIResponse with price history data
        """
        app_id = AppID.validate(app_id).appid
        cache_key = f"price_tracker:{app_id}:{currency}"
        
        # Check cache
        cached = app_cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Get current price
        price_response = self._get_current_price(app_id, currency)
        if not price_response.ok:
            return price_response
        
        # Create or update price history
        if app_id not in self._tracked_apps:
            self._tracked_apps[app_id] = PriceHistory(appid=app_id, currency=currency)
        
        price_history = self._tracked_apps[app_id]
        
        # Add current price point
        price_data = price_response.data.get("price_overview", {})
        if price_data:
            price_point = PricePoint.from_api_data(app_id, price_data, currency)
            price_history.add_price_point(price_point)
        
        # Build response
        response = APIResponse(
            ok=True,
            source="price_tracker",
            data={"price_history": price_history.to_dict()},
            summary=f"Tracking price for App {app_id} in {currency}"
        )
        
        # Cache
        app_cache.set(cache_key, response, ttl=self._cache_ttl)
        
        return response
    
    def get_price_history(self, app_id: Union[str, int], currency: str = "USD", 
                          days: int = 30) -> APIResponse:
        """
        Get price history for a specific app.
        
        Args:
            app_id: Application ID
            currency: Currency code
            days: Number of days to look back
            
        Returns:
            APIResponse with price history data
        """
        app_id = AppID.validate(app_id).appid
        
        if app_id not in self._tracked_apps:
            # Try to track it first
            track_response = self.track_app(app_id, currency)
            if not track_response.ok:
                return track_response
        
        price_history = self._tracked_apps.get(app_id)
        if not price_history:
            return APIResponse(
                ok=False,
                source="price_tracker",
                data={},
                error={"message": f"App {app_id} not being tracked"}
            )
        
        # Filter by time
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        recent_points = [p for p in price_history.price_points if p.timestamp >= cutoff]
        
        # Create filtered history
        filtered_history = PriceHistory(
            appid=price_history.appid,
            currency=price_history.currency,
            price_points=recent_points
        )
        
        if recent_points:
            filtered_history.current_price = recent_points[-1]
        
        response = APIResponse(
            ok=True,
            source="price_tracker",
            data={"price_history": filtered_history.to_dict()},
            summary=f"Price history for App {app_id}: {len(recent_points)} data points"
        )
        
        return response
    
    def check_discounts(self, app_ids: List[Union[str, int]], currency: str = "USD") -> APIResponse:
        """
        Check which apps are currently on sale.
        
        Args:
            app_ids: List of Application IDs
            currency: Currency code
            
        Returns:
            APIResponse with discount information
        """
        on_sale = []
        not_on_sale = []
        errors = []
        
        for app_id in app_ids:
            try:
                app_id = AppID.validate(app_id).appid
                response = self.track_app(app_id, currency)
                
                if response.ok:
                    price_history = self._tracked_apps.get(app_id)
                    if price_history and price_history.is_on_sale_now():
                        current = price_history.current_price
                        on_sale.append({
                            "appid": app_id,
                            "final_price": current.final_price,
                            "initial_price": current.initial_price,
                            "discount_percent": current.discount_percent,
                            "currency": current.currency
                        })
                    else:
                        not_on_sale.append(app_id)
                else:
                    errors.append({"appid": app_id, "error": response.error})
            except Exception as e:
                errors.append({"appid": app_id, "error": str(e)})
        
        response = APIResponse(
            ok=True,
            source="price_tracker",
            data={
                "on_sale": on_sale,
                "not_on_sale": not_on_sale,
                "errors": errors
            },
            summary=f"Discount check: {len(on_sale)} on sale, {len(not_on_sale)} not on sale"
        )
        
        return response
    
    def compare_regions(self, app_id: Union[str, int], 
                       regions: List[str] = ["US", "EU", "RU"]) -> APIResponse:
        """
        Compare prices across different regions.
        
        Args:
            app_id: Application ID
            regions: List of country codes to compare
            
        Returns:
            APIResponse with regional price comparison
        """
        app_id = AppID.validate(app_id).appid
        regional_prices = {}
        
        for region in regions:
            response = self._get_current_price(app_id, region)
            if response.ok:
                price_data = response.data.get("price_overview", {})
                if price_data:
                    final_price = price_data.get("final", 0) / 100.0
                    initial_price = price_data.get("initial", 0) / 100.0
                    discount = price_data.get("discount_percent", 0)
                    currency = price_data.get("currency", "USD")
                    
                    regional_prices[region] = {
                        "final_price": final_price,
                        "initial_price": initial_price,
                        "discount_percent": discount,
                        "currency": currency,
                        "is_on_sale": discount > 0
                    }
        
        # Find best deal
        best_deal = None
        if regional_prices:
            best_deal = min(
                regional_prices.items(),
                key=lambda x: x[1]["final_price"]
            )
            # Convert tuple to dict
            best_deal = {"region": best_deal[0], "price_info": best_deal[1]}
        
        response = APIResponse(
            ok=True,
            source="price_tracker",
            data={
                "appid": app_id,
                "regional_prices": regional_prices,
                "best_deal": best_deal
            },
            summary=f"Price comparison for App {app_id}: {len(regional_prices)} regions"
        )
        
        return response
    
    def _get_current_price(self, app_id: int, country_code: str = "US") -> APIResponse:
        """Get current price for an app from Steam Store API."""
        url = f"{self.client.STEAM_STORE_API_BASE}/appdetails"
        params = {"appids": app_id, "cc": country_code, "l": "english"}
        
        response = self.client.get(url, params=params)
        
        if response.ok:
            app_data = response.data.get(str(app_id), {})
            if app_data.get("success", False):
                response.data = app_data.get("data", {})
            else:
                response.ok = False
                response.error = {"message": f"App {app_id} not found or not available in {country_code}"}
        
        return response
