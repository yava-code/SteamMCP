import importlib
import pytest
from unittest.mock import patch, Mock
import requests


# ===== ТЕСТЫ ВАЛИДАЦИИ =====

def test_validate_steam_id():
    """Тест валидации Steam ID"""
    fetcher = importlib.import_module("fetcher")
    
    # Валидный Steam ID
    valid_id = "76561198006409530"
    assert fetcher.validate_steam_id(valid_id) == valid_id
    
    # Невалидные Steam ID
    with pytest.raises(ValueError, match="Steam ID must be a non-empty string"):
        fetcher.validate_steam_id("")
    
    with pytest.raises(ValueError, match="Steam ID must be a non-empty string"):
        fetcher.validate_steam_id(None)
    
    # Короткий ID (предупреждение, но не ошибка)
    short_id = "123456"
    result = fetcher.validate_steam_id(short_id)
    assert result == short_id
    
    # Не цифры
    non_digit_id = "abcd1234567890123"
    result = fetcher.validate_steam_id(non_digit_id)
    assert result == non_digit_id


def test_validate_app_id():
    """Тест валидации App ID"""
    fetcher = importlib.import_module("fetcher")
    
    # Валидные App ID
    assert fetcher.validate_app_id(730) == 730
    assert fetcher.validate_app_id("730") == 730
    
    # Невалидные App ID
    with pytest.raises(ValueError, match="App ID must be a positive integer"):
        fetcher.validate_app_id(0)
    
    with pytest.raises(ValueError, match="App ID must be a positive integer"):
        fetcher.validate_app_id(-1)
    
    with pytest.raises(ValueError, match="App ID must be a numeric string"):
        fetcher.validate_app_id("abc")
    
    with pytest.raises(ValueError, match="App ID must be a positive integer"):
        fetcher.validate_app_id(None)


# ===== ТЕСТЫ ДЛЯ fetch_steam_profile =====

def test_fetch_steam_profile_success(mock_requests_get):
    """Тест успешного получения профиля Steam"""
    fetcher = importlib.import_module("fetcher")
    
    steam_id = "76561198006409530"
    result = fetcher.fetch_steam_profile(steam_id)
    
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "GetPlayerSummaries" in last["url"]
    assert last["params"]["steamids"] == steam_id


def test_fetch_steam_profile_validates_steam_id():
    """Тест валидации Steam ID в fetch_steam_profile"""
    fetcher = importlib.import_module("fetcher")
    
    with pytest.raises(ValueError):
        fetcher.fetch_steam_profile("")


# ===== ТЕСТЫ ДЛЯ fetch_friend_list =====

def test_fetch_friend_list_success(mock_requests_get):
    """Тест успешного получения списка друзей"""
    fetcher = importlib.import_module("fetcher")
    
    steam_id = "76561198006409530"
    result = fetcher.fetch_friend_list(steam_id)
    
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "GetFriendList" in last["url"]
    assert last["params"]["steamid"] == steam_id
    assert last["params"]["relationship"] == "friend"


def test_fetch_friend_list_validates_relationship():
    """Тест валидации параметра relationship"""
    fetcher = importlib.import_module("fetcher")
    
    with pytest.raises(ValueError, match="Relationship must be 'friend' or 'all'"):
        fetcher.fetch_friend_list("76561198006409530", relationship="invalid")


def test_fetch_friend_list_all_relationship(mock_requests_get):
    """Тест с параметром relationship='all'"""
    fetcher = importlib.import_module("fetcher")
    
    steam_id = "76561198006409530"
    result = fetcher.fetch_friend_list(steam_id, relationship="all")
    
    last = mock_requests_get[-1]
    assert last["params"]["relationship"] == "all"


# ===== ТЕСТЫ ДЛЯ fetch_player_achievements =====

def test_fetch_player_achievements_success(mock_requests_get):
    """Тест успешного получения достижений игрока"""
    fetcher = importlib.import_module("fetcher")
    
    steam_id = "76561198006409530"
    app_id = 730
    result = fetcher.fetch_player_achievements(steam_id, app_id)
    
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "GetPlayerAchievements" in last["url"]
    assert last["params"]["steamid"] == steam_id
    assert last["params"]["appid"] == app_id
    assert last["params"]["l"] == "english"


