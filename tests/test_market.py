import importlib
import pytest


def test_search_market_requires_query():
    market = importlib.import_module("market")
    with pytest.raises(ValueError):
        market.search_market("")


def test_search_market_includes_appid_param(mock_requests_get):
    market = importlib.import_module("market")
    result = market.search_market("AK-47", appid=730)
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "search/render" in last["url"]
    assert last["params"]["appid"] == 730


def test_fetch_item_price_overview_encodes_hash_name(mock_requests_get):
    market = importlib.import_module("market")
    item_name = "AK-47 | Redline (Field-Tested)"
    market.fetch_item_price_overview(730, item_name)
    last = mock_requests_get[-1]
    # проверяем, что имя для рынка кодируется в урл (без пробелов)
    assert " " not in last["params"]["market_hash_name"]
    assert "%7C" in last["params"]["market_hash_name"]  # Encoded pipe


def test_fetch_market_popular_items_count_bounds():
    market = importlib.import_module("market")
    with pytest.raises(ValueError):
        market.fetch_market_popular_items(count=0)


def test_fetch_item_orders_histogram_builds_params(mock_requests_get):
    market = importlib.import_module("market")
    nameid = "123456"
    result = market.fetch_item_orders_histogram(nameid)
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "itemordershistogram" in last["url"]
    assert last["params"]["item_nameid"] == nameid