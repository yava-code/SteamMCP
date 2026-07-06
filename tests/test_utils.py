import importlib
import pytest
from datetime import datetime


# ===== ТЕСТЫ ДЛЯ format_steam_profile =====

def test_format_steam_profile_empty_data():
    """Тест форматирования пустых данных профиля"""
    utils = importlib.import_module("utils")
    
    # Пустые данные
    empty_data = {}
    result = utils.format_steam_profile(empty_data)
    assert "Профиль не найден или данные пусты." in result
    
    # Данные без players
    no_players_data = {"response": {}}
    result = utils.format_steam_profile(no_players_data)
    assert "Профиль не найден или данные пусты." in result
    
    # Пустой список players
    empty_players_data = {"response": {"players": []}}
    result = utils.format_steam_profile(empty_players_data)
    assert "Профиль не найден или данные пусты." in result


def test_format_steam_profile_basic_data():
    """Тест форматирования базовых данных профиля"""
    utils = importlib.import_module("utils")
    
    basic_data = {
        "response": {
            "players": [{
                "personaname": "TestUser",
                "steamid": "76561198006409530",
                "profileurl": "https://steamcommunity.com/id/testuser/",
                "personastate": 1,
                "communityvisibilitystate": 3
            }]
        }
    }
    
    result = utils.format_steam_profile(basic_data)
    
    # Проверяем основные элементы
    assert "TestUser" in result
    assert "76561198006409530" in result
    assert "https://steamcommunity.com/id/testuser/" in result
    assert "Online" in result
    assert "Public" in result
    assert "Steam Profile:" in result


def test_format_steam_profile_all_fields():
    """Тест форматирования полных данных профиля"""
    utils = importlib.import_module("utils")
    
    full_data = {
        "response": {
            "players": [{
                "personaname": "FullTestUser",
                "steamid": "76561198006409530",
                "profileurl": "https://steamcommunity.com/id/fulltestuser/",
                "personastate": 2,
                "communityvisibilitystate": 3,
                "timecreated": 1234567890,
                "loccountrycode": "US",
                "locstatecode": "CA",
                "loccityid": 12345,
                "realname": "John Doe",
                "avatarfull": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/12/123456.jpg"
            }]
        }
    }
    
    result = utils.format_steam_profile(full_data)
    
    # Проверяем все поля
    assert "FullTestUser" in result
    assert "76561198006409530" in result
    assert "Busy" in result  # personastate = 2
    assert "Public" in result
    assert "2009-02-13" in result  # timecreated converted (timestamp 1234567890 = 2009-02-13)
    assert "US/CA" in result  # location
    assert "John Doe" in result  # real name
    assert "https://steamcdn-a.akamaihd.net" in result  # avatar


def test_format_steam_profile_persona_states():
    """Тест различных состояний персоны"""
    utils = importlib.import_module("utils")
    
    states = {
        0: "Offline",
        1: "Online", 
        2: "Busy",
        3: "Away",
        4: "Snooze",
        5: "Looking to trade",
        6: "Looking to play",
        999: "Unknown"  # неизвестное состояние
    }
    
    for state_code, expected_text in states.items():
        data = {
            "response": {
                "players": [{
                    "personaname": "TestUser",
                    "steamid": "76561198006409530",
                    "personastate": state_code,
                    "communityvisibilitystate": 3
                }]
            }
        }
        
        result = utils.format_steam_profile(data)
        assert expected_text in result


def test_format_steam_profile_visibility_states():
    """Тест различных состояний видимости профиля"""
    utils = importlib.import_module("utils")
    
    visibility_states = {
        1: "Private",
        2: "Friends only",
        3: "Public",
        999: "Unknown"  # неизвестное состояние
    }
    
    for visibility_code, expected_text in visibility_states.items():
        data = {
            "response": {
                "players": [{
                    "personaname": "TestUser",
                    "steamid": "76561198006409530",
                    "personastate": 1,
                    "communityvisibilitystate": visibility_code
                }]
            }
        }
        
        result = utils.format_steam_profile(data)
        assert expected_text in result


def test_format_steam_profile_missing_optional_fields():
    """Тест обработки отсутствующих опциональных полей"""
    utils = importlib.import_module("utils")
    
    minimal_data = {
        "response": {
            "players": [{
                "steamid": "76561198006409530",
                "personastate": 1,
                "communityvisibilitystate": 3
                # отсутствуют personaname, profileurl и другие опциональные поля
            }]
        }
    }
    
    result = utils.format_steam_profile(minimal_data)
    
    # Проверяем, что функция не падает и использует значения по умолчанию
    assert "Unknown" in result or "N/A" in result
    assert "76561198006409530" in result
    assert "Online" in result
    assert "Public" in result


