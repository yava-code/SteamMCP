import os
import pytest
import json
from unittest.mock import Mock

class DummyResponse:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text

    def json(self):
        return self._json

@pytest.fixture(autouse=True)
def add_project_root_to_path(monkeypatch):
    # добавляем корень проекта в sys.path, чтобы импорты работали
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    monkeypatch.syspath_prepend(root)

@pytest.fixture(autouse=True)
def set_steam_api_key(monkeypatch):
    # ставим ключ api в окружение, чтобы тестам было ок
    monkeypatch.setenv("STEAM_API_KEY", "test_key")

@pytest.fixture
def mock_requests_get(monkeypatch):
    calls = []

    def _mock(url, params=None, timeout=10):
        calls.append({"url": url, "params": params})
        return DummyResponse(200, {"ok": True, "url": url, "params": params})

    monkeypatch.setattr("requests.get", _mock)
    return calls


# ===== ДОПОЛНИТЕЛЬНЫЕ ФИКСТУРЫ ДЛЯ РАЗЛИЧНЫХ СЦЕНАРИЕВ =====

@pytest.fixture
def mock_requests_error_responses(monkeypatch):
    """Фикстура для тестирования различных HTTP ошибок"""
    calls = []
    responses = []

    def _mock(url, params=None, timeout=10):
        calls.append({"url": url, "params": params})
        if responses:
            response_data = responses.pop(0)
            return DummyResponse(
                status_code=response_data.get("status_code", 200),
                json_data=response_data.get("json_data", {}),
                text=response_data.get("text", "")
            )
        return DummyResponse(200, {"ok": True})

    monkeypatch.setattr("requests.get", _mock)
    
    def set_responses(response_list):
        responses.clear()
        responses.extend(response_list)
    
    _mock.set_responses = set_responses
    _mock.calls = calls
    return _mock


@pytest.fixture
def mock_steam_profile_data():
    """Фикстура с примерами данных профиля Steam"""
    return {
        "minimal": {
            "response": {
                "players": [{
                    "steamid": "76561198006409530",
                    "personaname": "TestUser",
                    "personastate": 1,
                    "communityvisibilitystate": 3
                }]
            }
        },
        "full": {
            "response": {
                "players": [{
                    "steamid": "76561198006409530",
                    "personaname": "FullTestUser",
                    "profileurl": "https://steamcommunity.com/id/fulltestuser/",
                    "personastate": 1,
                    "communityvisibilitystate": 3,
                    "timecreated": 1234567890,
                    "loccountrycode": "US",
                    "locstatecode": "CA",
                    "realname": "John Doe",
                    "avatarfull": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/12/123456.jpg"
                }]
            }
        },
        "private": {
            "response": {
                "players": [{
                    "steamid": "76561198006409530",
                    "personaname": "PrivateUser",
                    "personastate": 0,
                    "communityvisibilitystate": 1
                }]
            }
        },
        "empty": {
            "response": {
                "players": []
            }
        }
    }


@pytest.fixture
def mock_market_data():
    """Фикстура с примерами данных рынка Steam"""
    return {
        "search_results": {
            "success": True,
            "start": 0,
            "pagesize": 10,
            "total_count": 1234,
            "results": [
                {
                    "name": "AK-47 | Redline (Field-Tested)",
                    "hash_name": "AK-47 | Redline (Field-Tested)",
                    "sell_price": 1500,
                    "sell_price_text": "$15.00",
                    "app_name": "Counter-Strike: Global Offensive",
                    "type": "Rifle",
                    "market_name": "AK-47 | Redline (Field-Tested)"
                }
            ]
        },
        "price_overview": {
            "success": True,
            "lowest_price": "$14.50",
            "volume": "123",
            "median_price": "$15.00"
        },
        "price_history": {
            "success": True,
            "price_prefix": "$",
            "price_suffix": " USD",
            "prices": [
                ["Jan 01 2023 01: +0", 15.0, "10"],
                ["Jan 02 2023 01: +0", 15.5, "8"],
                ["Jan 03 2023 01: +0", 14.8, "12"]
            ]
        },
        "item_orders": {
            "success": True,
            "sell_order_table": "<table>...</table>",
            "buy_order_table": "<table>...</table>",
            "sell_order_summary": "5 for sale starting at $15.00",
            "buy_order_summary": "10 buyers at $14.00 or lower"
        }
    }


