from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("STEAM_API_KEY")

def fetch_steam_profile(steam_id: str) -> dict:
    import requests
#fetch profile info
    response = requests.get(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}")
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")

