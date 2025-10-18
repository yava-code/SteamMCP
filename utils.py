from datetime import datetime

def format_steam_profile(data: dict) -> str:

    if not data.get("response", {}).get("players"):
        return "Профиль не найден или данные пусты."

    player = data["response"]["players"][0]
    result = []

    result.append("\n" + "=" * 50)
    result.append(f"Steam Profile: {player.get('personaname', 'Unknown')}".center(50))
    result.append("=" * 50 + "\n")

    # основная инфа
    result.append(f"👤 Nickname: {player.get('personaname', 'N/A')}")
    result.append(f"🆔 SteamID: {player.get('steamid', 'N/A')}")
    result.append(f"🌐 Profile URL: {player.get('profileurl', 'N/A')}")

    # статус
    status_map = {
        0: "Offline",
        1: "Online",
        2: "Busy",
        3: "Away",
        4: "Snooze",
        5: "Looking to trade",
        6: "Looking to play"
    }
    result.append(f"🟢 Status: {status_map.get(player.get('personastate'), 'Unknown')}")

    # когда создали аккаунт
    if "timecreated" in player:
        try:
            result.append(f"📅 Account created: {datetime.fromtimestamp(player['timecreated']).strftime('%Y-%m-%d')}")
        except:
            result.append(f"📅 Account created: {player['timecreated']}")

    # локация
    if any(k in player for k in ["loccountrycode", "locstatecode", "loccityid"]):
        result.append(f"📍 Location: {player.get('loccountrycode', '?')}/{player.get('locstatecode', '?')}")

    # реальное имя (если есть)
    if player.get("realname"):
        result.append(f"👥 Real name: {player['realname']}")

    # аватар
    if player.get("avatarfull"):
        result.append(f"🖼️ Avatar: {player['avatarfull']}")

    # видимость профиля
    visibility_map = {
        1: "Private",
        2: "Friends only",
        3: "Public"
    }
    result.append(f"👁️ Visibility: {visibility_map.get(player.get('communityvisibilitystate'), 'Unknown')}")

    result.append("\n" + "=" * 50 + "\n")
    return "\n".join(result)

# пример использования:
# print(format_steam_profile(fetch_steam_profile("76561198006409530")))
