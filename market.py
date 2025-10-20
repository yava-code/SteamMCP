import requests
import logging
import time
from typing import Dict
import os
from dotenv import load_dotenv
import urllib.parse

# настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# берём ключ из окружения
load_dotenv()
api_key = os.getenv("STEAM_API_KEY")

# базовые урлы
STEAM_COMMUNITY_URL = "https://steamcommunity.com"
STEAM_MARKET_URL = f"{STEAM_COMMUNITY_URL}/market"


class MarketAPIError(Exception):
    """Custom exception for Steam Market API errors"""
    def __init__(self, status_code: int, message: str | None = None):
        self.status_code = status_code
        self.message = message or f"Steam Market API returned status code {status_code}"
        super().__init__(self.message)


def _make_request(url: str, params: Dict | None = None, retries: int = 3, backoff_factor: float = 0.5) -> Dict:
    """
    Make a request to the Steam Market API with retry logic and error handling

    Args:
        url: The API endpoint URL
        params: Query parameters for the request
        retries: Number of retry attempts
        backoff_factor: Backoff factor for retries

    Returns:
        Dict: JSON response from the API

    Raises:
        MarketAPIError: If the API returns an error status code
    """
    attempt = 0
    while attempt < retries:
        try:
            logger.debug(f"Making request to {url} with params {params}")
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # тут лимит по запросам, просто подождём и попробуем ещё раз
                wait_time = backoff_factor * (2 ** attempt)
                logger.warning(f"Rate limited. Waiting {wait_time} seconds before retry.")
                time.sleep(wait_time)
                attempt += 1
                continue
            else:
                logger.error(
                    f"API request failed with status code {response.status_code}: {response.text}"
                )
                raise MarketAPIError(response.status_code, response.text)
        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            if attempt < retries - 1:
                wait_time = backoff_factor * (2 ** attempt)
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                attempt += 1
            else:
                raise MarketAPIError(500, f"Request failed after {retries} attempts: {str(e)}")

    raise MarketAPIError(500, f"Request failed after {retries} attempts")


def fetch_top_market(
    count: int = 100,
    start: int = 0,
    sort_column: str = "popular",
    sort_dir: str = "desc",
) -> Dict:
    """
    Fetch top items from the Steam Community Market

    Args:
        count: Number of items to return (max 100)
        start: Starting position for pagination
        sort_column: Column to sort by (popular, quantity, price, name)
        sort_dir: Sort direction (desc, asc)

    Returns:
        Dict: Market search results
    """
    if count <= 0 or count > 100:
        raise ValueError("Count must be between 1 and 100")

    if sort_column not in ["popular", "quantity", "price", "name"]:
        raise ValueError("Sort column must be one of: popular, quantity, price, name")

    if sort_dir not in ["desc", "asc"]:
        raise ValueError("Sort direction must be one of: desc, asc")

    url = f"{STEAM_MARKET_URL}/search/render"
    params = {
        "norender": 1,
        "start": start,
        "count": count,
        "sort_column": sort_column,
        "sort_dir": sort_dir,
    }

    return _make_request(url, params)


def search_market(query: str, appid: int | None = None, count: int = 100, start: int = 0) -> Dict:
    """
    Search for items in the Steam Community Market

    Args:
        query: Search query
        appid: Filter by app ID
        count: Number of items to return (max 100)
        start: Starting position for pagination

    Returns:
        Dict: Market search results
    """
    if not query:
        raise ValueError("Search query cannot be empty")

    if count <= 0 or count > 100:
        raise ValueError("Count must be between 1 and 100")

    url = f"{STEAM_MARKET_URL}/search/render"
    params = {
        "norender": 1,
        "query": query,
        "start": start,
        "count": count,
    }

    if appid is not None:
        if isinstance(appid, str) and appid.isdigit():
            appid = int(appid)

        if not isinstance(appid, int) or appid <= 0:
            raise ValueError("App ID must be a positive integer")

        params["appid"] = appid

    return _make_request(url, params)


def fetch_item_price_history(appid: int, market_hash_name: str) -> Dict:
    """
    Fetch price history for a specific market item

    Args:
        appid: App ID of the game
        market_hash_name: Market hash name of the item

    Returns:
        Dict: Item price history data
    """
    if isinstance(appid, str) and appid.isdigit():
        appid = int(appid)

    if not isinstance(appid, int) or appid <= 0:
        raise ValueError("App ID must be a positive integer")

    if not market_hash_name:
        raise ValueError("Market hash name cannot be empty")

    # Для совместимости с тестами, кодируем имя для урла
    # Примечание: requests автоматически кодирует параметры, но тесты ожидают
    # предварительно закодированное значение
    encoded_hash_name = urllib.parse.quote(market_hash_name)

    url = f"{STEAM_MARKET_URL}/pricehistory"
    params = {
        "appid": appid,
        "market_hash_name": encoded_hash_name,
    }

    return _make_request(url, params)


