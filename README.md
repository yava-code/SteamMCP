# SteamMCP

![img.png](misc%2Fimg.png)

MCP-сервер для взаимодействия с API Steam через LLM-клиенты. Предоставляет инструменты для получения информации о профилях пользователей, играх, достижениях, новостях и данных торговой площадки Steam.

## Быстрый старт

### Установка

```bash
# Клонировать репозиторий
git clone https://github.com/yava-code/SteamMCP.git
cd SteamMCP

# Установить зависимости
pip install -r requirements.txt
```

### Настройка

Создайте файл `.env` в корне проекта и добавьте ваш Steam API ключ:

```bash
STEAM_API_KEY=your_steam_api_key_here
```

**Важно:** Не коммитьте `.env` файл в git! Используйте `.env.example` как шаблон.

### Запуск сервера

```bash
# Запуск через Python
python server.py

# Или через uv
uv run server.py
```

Сервер будет доступен как MCP-сервер через stdio.

## 📋 Доступные инструменты (Tools)

Все функции сервера доступны как MCP tools для LLM-клиентов. Полный список инструментов можно получить через MCP-клиент.

### 👤 Профиль пользователя

| Инструмент | Описание |
|-----------|----------|
| `get_profile_info` | Получение информации о профиле Steam пользователя |
| `get_friends` | Получение списка друзей пользователя |
| `resolve_vanity_url_name` | Преобразование имени vanity URL в Steam ID |
| `get_user_level` | Получение уровня пользователя Steam |
| `get_user_badges` | Получение значков пользователя |
| `get_player_bans` | Получение информации о банях игрока |

### 🎮 Игры и достижения

| Инструмент | Описание |
|-----------|----------|
| `get_player_achievements` | Получение достижений игрока в конкретной игре |
| `get_user_stats` | Получение статистики игрока в конкретной игре |
| `get_owned_games` | Получение списка игр, принадлежащих пользователю |
| `get_recently_played_games` | Получение списка недавно сыгранных игр |
| `get_game_news` | Получение новостных статей об игре |
| `get_game_schema` | Получение схемы игры (достижения, статистика) |
| `get_app_details` | Получение подробной информации о приложении из магазина Steam |
| `get_global_achievement_percentages` | Получение глобальных процентов завершения достижений |
| `get_current_players` | Получение текущего количества игроков в игре |

### 💰 Торговая площадка

| Инструмент | Описание |
|-----------|----------|
| `get_top_market_items` | Получение популярных предметов с торговой площадки |
| `search_market_items` | Поиск предметов на торговой площадке |
| `get_item_price_history` | Получение истории цен для конкретного предмета |
| `get_item_price_overview` | Получение обзора текущих цен для конкретного предмета |
| `get_popular_market_items` | Получение популярных предметов с торговой площадки |
| `get_recent_market_activity` | Получение недавней активности на торговой площадке |

### Примеры использования

```python
# Получение информации о профиле
get_profile_info(steam_id="76561198028121353")

# Получение списка игр пользователя
get_owned_games(steam_id="76561198028121353")

# Поиск предметов на рынке
search_market_items(query="AK-47", app_id=730, count=10)

# Получение информации об игре
get_app_details(app_id=570)
```

#### get_friends
Получение списка друзей пользователя.

```python
get_friends(steam_id="76561198028121353")
```

#### resolve_vanity_url_name
Преобразование имени vanity URL в Steam ID.

```python
resolve_vanity_url_name(vanity_url_name="gabelogannewell")
```

### Игры и достижения

#### get_player_achievements
Получение достижений игрока в конкретной игре.

```python
get_player_achievements(steam_id="76561198028121353", app_id=570)
```

#### get_user_stats
Получение статистики игрока в конкретной игре.

```python
get_user_stats(steam_id="76561198028121353", app_id=570)
```

#### get_owned_games
Получение списка игр, принадлежащих пользователю.

```python
get_owned_games(steam_id="76561198028121353", include_appinfo=True, include_played_free_games=True)
```

#### get_recently_played_games
Получение списка недавно сыгранных игр.

```python
get_recently_played_games(steam_id="76561198028121353", count=10)
```