@pytest.fixture
def mock_game_data():
    """Фикстура с примерами данных игр"""
    return {
        "owned_games": {
            "response": {
                "game_count": 2,
                "games": [
                    {
                        "appid": 730,
                        "name": "Counter-Strike: Global Offensive",
                        "playtime_forever": 12345,
                        "img_icon_url": "6b0312cda02f5f777efa2f3318c307ff9acafbb5",
                        "img_logo_url": "d0595ff02f5c79fd19b06f4d6165c3fda2372820"
                    },
                    {
                        "appid": 440,
                        "name": "Team Fortress 2",
                        "playtime_forever": 5678,
                        "img_icon_url": "e3f595a92552da3d664ad00277fad2107345f743",
                        "img_logo_url": "07385eb55b5ba974aebbe74d3c99626bda7920b8"
                    }
                ]
            }
        },
        "achievements": {
            "playerstats": {
                "steamID": "76561198006409530",
                "gameName": "Counter-Strike: Global Offensive",
                "achievements": [
                    {
                        "apiname": "WIN_BOMB_DEFUSE",
                        "achieved": 1,
                        "unlocktime": 1234567890
                    },
                    {
                        "apiname": "KILL_ENEMY_WITH_KNIFE",
                        "achieved": 0
                    }
                ]
            }
        },
        "game_schema": {
            "game": {
                "gameName": "Counter-Strike: Global Offensive",
                "gameVersion": "1.0.0.0",
                "availableGameStats": {
                    "achievements": [
                        {
                            "name": "WIN_BOMB_DEFUSE",
                            "displayName": "Defuse the Bomb",
                            "description": "Defuse a bomb"
                        }
                    ]
                }
            }
        }
    }


@pytest.fixture
def mock_api_rate_limit(monkeypatch):
    """Фикстура для тестирования rate limiting"""
    import time
    calls = []
    
    def _mock_sleep(seconds):
        calls.append({"sleep": seconds})
    
    monkeypatch.setattr("time.sleep", _mock_sleep)
    return calls


@pytest.fixture
def mock_network_errors(monkeypatch):
    """Фикстура для тестирования сетевых ошибок"""
    import requests
    
    def _mock_get_with_error(url, params=None, timeout=10):
        raise requests.ConnectionError("Network unreachable")
    
    monkeypatch.setattr("requests.get", _mock_get_with_error)


@pytest.fixture
def mock_timeout_error(monkeypatch):
    """Фикстура для тестирования timeout ошибок"""
    import requests
    
    def _mock_get_with_timeout(url, params=None, timeout=10):
        raise requests.Timeout("Request timed out")
    
    monkeypatch.setattr("requests.get", _mock_get_with_timeout)


@pytest.fixture
def mock_json_decode_error(monkeypatch):
    """Фикстура для тестирования ошибок декодирования JSON"""
    calls = []
    
    def _mock(url, params=None, timeout=10):
        calls.append({"url": url, "params": params})
        response = Mock()
        response.status_code = 200
        response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        response.text = "Invalid JSON response"
        return response
    
    monkeypatch.setattr("requests.get", _mock)
    return calls


@pytest.fixture
def sample_steam_ids():
    """Фикстура с примерами Steam ID для тестирования"""
    return {
        "valid": [
            "76561198006409530",
            "76561198000000000",
            "76561199999999999"
        ],
        "invalid": [
            "",
            "123",  # слишком короткий
            "abcdefghijklmnopq",  # не цифры
            "765611980064095301",  # слишком длинный
            None
        ],
        "edge_cases": [
            "00000000000000000",  # все нули
            "99999999999999999"   # все девятки
        ]
    }


@pytest.fixture
def sample_app_ids():
    """Фикстура с примерами App ID для тестирования"""
    return {
        "valid": [730, 440, 570, 1, 999999],
        "valid_strings": ["730", "440", "570"],
        "invalid": [0, -1, -999, "abc", "123abc", None, ""],
        "edge_cases": [1, 2147483647]  # минимальный и максимальный int32
    }


@pytest.fixture
def mock_environment_variables(monkeypatch):
    """Фикстура для управления переменными окружения в тестах"""
    original_env = {}
    
    def set_env(key, value):
        if key in os.environ:
            original_env[key] = os.environ[key]
        monkeypatch.setenv(key, value)
    
    def unset_env(key):
        if key in os.environ:
            original_env[key] = os.environ[key]
        monkeypatch.delenv(key, raising=False)
    
    def restore_env():
        for key, value in original_env.items():
            monkeypatch.setenv(key, value)
    
    mock_env = Mock()
    mock_env.set = set_env
    mock_env.unset = unset_env
    mock_env.restore = restore_env
    
    return mock_env