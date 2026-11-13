import json
import re
import time
import pandas as pd
import requests


# The sportsbooks we keep, and the short name used for each one in column names
BOOKS = {"bet365": "b365", "draftkings": "dk", "fanduel": "fd"}

# SportsbookReview (SBR) has a separate page for each type of bet
SBR_URLS = {
    "moneyline": "https://www.sportsbookreview.com/betting-odds/mlb-baseball/?date={}",
    "runline": "https://www.sportsbookreview.com/betting-odds/mlb-baseball/pointspread/full-game/?date={}",
    "total": "https://www.sportsbookreview.com/betting-odds/mlb-baseball/totals/full-game/?date={}",
}

# Seconds to wait after each request so we don't overload the website
DELAY = 2

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# SBR uses the current team names for old seasons, so we rename old names to match
TEAM_NAME_FIXES = {
    "Cleveland Indians": "Cleveland Guardians",
    "Oakland Athletics": "Athletics",
    "Athletics Athletics": "Athletics",
}


def fix_team_name(name):
    return TEAM_NAME_FIXES.get(name, name)


def get_mlb_schedule(season):
    """Download one season's schedule (regular season + playoffs) from the MLB Stats API."""
    url = "https://statsapi.mlb.com/api/v1/schedule"
    params = {"sportId": 1, "season": season, "gameType": "R,F,D,L,W"}
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()

    games = []
    for day in data["dates"]:
        for game in day["games"]:
            games.append({
                "game_pk": game["gamePk"],
                "date": game["officialDate"],
                "season": season,
                "game_type": game["gameType"],
                "away": fix_team_name(game["teams"]["away"]["team"]["name"]),
                "home": fix_team_name(game["teams"]["home"]["team"]["name"]),
                "start_time": game["gameDate"],
                "status": game["status"]["detailedState"],
            })
    return pd.DataFrame(games)


def download_page(url):
    """Download a web page. Tries again if the connection or server fails, but stops if the site blocks us."""
    for attempt in range(3):
        try:
            response = requests.get(url, headers=HEADERS, timeout=60)
        except requests.exceptions.RequestException as error:
            print("  Connection problem, trying again in 10 seconds:", error)
            time.sleep(10)
            continue

        if response.status_code == 200:
            return response.text
        if response.status_code >= 500:  # a temporary problem on their end
            print(f"  Server error {response.status_code}, trying again in 10 seconds")
            time.sleep(10)
            continue
        # Something like 403 or 429 means the site doesn't want more requests right now
        raise Exception(f"Got status code {response.status_code} for {url}")

    raise Exception(f"Could not download {url} after 3 tries")


def get_games_from_page(html):
    """SBR pages keep all their data as JSON inside a <script id="__NEXT_DATA__"> tag."""
    match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if match is None:
        raise Exception("Couldn't find the odds data on the page (maybe the website changed)")

    page_data = json.loads(match.group(1))
    games = []
    for table in page_data["props"]["pageProps"]["oddsTables"]:
        games.extend(table["oddsTableModel"]["gameRows"])
    return games


def scrape_date(date):
    """Get moneyline, run line and total odds for every game on one date.
    Returns a DataFrame with one row per game, sportsbook and market."""
    rows = []
    for market, url in SBR_URLS.items():
        html = download_page(url.format(date))
        time.sleep(DELAY)

        for game in get_games_from_page(html):
            info = game["gameView"]
            for odds in game["oddsViews"]:
                if odds is None:  # this book has no odds for this game
                    continue
                opening = odds.get("openingLine") or {}
                current = odds.get("currentLine") or {}
                rows.append({
                    "date": date,
                    "market": market,
                    "sbr_game_id": info["gameId"],
                    "start_time": info["startDate"],
                    "away": info["awayTeam"]["fullName"],
                    "home": info["homeTeam"]["fullName"],
                    "book": odds["sportsbook"],
                    "open_away_odds": opening.get("awayOdds"),
                    "open_home_odds": opening.get("homeOdds"),
                    "open_home_spread": opening.get("homeSpread"),
                    "open_total": opening.get("total"),
                    "open_over_odds": opening.get("overOdds"),
                    "open_under_odds": opening.get("underOdds"),
                    "close_away_odds": current.get("awayOdds"),
                    "close_home_odds": current.get("homeOdds"),
                    "close_home_spread": current.get("homeSpread"),
                    "close_total": current.get("total"),
                    "close_over_odds": current.get("overOdds"),
                    "close_under_odds": current.get("underOdds"),
                })
    return pd.DataFrame(rows)


def implied_probability(odds):
    """Convert American odds to an implied probability.
    Examples: -150 -> 150 / 250 = 0.600,  +130 -> 100 / 230 = 0.435"""
    if pd.isna(odds):
        return None
    if odds < 0:
        return -odds / (-odds + 100)
    else:
        return 100 / (odds + 100)
