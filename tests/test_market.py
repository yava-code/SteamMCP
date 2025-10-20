import importlib
import pytest
from unittest.mock import patch, Mock
import requests


# ===== ТЕСТЫ ДЛЯ search_market =====

def test_search_market_requires_query():
    """Тест проверки обязательного параметра query"""
    market = importlib.import_module("market")
    with pytest.raises(ValueError, match="Search query cannot be empty"):
        market.search_market("")
    
    with pytest.raises(ValueError, match="Search query cannot be empty"):
        market.search_market(None)


def test_search_market_includes_appid_param(mock_requests_get):
    """Тест включения appid в параметры запроса"""
    market = importlib.import_module("market")
    result = market.search_market("AK-47", appid=730)
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "search/render" in last["url"]
    assert last["params"]["appid"] == 730


def test_search_market_validates_appid():
    """Тест валидации appid"""
    market = importlib.import_module("market")
    
    # Негативные значения
    with pytest.raises(ValueError, match="App ID must be a positive integer"):
        market.search_market("test", appid=-1)
    
    # Ноль
    with pytest.raises(ValueError, match="App ID must be a positive integer"):
        market.search_market("test", appid=0)
    
    # Строка с числом должна работать
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"ok": True}
        market.search_market("test", appid="730")
        mock_get.assert_called_once()


def test_search_market_count_validation():
    """Тест валидации параметра count"""
    market = importlib.import_module("market")
    
    with pytest.raises(ValueError, match="Count must be between 1 and 100"):
        market.search_market("test", count=0)
    
    with pytest.raises(ValueError, match="Count must be between 1 and 100"):
        market.search_market("test", count=101)
    
    with pytest.raises(ValueError, match="Count must be between 1 and 100"):
        market.search_market("test", count=-5)


def test_search_market_pagination_params(mock_requests_get):
    """Тест параметров пагинации"""
    market = importlib.import_module("market")
    result = market.search_market("test", start=50, count=25)
    
    last = mock_requests_get[-1]
    assert last["params"]["start"] == 50
    assert last["params"]["count"] == 25


# ===== ТЕСТЫ ДЛЯ fetch_top_market =====

def test_fetch_top_market_count_validation():
    """Тест валидации count для fetch_top_market"""
    market = importlib.import_module("market")
    
    with pytest.raises(ValueError, match="Count must be between 1 and 100"):
        market.fetch_top_market(count=0)
    
    with pytest.raises(ValueError, match="Count must be between 1 and 100"):
        market.fetch_top_market(count=101)


def test_fetch_top_market_sort_column_validation():
    """Тест валидации sort_column"""
    market = importlib.import_module("market")
    
    with pytest.raises(ValueError, match="Sort column must be one of"):
        market.fetch_top_market(sort_column="invalid")


def test_fetch_top_market_sort_dir_validation():
    """Тест валидации sort_dir"""
    market = importlib.import_module("market")
    
    with pytest.raises(ValueError, match="Sort direction must be one of"):
        market.fetch_top_market(sort_dir="invalid")


def test_fetch_top_market_valid_params(mock_requests_get):
    """Тест корректных параметров для fetch_top_market"""
    market = importlib.import_module("market")
    result = market.fetch_top_market(count=50, start=10, sort_column="price", sort_dir="asc")
    
    last = mock_requests_get[-1]
    assert last["params"]["count"] == 50
    assert last["params"]["start"] == 10
    assert last["params"]["sort_column"] == "price"
    assert last["params"]["sort_dir"] == "asc"


# ===== ТЕСТЫ ДЛЯ fetch_item_price_overview =====

def test_fetch_item_price_overview_encodes_hash_name(mock_requests_get):
    """Тест кодирования имени предмета в URL"""
    market = importlib.import_module("market")
    item_name = "AK-47 | Redline (Field-Tested)"
    market.fetch_item_price_overview(730, item_name)
    last = mock_requests_get[-1]
    # проверяем, что имя для рынка кодируется в урл (без пробелов)
    assert " " not in last["params"]["market_hash_name"]
    assert "%7C" in last["params"]["market_hash_name"]  # Encoded pipe


def test_fetch_item_price_overview_validates_appid():
    """Тест валидации appid для fetch_item_price_overview"""
    market = importlib.import_module("market")
    
    with pytest.raises(ValueError, match="App ID must be a positive integer"):
        market.fetch_item_price_overview(-1, "test")
    
    with pytest.raises(ValueError, match="App ID must be a positive integer"):
        market.fetch_item_price_overview(0, "test")


