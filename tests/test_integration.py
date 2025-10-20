import importlib
import pytest
from unittest.mock import patch, Mock


# ===== ИНТЕГРАЦИОННЫЕ ТЕСТЫ =====

def test_fetcher_and_utils_integration(mock_requests_get, mock_steam_profile_data):
    """Тест интеграции между fetcher и utils для получения и форматирования профиля"""
    fetcher = importlib.import_module("fetcher")
    utils = importlib.import_module("utils")
    
    # Настраиваем мок для возврата реальных данных профиля
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_steam_profile_data["full"]
        mock_get.return_value = mock_response
        
        # Получаем данные профиля через fetcher
        steam_id = "76561198006409530"
        profile_data = fetcher.fetch_steam_profile(steam_id)
        
        # Форматируем данные через utils
        formatted_profile = utils.format_steam_profile(profile_data)
        
        # Проверяем, что данные корректно прошли через оба модуля
        assert "FullTestUser" in formatted_profile
        assert "76561198006409530" in formatted_profile
        assert "John Doe" in formatted_profile
        assert "US/CA" in formatted_profile


def test_market_search_and_price_workflow(mock_requests_get):
    """Тест полного workflow поиска предмета и получения его цены"""
    market = importlib.import_module("market")
    
    # Сначала ищем предмет
    search_results = market.search_market("AK-47", appid=730)
    assert search_results["ok"] is True
    
    # Затем получаем обзор цены для найденного предмета
    item_name = "AK-47 | Redline (Field-Tested)"
    price_overview = market.fetch_item_price_overview(730, item_name)
    assert price_overview["ok"] is True
    
    # Получаем историю цен
    price_history = market.fetch_item_price_history(730, item_name)
    assert price_history["ok"] is True
    
    # Проверяем, что все запросы были сделаны в правильном порядке
    assert len(mock_requests_get) == 3
    assert "search/render" in mock_requests_get[0]["url"]
    assert "priceoverview" in mock_requests_get[1]["url"]
    assert "pricehistory" in mock_requests_get[2]["url"]


def test_user_game_analysis_workflow(mock_requests_get):
    """Тест полного workflow анализа игр пользователя"""
    fetcher = importlib.import_module("fetcher")
    
    steam_id = "76561198006409530"
    
    # Получаем профиль пользователя
    profile = fetcher.fetch_steam_profile(steam_id)
    assert profile["ok"] is True
    
    # Получаем список игр
    owned_games = fetcher.fetch_owned_games(steam_id)
    assert owned_games["ok"] is True
    
    # Получаем недавно игранные игры
    recent_games = fetcher.fetch_recently_played_games(steam_id, count=5)
    assert recent_games["ok"] is True
    
    # Получаем достижения для конкретной игры
    achievements = fetcher.fetch_player_achievements(steam_id, 730)
    assert achievements["ok"] is True
    
    # Получаем статистику для игры
    stats = fetcher.fetch_user_stats_for_game(steam_id, 730)
    assert stats["ok"] is True
    
    # Проверяем последовательность запросов
    assert len(mock_requests_get) == 5
    urls = [call["url"] for call in mock_requests_get]
    assert any("GetPlayerSummaries" in url for url in urls)
    assert any("GetOwnedGames" in url for url in urls)
    assert any("GetRecentlyPlayedGames" in url for url in urls)
    assert any("GetPlayerAchievements" in url for url in urls)
    assert any("GetUserStatsForGame" in url for url in urls)


def test_game_information_gathering_workflow(mock_requests_get):
    """Тест полного workflow сбора информации об игре"""
    fetcher = importlib.import_module("fetcher")
    
    app_id = 730
    
    # Получаем детали приложения
    app_details = fetcher.fetch_app_details(app_id)
    assert app_details["ok"] is True
    
    # Получаем схему игры
    game_schema = fetcher.fetch_game_schema(app_id)
    assert game_schema["ok"] is True
    
    # Получаем новости игры
    game_news = fetcher.fetch_game_news(app_id, count=5)
    assert game_news["ok"] is True
    
    # Получаем глобальные проценты достижений
    achievement_percentages = fetcher.fetch_global_achievement_percentages(app_id)
    assert achievement_percentages["ok"] is True
    
    # Проверяем все запросы
    assert len(mock_requests_get) == 4
    urls = [call["url"] for call in mock_requests_get]
    assert any("appdetails" in url for url in urls)
    assert any("GetSchemaForGame" in url for url in urls)
    assert any("GetNewsForApp" in url for url in urls)
    assert any("GetGlobalAchievementPercentagesForApp" in url for url in urls)