#### get_game_news
Получение новостных статей об игре.

```python
get_game_news(app_id=570)
```

#### get_game_schema
Получение схемы игры (достижения, статистика).

```python
get_game_schema(app_id=570)
```

#### get_app_details
Получение подробной информации о приложении из магазина Steam.

```python
get_app_details(app_id=570)
```

### Торговая площадка

#### get_top_market_items
Получение популярных предметов с торговой площадки.

```python
get_top_market_items(count=100, start=0, sort_column="popular", sort_dir="desc")
```

#### search_market_items
Поиск предметов на торговой площадке.

```python
search_market_items(query="knife", app_id=730, count=100, start=0)
```

#### get_item_price_history
Получение истории цен для конкретного предмета.

```python
get_item_price_history(app_id=730, market_hash_name="AWP | Dragon Lore (Factory New)")
```

#### get_item_price_overview
Получение обзора текущих цен для конкретного предмета.

```python
get_item_price_overview(app_id=730, market_hash_name="AWP | Dragon Lore (Factory New)", currency=1)
```

#### get_popular_market_items
Получение популярных предметов с торговой площадки.

```python
get_popular_market_items(count=10)
```

#### get_recent_market_activity
Получение недавней активности на торговой площадке.

```python
get_recent_market_activity(app_id=730, count=10)
```

## 🧪 Тестирование

Проект включает комплексные тесты для всех модулей:

- **Unit-тесты** для функций `fetcher.py` и `market.py`
- **Интеграционные тесты** для проверки workflow между модулями
- **MCP Smoke тесты** для проверки регистрации инструментов

### Запуск тестов

```bash
# Запуск всех тестов
pytest -v

# Запуск только unit-тестов
pytest tests/test_fetcher.py tests/test_market.py -v

# Запуск только MCP smoke тестов
pytest tests/test_mcp_smoke.py -v

# Быстрый запуск (quiet mode)
pytest -q
```

**Примечание:** Все тесты выполняются офлайн и используют моки для `requests.get`, поэтому не требуют реального Steam API ключа.

## 🐳 Docker

Сборка и запуск контейнера:

```bash
# Сборка образа
docker build -t steam-mcp .

# Запуск контейнера
docker run --rm -e STEAM_API_KEY=your_key steam-mcp
```

**Примечание:** MCP-сервер работает через stdio, поэтому порт не требуется.

## 🔧 Разработка

### Структура проекта

```
SteamMCP/
├── server.py           # MCP-сервер с инструментами
├── steam/              # Новые модули Steam API
│   ├── __init__.py
│   ├── client.py       # Единый HTTP-клиент с retry и rate limiting
│   ├── schemas.py      # Dataclasses для нормализованных ответов
│   ├── web.py          # Steam Web API функции
│   ├── store.py        # Steam Store API функции
│   ├── market.py       # Steam Community Market функции
│   └── adapters.py     # Адаптеры для обратной совместимости
├── fetcher.py          # Старые функции (депрекация)
├── market.py           # Старые функции (депрекация)
├── utils.py            # Утилитарные функции
├── requirements.txt    # Зависимости Python
├── Dockerfile          # Конфигурация Docker
├── .env.example        # Шаблон для переменных окружения
├── tests/              # Тесты
│   ├── test_fetcher.py
│   ├── test_market.py
│   ├── test_integration.py
│   ├── test_mcp_smoke.py
│   └── test_steam_client.py
└── README.md
```

**Примечание:** Модули `fetcher.py` и `market.py` в корне проекта сохранены для обратной совместимости, но новые функции следует использовать из пакета `steam/`.

### Добавление новых инструментов

1. Создайте функцию в `fetcher.py` или `market.py`
2. Импортируйте её в `server.py`
3. Добавьте декоратор `@mcp.tool()`
4. Добавьте тесты для новой функции

## 🤖 CI/CD (GitHub Actions)

- Workflow `CI` (`.github/workflows/ci.yml`) устанавливает зависимости и запускает `pytest`
- Workflow `Docker Build` собирает Docker образ
- `STEAM_API_KEY` должен быть добавлен в GitHub Secrets репозитория для CI

## 📄 Лицензия

MIT License
