import os
import pytest

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