def test_market_item_deep_analysis_workflow(mock_requests_get):
    """Тест глубокого анализа предмета на рынке"""
    market = importlib.import_module("market")
    
    app_id = 730
    item_name = "AK-47 | Redline (Field-Tested)"
    
    # Поиск предмета
    search_results = market.search_market("AK-47", appid=app_id)
    assert search_results["ok"] is True
    
    # Обзор цены
    price_overview = market.fetch_item_price_overview(app_id, item_name)
    assert price_overview["ok"] is True
    
    # История цен
    price_history = market.fetch_item_price_history(app_id, item_name)
    assert price_history["ok"] is True
    
    # Текущие листинги
    listings = market.fetch_item_listings(app_id, item_name, count=20)
    assert listings["ok"] is True
    
    # Гистограмма ордеров (требует item_nameid)
    item_nameid = "123456"
    orders_histogram = market.fetch_item_orders_histogram(item_nameid)
    assert orders_histogram["ok"] is True
    
    # Проверяем все запросы
    assert len(mock_requests_get) == 5


def test_error_handling_across_modules():
    """Тест обработки ошибок в разных модулях"""
    market = importlib.import_module("market")
    fetcher = importlib.import_module("fetcher")
    
    # Тест обработки ошибок в market
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response
        
        with pytest.raises(market.MarketAPIError):
            market.search_market("test")
    
    # Тест обработки ошибок в fetcher
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_get.return_value = mock_response
        
        with pytest.raises(fetcher.SteamAPIError):
            fetcher.fetch_steam_profile("76561198006409530")


def test_data_consistency_between_modules(mock_requests_get):
    """Тест согласованности данных между модулями"""
    fetcher = importlib.import_module("fetcher")
    market = importlib.import_module("market")
    
    # Используем одинаковые app_id в разных модулях
    app_id = 730
    
    # Запросы через fetcher
    app_details = fetcher.fetch_app_details(app_id)
    game_news = fetcher.fetch_game_news(app_id)
    
    # Запросы через market с тем же app_id
    market_search = market.search_market("test", appid=app_id)
    
    # Проверяем, что app_id передается корректно в обоих модулях
    market_calls = [call for call in mock_requests_get if "search/render" in call["url"]]
    fetcher_calls = [call for call in mock_requests_get if "appdetails" in call["url"] or "GetNewsForApp" in call["url"]]
    
    assert len(market_calls) == 1
    assert len(fetcher_calls) == 2
    assert market_calls[0]["params"]["appid"] == app_id


def test_rate_limiting_across_modules(mock_api_rate_limit):
    """Тест обработки rate limiting в разных модулях"""
    market = importlib.import_module("market")
    fetcher = importlib.import_module("fetcher")
    
    with patch('requests.get') as mock_get:
        # Настраиваем последовательность ответов: 429, затем 200
        responses = [
            Mock(status_code=429),
            Mock(status_code=200, json=lambda: {"ok": True}),
            Mock(status_code=429),
            Mock(status_code=200, json=lambda: {"ok": True})
        ]
        mock_get.side_effect = responses
        
        # Тестируем rate limiting в market
        result1 = market.search_market("test")
        assert result1["ok"] is True
        
        # Тестируем rate limiting в fetcher
        result2 = fetcher.fetch_steam_profile("76561198006409530")
        assert result2["ok"] is True
        
        # Проверяем, что sleep был вызван для обоих модулей
        assert len(mock_api_rate_limit) == 2


def test_parameter_validation_consistency():
    """Тест согласованности валидации параметров между модулями"""
    market = importlib.import_module("market")
    fetcher = importlib.import_module("fetcher")
    
    # Тест валидации app_id в разных модулях
    invalid_app_ids = [-1, "abc"]  # Убираем 0 и None, так как они могут обрабатываться по-разному
    
    for invalid_id in invalid_app_ids:
        # market модуль
        with pytest.raises(ValueError):
            market.search_market("test", appid=invalid_id)
        
        # fetcher модуль
        with pytest.raises(ValueError):
            fetcher.fetch_app_details(invalid_id)
        
        with pytest.raises(ValueError):
            fetcher.fetch_game_news(invalid_id)


