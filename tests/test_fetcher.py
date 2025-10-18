import importlib
import pytest


def test_validate_app_id_valid_string():
    fetcher = importlib.import_module("fetcher")
    assert fetcher.validate_app_id("570") == 570


def test_validate_app_id_invalid_string_raises():
    fetcher = importlib.import_module("fetcher")
    with pytest.raises(ValueError):
        fetcher.validate_app_id("five70")


def test_fetch_steam_profile_builds_params(mock_requests_get):
    fetcher = importlib.import_module("fetcher")
    steam_id = "76561198000000000"
    result = fetcher.fetch_steam_profile(steam_id)
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "GetPlayerSummaries" in last["url"]
    assert last["params"]["steamids"] == steam_id
    assert last["params"]["key"] == "test_key"


def test_fetch_game_news_defaults(mock_requests_get):
    fetcher = importlib.import_module("fetcher")
    app_id = 570
    result = fetcher.fetch_game_news(app_id)
    last = mock_requests_get[-1]
    assert "GetNewsForApp" in last["url"]
    assert last["params"]["appid"] == app_id
    assert last["params"]["count"] == 3
    assert last["params"]["maxlength"] == 300


def test_fetch_recently_played_count_bounds():
    fetcher = importlib.import_module("fetcher")
    with pytest.raises(ValueError):
        fetcher.fetch_recently_played_games("76561198000000000", count=101)


def test_resolve_vanity_url_builds_params(mock_requests_get):
    fetcher = importlib.import_module("fetcher")
    name = "gaben"
    result = fetcher.resolve_vanity_url(name)
    last = mock_requests_get[-1]
    assert "ResolveVanityURL" in last["url"]
    assert last["params"]["vanityurl"] == name