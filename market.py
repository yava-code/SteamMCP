def fetch_top_market() -> dict:
    import requests
    #fetch top items market
    response = requests.get(f"https://steamcommunity.com/market/search/render?norender=1&start=0&count=99&")
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")