def test_fetch_player_achievements_custom_language(mock_requests_get):
    """Тест с пользовательским языком"""
    fetcher = importlib.import_module("fetcher")
    
    steam_id = "76561198006409530"
    app_id = 730
    result = fetcher.fetch_player_achievements(steam_id, app_id, language="russian")
    
    last = mock_requests_get[-1]
    assert last["params"]["l"] == "russian"


def test_fetch_player_achievements_validates_params():
    """Тест валидации параметров для fetch_player_achievements"""
    fetcher = importlib.import_module("fetcher")
    
    # Невалидный Steam ID
    with pytest.raises(ValueError):
        fetcher.fetch_player_achievements("", 730)
    
    # Невалидный App ID
    with pytest.raises(ValueError):
        fetcher.fetch_player_achievements("76561198006409530", -1)


# ===== ТЕСТЫ ДЛЯ fetch_user_stats_for_game =====

def test_fetch_user_stats_for_game_success(mock_requests_get):
    """Тест успешного получения статистики игрока"""
    fetcher = importlib.import_module("fetcher")
    
    steam_id = "76561198006409530"
    app_id = 730
    result = fetcher.fetch_user_stats_for_game(steam_id, app_id)
    
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "GetUserStatsForGame" in last["url"]
    assert last["params"]["steamid"] == steam_id
    assert last["params"]["appid"] == app_id


# ===== ТЕСТЫ ДЛЯ fetch_owned_games =====

def test_fetch_owned_games_success(mock_requests_get):
    """Тест успешного получения списка игр"""
    fetcher = importlib.import_module("fetcher")
    
    steam_id = "76561198006409530"
    result = fetcher.fetch_owned_games(steam_id)
    
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "GetOwnedGames" in last["url"]
    assert last["params"]["steamid"] == steam_id
    assert last["params"]["include_appinfo"] == 1
    assert last["params"]["include_played_free_games"] == 1


def test_fetch_owned_games_custom_params(mock_requests_get):
    """Тест с пользовательскими параметрами"""
    fetcher = importlib.import_module("fetcher")
    
    steam_id = "76561198006409530"
    result = fetcher.fetch_owned_games(
        steam_id, 
        include_appinfo=False, 
        include_played_free_games=False
    )
    
    last = mock_requests_get[-1]
    assert last["params"]["include_appinfo"] == 0
    assert last["params"]["include_played_free_games"] == 0


# ===== ТЕСТЫ ДЛЯ fetch_recently_played_games =====

def test_fetch_recently_played_games_success(mock_requests_get):
    """Тест успешного получения недавно игранных игр"""
    fetcher = importlib.import_module("fetcher")
    
    steam_id = "76561198006409530"
    result = fetcher.fetch_recently_played_games(steam_id)
    
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "GetRecentlyPlayedGames" in last["url"]
    assert last["params"]["steamid"] == steam_id
    assert last["params"]["count"] == 10


def test_fetch_recently_played_games_validates_count():
    """Тест валидации параметра count"""
    fetcher = importlib.import_module("fetcher")
    
    steam_id = "76561198006409530"
    
    with pytest.raises(ValueError, match="Count must be between 1 and 100"):
        fetcher.fetch_recently_played_games(steam_id, count=0)
    
    with pytest.raises(ValueError, match="Count must be between 1 and 100"):
        fetcher.fetch_recently_played_games(steam_id, count=101)


def test_fetch_recently_played_games_custom_count(mock_requests_get):
    """Тест с пользовательским количеством"""
    fetcher = importlib.import_module("fetcher")
    
    steam_id = "76561198006409530"
    result = fetcher.fetch_recently_played_games(steam_id, count=25)
    
    last = mock_requests_get[-1]
    assert last["params"]["count"] == 25


# ===== ТЕСТЫ ДЛЯ fetch_game_news =====

def test_fetch_game_news_success(mock_requests_get):
    """Тест успешного получения новостей игры"""
    fetcher = importlib.import_module("fetcher")
    
    app_id = 730
    result = fetcher.fetch_game_news(app_id)
    
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "GetNewsForApp" in last["url"]
    assert last["params"]["appid"] == app_id
    assert last["params"]["count"] == 3
    assert last["params"]["maxlength"] == 300