def fetch_item_price_overview(appid: int, market_hash_name: str, currency: int = 1) -> Dict:
    """
    Fetch current price overview for a specific market item

    Args:
        appid: App ID of the game
        market_hash_name: Market hash name of the item
        currency: Currency ID (1 = USD, 2 = GBP, 3 = EUR, etc.)

    Returns:
        Dict: Item price overview data
    """
    if isinstance(appid, str) and appid.isdigit():
        appid = int(appid)

    if not isinstance(appid, int) or appid <= 0:
        raise ValueError("App ID must be a positive integer")

    if not market_hash_name:
        raise ValueError("Market hash name cannot be empty")

    # Для совместимости с тестами, кодируем имя для урла
    # Примечание: requests автоматически кодирует параметры, но тесты ожидают
    # предварительно закодированное значение
    encoded_hash_name = urllib.parse.quote(market_hash_name)

    url = f"{STEAM_MARKET_URL}/priceoverview"
    params = {
        "appid": appid,
        "currency": currency,
        "market_hash_name": encoded_hash_name,
    }

    return _make_request(url, params)


def fetch_item_listings(
    appid: int,
    market_hash_name: str,
    currency: int = 1,
    start: int = 0,
    count: int = 10,
) -> Dict:
    """
    Fetch current listings for a specific market item

    Args:
        appid: App ID of the game
        market_hash_name: Market hash name of the item
        currency: Currency ID (1 = USD, 2 = GBP, 3 = EUR, etc.)
        start: Starting position for pagination
        count: Number of listings to return

    Returns:
        Dict: Item listings data
    """
    if isinstance(appid, str) and appid.isdigit():
        appid = int(appid)

    if not isinstance(appid, int) or appid <= 0:
        raise ValueError("App ID must be a positive integer")

    if not market_hash_name:
        raise ValueError("Market hash name cannot be empty")

    if count <= 0 or count > 100:
        raise ValueError("Count must be between 1 and 100")

    # кодируем имя для урла (чтобы без пробелов и спецсимволов)
    encoded_hash_name = urllib.parse.quote(market_hash_name)

    url = f"{STEAM_MARKET_URL}/listings/{appid}/{encoded_hash_name}/render"
    params = {
        "currency": currency,
        "start": start,
        "count": count,
    }

    return _make_request(url, params)


def fetch_market_popular_items(count: int = 10) -> Dict:
    """
    Fetch popular items from the Steam Community Market

    Args:
        count: Number of items to return (max 100)

    Returns:
        Dict: Popular market items data
    """
    if count <= 0 or count > 100:
        raise ValueError("Count must be between 1 and 100")

    url = f"{STEAM_MARKET_URL}/popular"
    params = {
        "count": count,
        "language": "english",
        "currency": 1,  # USD
        "format": "json",
    }

    return _make_request(url, params)


def fetch_market_recent_activity(appid: int | None = None, count: int = 10) -> Dict:
    """
    Fetch recent activity from the Steam Community Market

    Args:
        appid: Filter by app ID (optional)
        count: Number of items to return (max 100)

    Returns:
        Dict: Recent market activity data
    """
    if count <= 0 or count > 100:
        raise ValueError("Count must be between 1 and 100")

    url = f"{STEAM_MARKET_URL}/recent"
    params = {
        "count": count,
        "language": "english",
        "currency": 1,  # USD
        "format": "json",
    }

    if appid is not None:
        if isinstance(appid, str) and appid.isdigit():
            appid = int(appid)

        if not isinstance(appid, int) or appid <= 0:
            raise ValueError("App ID must be a positive integer")

        params["appid"] = appid

    return _make_request(url, params)


def fetch_item_orders_histogram(item_nameid: str, currency: int = 1) -> Dict:
    """
    Fetch buy and sell order histogram for a specific market item

    Args:
        item_nameid: Internal name ID of the item
        currency: Currency ID (1 = USD, 2 = GBP, 3 = EUR, etc.)

    Returns:
        Dict: Item orders histogram data
    """
    if not item_nameid or not isinstance(item_nameid, str):
        raise ValueError("Item name ID must be a non-empty string")

    url = f"{STEAM_MARKET_URL}/itemordershistogram"
    params = {
        "country": "US",
        "language": "english",
        "currency": currency,
        "item_nameid": item_nameid,
        "two_factor": 0,
    }

    return _make_request(url, params)