def test_fetch_item_price_overview_validates_hash_name():
    """Тест валидации market_hash_name"""
    market = importlib.import_module("market")
    
    with pytest.raises(ValueError, match="Market hash name cannot be empty"):
        market.fetch_item_price_overview(730, "")
    
    with pytest.raises(ValueError, match="Market hash name cannot be empty"):
        market.fetch_item_price_overview(730, None)


def test_fetch_item_price_overview_currency_param(mock_requests_get):
    """Тест параметра currency"""
    market = importlib.import_module("market")
    market.fetch_item_price_overview(730, "test", currency=3)
    
    last = mock_requests_get[-1]
    assert last["params"]["currency"] == 3


# ===== ТЕСТЫ ДЛЯ fetch_item_price_history =====

def test_fetch_item_price_history_validates_params():
    """Тест валидации параметров для fetch_item_price_history"""
    market = importlib.import_module("market")
    
    # Невалидный appid
    with pytest.raises(ValueError, match="App ID must be a positive integer"):
        market.fetch_item_price_history(-1, "test")
    
    # Пустое имя
    with pytest.raises(ValueError, match="Market hash name cannot be empty"):
        market.fetch_item_price_history(730, "")


def test_fetch_item_price_history_string_appid_conversion(mock_requests_get):
    """Тест конвертации строкового appid в число"""
    market = importlib.import_module("market")
    market.fetch_item_price_history("730", "test")
    
    last = mock_requests_get[-1]
    assert "pricehistory" in last["url"]


# ===== ТЕСТЫ ДЛЯ fetch_item_listings =====

def test_fetch_item_listings_validates_count():
    """Тест валидации count для fetch_item_listings"""
    market = importlib.import_module("market")
    
    with pytest.raises(ValueError, match="Count must be between 1 and 100"):
        market.fetch_item_listings(730, "test", count=0)
    
    with pytest.raises(ValueError, match="Count must be between 1 and 100"):
        market.fetch_item_listings(730, "test", count=101)


def test_fetch_item_listings_pagination(mock_requests_get):
    """Тест пагинации для fetch_item_listings"""
    market = importlib.import_module("market")
    market.fetch_item_listings(730, "test", start=20, count=50)
    
    last = mock_requests_get[-1]
    assert last["params"]["start"] == 20
    assert last["params"]["count"] == 50


# ===== ТЕСТЫ ДЛЯ fetch_market_popular_items =====

def test_fetch_market_popular_items_count_bounds():
    """Тест границ count для fetch_market_popular_items"""
    market = importlib.import_module("market")
    with pytest.raises(ValueError, match="Count must be between 1 and 100"):
        market.fetch_market_popular_items(count=0)
    
    with pytest.raises(ValueError, match="Count must be between 1 and 100"):
        market.fetch_market_popular_items(count=101)


def test_fetch_market_popular_items_default_params(mock_requests_get):
    """Тест дефолтных параметров для fetch_market_popular_items"""
    market = importlib.import_module("market")
    market.fetch_market_popular_items()
    
    last = mock_requests_get[-1]
    assert last["params"]["count"] == 10
    assert last["params"]["language"] == "english"
    assert last["params"]["currency"] == 1


# ===== ТЕСТЫ ДЛЯ fetch_market_recent_activity =====

def test_fetch_market_recent_activity_count_validation():
    """Тест валидации count для fetch_market_recent_activity"""
    market = importlib.import_module("market")
    
    with pytest.raises(ValueError, match="Count must be between 1 and 100"):
        market.fetch_market_recent_activity(count=0)
    
    with pytest.raises(ValueError, match="Count must be between 1 and 100"):
        market.fetch_market_recent_activity(count=101)


def test_fetch_market_recent_activity_with_appid(mock_requests_get):
    """Тест с параметром appid для fetch_market_recent_activity"""
    market = importlib.import_module("market")
    market.fetch_market_recent_activity(appid=730, count=20)
    
    last = mock_requests_get[-1]
    assert last["params"]["appid"] == 730
    assert last["params"]["count"] == 20