def test_fetch_game_news_validates_count():
    """Тест валидации параметра count"""
    fetcher = importlib.import_module("fetcher")
    
    with pytest.raises(ValueError, match="Count must be positive"):
        fetcher.fetch_game_news(730, count=0)
    
    with pytest.raises(ValueError, match="Count must be positive"):
        fetcher.fetch_game_news(730, count=-1)


def test_fetch_game_news_with_feed_name(mock_requests_get):
    """Тест с указанием имени фида"""
    fetcher = importlib.import_module("fetcher")
    
    app_id = 730
    feed_name = "steam_community_announcements"
    result = fetcher.fetch_game_news(app_id, feed_name=feed_name)
    
    last = mock_requests_get[-1]
    assert last["params"]["feedname"] == feed_name


# ===== ТЕСТЫ ДЛЯ fetch_game_schema =====

def test_fetch_game_schema_success(mock_requests_get):
    """Тест успешного получения схемы игры"""
    fetcher = importlib.import_module("fetcher")
    
    app_id = 730
    result = fetcher.fetch_game_schema(app_id)
    
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "GetSchemaForGame" in last["url"]
    assert last["params"]["appid"] == app_id
    assert last["params"]["l"] == "english"


def test_fetch_game_schema_custom_language(mock_requests_get):
    """Тест с пользовательским языком"""
    fetcher = importlib.import_module("fetcher")
    
    app_id = 730
    result = fetcher.fetch_game_schema(app_id, language="russian")
    
    last = mock_requests_get[-1]
    assert last["params"]["l"] == "russian"


# ===== ТЕСТЫ ДЛЯ fetch_app_details =====

def test_fetch_app_details_success(mock_requests_get):
    """Тест успешного получения деталей приложения"""
    fetcher = importlib.import_module("fetcher")
    
    app_id = 730
    result = fetcher.fetch_app_details(app_id)
    
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "appdetails" in last["url"]
    assert last["params"]["appids"] == app_id
    assert last["params"]["cc"] == "US"
    assert last["params"]["l"] == "english"


def test_fetch_app_details_custom_country(mock_requests_get):
    """Тест с пользовательским кодом страны"""
    fetcher = importlib.import_module("fetcher")
    
    app_id = 730
    result = fetcher.fetch_app_details(app_id, country_code="RU")
    
    last = mock_requests_get[-1]
    assert last["params"]["cc"] == "RU"


# ===== ТЕСТЫ ДЛЯ fetch_global_achievement_percentages =====

def test_fetch_global_achievement_percentages_success(mock_requests_get):
    """Тест успешного получения глобальных процентов достижений"""
    fetcher = importlib.import_module("fetcher")
    
    app_id = 730
    result = fetcher.fetch_global_achievement_percentages(app_id)
    
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "GetGlobalAchievementPercentagesForApp" in last["url"]
    assert last["params"]["gameid"] == app_id


# ===== ТЕСТЫ ДЛЯ fetch_user_level =====

def test_fetch_user_level_success(mock_requests_get):
    """Тест успешного получения уровня пользователя"""
    fetcher = importlib.import_module("fetcher")
    
    steam_id = "76561198006409530"
    result = fetcher.fetch_user_level(steam_id)
    
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "GetSteamLevel" in last["url"]
    assert last["params"]["steamid"] == steam_id


# ===== ТЕСТЫ ДЛЯ fetch_user_badges =====

def test_fetch_user_badges_success(mock_requests_get):
    """Тест успешного получения значков пользователя"""
    fetcher = importlib.import_module("fetcher")
    
    steam_id = "76561198006409530"
    result = fetcher.fetch_user_badges(steam_id)
    
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "GetBadges" in last["url"]
    assert last["params"]["steamid"] == steam_id


# ===== ТЕСТЫ ДЛЯ resolve_vanity_url =====

def test_resolve_vanity_url_success(mock_requests_get):
    """Тест успешного разрешения vanity URL"""
    fetcher = importlib.import_module("fetcher")
    
    vanity_name = "testuser"
    result = fetcher.resolve_vanity_url(vanity_name)
    
    assert result["ok"] is True
    last = mock_requests_get[-1]
    assert "ResolveVanityURL" in last["url"]
    assert last["params"]["vanityurl"] == vanity_name