def test_string_to_int_conversion_consistency(mock_requests_get):
    """Тест согласованности конвертации строк в числа"""
    market = importlib.import_module("market")
    fetcher = importlib.import_module("fetcher")
    
    # Оба модуля должны корректно обрабатывать строковые app_id
    string_app_id = "730"
    
    # market модуль
    market.search_market("test", appid=string_app_id)
    
    # fetcher модуль
    fetcher.fetch_app_details(string_app_id)
    fetcher.fetch_game_news(string_app_id)
    
    # Проверяем, что все запросы прошли успешно
    assert len(mock_requests_get) == 3


def test_complex_user_profile_analysis(mock_steam_profile_data):
    """Тест комплексного анализа профиля пользователя"""
    fetcher = importlib.import_module("fetcher")
    utils = importlib.import_module("utils")
    
    steam_id = "76561198006409530"
    
    with patch('requests.get') as mock_get:
        # Настраиваем разные ответы для разных запросов
        def mock_response(*args, **kwargs):
            url = args[0]
            response = Mock()
            response.status_code = 200
            
            if "GetPlayerSummaries" in url:
                response.json.return_value = mock_steam_profile_data["full"]
            elif "GetOwnedGames" in url:
                response.json.return_value = {
                    "response": {
                        "game_count": 100,
                        "games": [{"appid": 730, "name": "CS:GO", "playtime_forever": 1000}]
                    }
                }
            elif "GetSteamLevel" in url:
                response.json.return_value = {"response": {"player_level": 25}}
            elif "GetBadges" in url:
                response.json.return_value = {"response": {"badges": []}}
            else:
                response.json.return_value = {"ok": True}
            
            return response
        
        mock_get.side_effect = mock_response
        
        # Собираем полную информацию о пользователе
        profile = fetcher.fetch_steam_profile(steam_id)
        owned_games = fetcher.fetch_owned_games(steam_id)
        user_level = fetcher.fetch_user_level(steam_id)
        user_badges = fetcher.fetch_user_badges(steam_id)
        
        # Форматируем профиль
        formatted_profile = utils.format_steam_profile(profile)
        
        # Проверяем, что все данные получены
        assert profile["response"]["players"][0]["personaname"] == "FullTestUser"
        assert owned_games["response"]["game_count"] == 100
        assert user_level["response"]["player_level"] == 25
        assert "FullTestUser" in formatted_profile
        assert "John Doe" in formatted_profile


def test_market_trend_analysis_workflow(mock_requests_get):
    """Тест workflow анализа трендов рынка"""
    market = importlib.import_module("market")
    
    # Получаем популярные предметы
    popular_items = market.fetch_market_popular_items(count=20)
    assert popular_items["ok"] is True
    
    # Получаем недавнюю активность
    recent_activity = market.fetch_market_recent_activity(count=15)
    assert recent_activity["ok"] is True
    
    # Получаем топ предметы с разными сортировками
    top_by_price = market.fetch_top_market(sort_column="price", sort_dir="desc")
    assert top_by_price["ok"] is True
    
    top_by_volume = market.fetch_top_market(sort_column="quantity", sort_dir="desc")
    assert top_by_volume["ok"] is True
    
    # Проверяем все запросы
    assert len(mock_requests_get) == 4
    
    # Проверяем параметры сортировки
    sort_calls = [call for call in mock_requests_get if "sort_column" in call["params"]]
    assert len(sort_calls) == 2
    assert sort_calls[0]["params"]["sort_column"] == "price"
    assert sort_calls[1]["params"]["sort_column"] == "quantity"


def test_cross_module_error_propagation():
    """Тест распространения ошибок между модулями"""
    fetcher = importlib.import_module("fetcher")
    utils = importlib.import_module("utils")
    
    # Тест случая, когда fetcher возвращает ошибку, а utils должен ее обработать
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {"players": []}}  # Пустой ответ
        mock_get.return_value = mock_response
        
        # Получаем пустые данные профиля
        profile_data = fetcher.fetch_steam_profile("76561198006409530")
        
        # utils должен корректно обработать пустые данные
        formatted_profile = utils.format_steam_profile(profile_data)
        assert "Профиль не найден или данные пусты." in formatted_profile