def test_fetch_market_recent_activity_appid_validation():
    """Тест валидации appid для fetch_market_recent_activity"""
    market = importlib.import_module("market")
    
    with pytest.raises(ValueError, match="App ID must be a positive integer"):
        market.fetch_market_recent_activity(appid=-1)


# ===== ТЕСТЫ ДЛЯ fetch_item_orders_histogram =====

def test_fetch_item_orders_histogram_builds_params(mock_requests_get):
    """Тест построения параметров для fetch_item_orders_histogram"""
    market = importlib.import_module("market")
    nameid = "123456"
    result = market.fetch_item_orders_histogram(nameid)
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "itemordershistogram" in last["url"]
    assert last["params"]["item_nameid"] == nameid


def test_fetch_item_orders_histogram_validates_nameid():
    """Тест валидации item_nameid"""
    market = importlib.import_module("market")
    
    with pytest.raises(ValueError, match="Item name ID must be a non-empty string"):
        market.fetch_item_orders_histogram("")
    
    with pytest.raises(ValueError, match="Item name ID must be a non-empty string"):
        market.fetch_item_orders_histogram(None)
    
    with pytest.raises(ValueError, match="Item name ID must be a non-empty string"):
        market.fetch_item_orders_histogram(123)


def test_fetch_item_orders_histogram_currency_param(mock_requests_get):
    """Тест параметра currency для fetch_item_orders_histogram"""
    market = importlib.import_module("market")
    market.fetch_item_orders_histogram("123456", currency=3)
    
    last = mock_requests_get[-1]
    assert last["params"]["currency"] == 3


# ===== ТЕСТЫ ОБРАБОТКИ ОШИБОК =====

def test_market_api_error_handling():
    """Тест обработки ошибок MarketAPIError"""
    market = importlib.import_module("market")
    
    with patch('requests.get') as mock_get:
        # Тест 404 ошибки
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response
        
        with pytest.raises(market.MarketAPIError) as exc_info:
            market.search_market("test")
        
        assert exc_info.value.status_code == 404
        assert "Not Found" in str(exc_info.value)


def test_rate_limiting_retry():
    """Тест обработки rate limiting (429 ошибка)"""
    market = importlib.import_module("market")
    
    with patch('requests.get') as mock_get, patch('time.sleep') as mock_sleep:
        # Первый запрос - 429, второй - успех
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"ok": True}
        
        mock_get.side_effect = [mock_response_429, mock_response_200]
        
        result = market.search_market("test")
        assert result["ok"] is True
        assert mock_get.call_count == 2
        mock_sleep.assert_called_once()


def test_request_exception_handling():
    """Тест обработки исключений requests"""
    market = importlib.import_module("market")
    
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.RequestException("Connection error")
        
        with pytest.raises(market.MarketAPIError) as exc_info:
            market.search_market("test")
        
        assert "Connection error" in str(exc_info.value)


# ===== ТЕСТЫ ГРАНИЧНЫХ СЛУЧАЕВ =====

def test_special_characters_in_item_names(mock_requests_get):
    """Тест обработки специальных символов в именах предметов"""
    market = importlib.import_module("market")
    
    special_names = [
        "AK-47 | Redline (Field-Tested)",
        "★ Karambit | Fade (Factory New)",
        "M4A4 | Howl (Minimal Wear) [Contraband]",
        "Предмет с русскими символами",
        "Item with émojis 🔥💎"
    ]
    
    for name in special_names:
        market.fetch_item_price_overview(730, name)
        last = mock_requests_get[-1]
        # Проверяем, что имя было закодировано
        assert isinstance(last["params"]["market_hash_name"], str)


def test_extreme_pagination_values(mock_requests_get):
    """Тест экстремальных значений пагинации"""
    market = importlib.import_module("market")
    
    # Максимальные валидные значения
    market.search_market("test", count=100, start=9999)
    last = mock_requests_get[-1]
    assert last["params"]["count"] == 100
    assert last["params"]["start"] == 9999


def test_all_sort_combinations(mock_requests_get):
    """Тест всех комбинаций сортировки"""
    market = importlib.import_module("market")
    
    sort_columns = ["popular", "quantity", "price", "name"]
    sort_dirs = ["desc", "asc"]
    
    for column in sort_columns:
        for direction in sort_dirs:
            market.fetch_top_market(sort_column=column, sort_dir=direction)
            last = mock_requests_get[-1]
            assert last["params"]["sort_column"] == column
            assert last["params"]["sort_dir"] == direction