def test_resolve_vanity_url_validates_name():
    """Тест валидации имени vanity URL"""
    fetcher = importlib.import_module("fetcher")
    
    with pytest.raises(ValueError, match="Vanity URL name must be a non-empty string"):
        fetcher.resolve_vanity_url("")
    
    with pytest.raises(ValueError, match="Vanity URL name must be a non-empty string"):
        fetcher.resolve_vanity_url(None)


# ===== ТЕСТЫ ОБРАБОТКИ ОШИБОК =====

def test_steam_api_error_handling():
    """Тест обработки ошибок SteamAPIError"""
    fetcher = importlib.import_module("fetcher")
    
    with patch('requests.get') as mock_get:
        # Тест 403 ошибки (Forbidden)
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_get.return_value = mock_response
        
        with pytest.raises(fetcher.SteamAPIError) as exc_info:
            fetcher.fetch_steam_profile("76561198006409530")
        
        assert exc_info.value.status_code == 403
        assert "Forbidden" in str(exc_info.value)


def test_api_key_missing():
    """Тест отсутствия API ключа"""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="STEAM_API_KEY not found"):
            importlib.reload(importlib.import_module("fetcher"))


def test_rate_limiting_retry_fetcher():
    """Тест обработки rate limiting для fetcher"""
    fetcher = importlib.import_module("fetcher")
    
    with patch('requests.get') as mock_get, patch('time.sleep') as mock_sleep:
        # Первый запрос - 429, второй - успех
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"ok": True}
        
        mock_get.side_effect = [mock_response_429, mock_response_200]
        
        result = fetcher.fetch_steam_profile("76561198006409530")
        assert result["ok"] is True
        assert mock_get.call_count == 2
        mock_sleep.assert_called_once()


def test_request_exception_handling_fetcher():
    """Тест обработки исключений requests в fetcher"""
    fetcher = importlib.import_module("fetcher")
    
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.RequestException("Network error")
        
        with pytest.raises(fetcher.SteamAPIError) as exc_info:
            fetcher.fetch_steam_profile("76561198006409530")
        
        assert "Network error" in str(exc_info.value)


# ===== ТЕСТЫ ГРАНИЧНЫХ СЛУЧАЕВ =====

def test_string_app_id_conversion(mock_requests_get):
    """Тест конвертации строкового App ID в число"""
    fetcher = importlib.import_module("fetcher")
    
    # Все функции, принимающие app_id, должны корректно обрабатывать строки
    app_id_functions = [
        lambda: fetcher.fetch_player_achievements("76561198006409530", "730"),
        lambda: fetcher.fetch_user_stats_for_game("76561198006409530", "730"),
        lambda: fetcher.fetch_game_news("730"),
        lambda: fetcher.fetch_game_schema("730"),
        lambda: fetcher.fetch_app_details("730"),
        lambda: fetcher.fetch_global_achievement_percentages("730"),
    ]
    
    for func in app_id_functions:
        func()
        # Проверяем, что запрос был сделан (не упал с ошибкой)
        assert len(mock_requests_get) > 0


def test_extreme_count_values():
    """Тест экстремальных значений count"""
    fetcher = importlib.import_module("fetcher")
    
    steam_id = "76561198006409530"
    
    # Максимальные валидные значения
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"ok": True}
        
        # Максимальный count для recently played games
        fetcher.fetch_recently_played_games(steam_id, count=100)
        
        # Минимальный count
        fetcher.fetch_recently_played_games(steam_id, count=1)


def test_various_languages(mock_requests_get):
    """Тест различных языков"""
    fetcher = importlib.import_module("fetcher")
    
    languages = ["english", "russian", "german", "french", "spanish"]
    
    for lang in languages:
        fetcher.fetch_player_achievements("76561198006409530", 730, language=lang)
        last = mock_requests_get[-1]
        assert last["params"]["l"] == lang


def test_special_characters_in_vanity_url(mock_requests_get):
    """Тест специальных символов в vanity URL"""
    fetcher = importlib.import_module("fetcher")
    
    special_names = [
        "test_user",
        "test-user",
        "testuser123",
        "user.name",
    ]
    
    for name in special_names:
        fetcher.resolve_vanity_url(name)
        last = mock_requests_get[-1]
        assert last["params"]["vanityurl"] == name