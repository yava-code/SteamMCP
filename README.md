# SteamMCP

![img.png](misc%2Fimg.png)

Сервер MCP для взаимодействия с API Steam через модель LLM.

## Установка

```bash
pip install -r requirements.txt
```

## Переменные окружения

- Обязательно: `STEAM_API_KEY` — ключ доступа к Steam Web API.
- Можно задать в `.env` или через переменные окружения системы/CI.

## Запуск сервера

```bash
python server.py
# или
uv run server.py
```

## Доступные функции

### Профиль пользователя

#### get_profile_info
Получение информации о профиле Steam пользователя.

```python
get_profile_info(steam_id="76561198028121353")
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

## Тестирование

- Запуск тестов локально:

```bash
pytest -q
```

- Тесты используют фикстуры для подстановки `STEAM_API_KEY` и мокают `requests.get`, поэтому выполняются офлайн.

## Docker

Сборка и запуск контейнера:

```bash
docker build -t steam-mcp .
docker run --rm -e STEAM_API_KEY=your_key -p 8000:8000 steam-mcp
```

## CI (GitHub Actions)

- Workflow `CI` (`.github/workflows/ci.yml`) устанавливает зависимости и запускает `pytest`.
- `STEAM_API_KEY` должен быть добавлен в GitHub Secrets репозитория.
- Workflow `Docker Build` собирает образ с помощью `Dockerfile` (без push по умолчанию).