def test_format_steam_profile_invalid_timestamp():
    """Тест обработки невалидного timestamp"""
    utils = importlib.import_module("utils")
    
    data_with_invalid_timestamp = {
        "response": {
            "players": [{
                "personaname": "TestUser",
                "steamid": "76561198006409530",
                "personastate": 1,
                "communityvisibilitystate": 3,
                "timecreated": "invalid_timestamp"  # невалидный timestamp
            }]
        }
    }
    
    result = utils.format_steam_profile(data_with_invalid_timestamp)
    
    # Функция должна обработать ошибку и показать исходное значение
    assert "invalid_timestamp" in result
    assert "TestUser" in result


def test_format_steam_profile_special_characters():
    """Тест обработки специальных символов в именах"""
    utils = importlib.import_module("utils")
    
    special_names = [
        "User with émojis 🎮🔥",
        "Русское имя пользователя",
        "User with <HTML> & symbols",
        "User|with|pipes",
        "User\"with\"quotes"
    ]
    
    for name in special_names:
        data = {
            "response": {
                "players": [{
                    "personaname": name,
                    "steamid": "76561198006409530",
                    "personastate": 1,
                    "communityvisibilitystate": 3
                }]
            }
        }
        
        result = utils.format_steam_profile(data)
        assert name in result
        assert "Steam Profile:" in result


def test_format_steam_profile_location_combinations():
    """Тест различных комбинаций локации"""
    utils = importlib.import_module("utils")
    
    location_tests = [
        # Полная локация
        {"loccountrycode": "US", "locstatecode": "CA", "loccityid": 12345},
        # Только страна
        {"loccountrycode": "RU"},
        # Страна и штат
        {"loccountrycode": "US", "locstatecode": "NY"},
        # Только штат (странный случай)
        {"locstatecode": "TX"},
        # Только город (странный случай)
        {"loccityid": 54321}
    ]
    
    for location_data in location_tests:
        data = {
            "response": {
                "players": [{
                    "personaname": "TestUser",
                    "steamid": "76561198006409530",
                    "personastate": 1,
                    "communityvisibilitystate": 3,
                    **location_data
                }]
            }
        }
        
        result = utils.format_steam_profile(data)
        
        # Проверяем, что локация отображается, если есть хотя бы одно поле
        if location_data:
            assert "📍 Location:" in result


def test_format_steam_profile_edge_cases():
    """Тест граничных случаев"""
    utils = importlib.import_module("utils")
    
    edge_cases = [
        # Очень длинное имя
        {
            "personaname": "A" * 1000,
            "steamid": "76561198006409530",
            "personastate": 1,
            "communityvisibilitystate": 3
        },
        # Пустое имя
        {
            "personaname": "",
            "steamid": "76561198006409530",
            "personastate": 1,
            "communityvisibilitystate": 3
        },
        # Очень старый timestamp
        {
            "personaname": "OldUser",
            "steamid": "76561198006409530",
            "personastate": 1,
            "communityvisibilitystate": 3,
            "timecreated": 0  # 1970-01-01
        },
        # Очень новый timestamp
        {
            "personaname": "FutureUser",
            "steamid": "76561198006409530",
            "personastate": 1,
            "communityvisibilitystate": 3,
            "timecreated": 2147483647  # максимальный 32-битный timestamp
        }
    ]
    
    for player_data in edge_cases:
        data = {
            "response": {
                "players": [player_data]
            }
        }
        
        result = utils.format_steam_profile(data)
        
        # Функция не должна падать
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Steam Profile:" in result


def test_format_steam_profile_output_structure():
    """Тест структуры выходных данных"""
    utils = importlib.import_module("utils")
    
    data = {
        "response": {
            "players": [{
                "personaname": "StructureTest",
                "steamid": "76561198006409530",
                "profileurl": "https://steamcommunity.com/id/test/",
                "personastate": 1,
                "communityvisibilitystate": 3,
                "timecreated": 1234567890,
                "realname": "Test User"
            }]
        }
    }
    
    result = utils.format_steam_profile(data)
    lines = result.split('\n')
    
    # Проверяем структуру вывода
    assert any("=" * 50 in line for line in lines)  # разделители
    assert any("Steam Profile:" in line for line in lines)  # заголовок
    assert any("👤 Nickname:" in line for line in lines)  # никнейм
    assert any("🆔 SteamID:" in line for line in lines)  # Steam ID
    assert any("🌐 Profile URL:" in line for line in lines)  # URL профиля
    assert any("🟢 Status:" in line for line in lines)  # статус
    assert any("📅 Account created:" in line for line in lines)  # дата создания
    assert any("👥 Real name:" in line for line in lines)  # реальное имя
    assert any("👁️ Visibility:" in line for line in lines)  # видимость


def test_format_steam_profile_none_values():
    """Тест обработки None значений"""
    utils = importlib.import_module("utils")
    
    data_with_nones = {
        "response": {
            "players": [{
                "personaname": None,
                "steamid": "76561198006409530",
                "profileurl": None,
                "personastate": 1,
                "communityvisibilitystate": 3,
                "realname": None
            }]
        }
    }
    
    result = utils.format_steam_profile(data_with_nones)
    
    # Функция должна обработать None значения
    assert "None" in result  # None значения отображаются как есть
    assert "76561198006409530" in result
    assert "Steam Profile:" in result