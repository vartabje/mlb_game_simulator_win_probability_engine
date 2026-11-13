# MLB Game Simulator and Win Probability Engine

This is Team 23's capstone project for the University of Michigan Master of Applied Data Science program. The goal is to estimate how likely each team is to win an MLB game by simulating the game many times from player statistics.

## Team

- Andrew Rebits
- Bradley Hofmeister
- Jeffrey Vartabedian
- Zain-Ul-Abidin Adhami

## Project status

Data collection is done. Two notebooks download the data, check it and save it as CSV files:

- **Season statistics** for MLB batters and pitchers, 2022 through 2026.
- **Game-level data** for every regular-season game from 2022 through 2026: schedules, final scores, starting lineups and pitchers, and bullpens. For 2022 through 2025 it also includes every plate appearance, runner movement and Statcast pitch. Those four seasons are for building the model. 2026 has no play-by-play data, so it can be held out for testing.
- **Game conditions** for every game from 2022 through 2026: temperature, sky or roof condition, wind, start times, attendance and umpires, from `notebooks/weather_scrape.ipynb`.

The files from the saved run are included, so you don't need to download anything to start working with the data.

The simulator itself is still planned. The [evaluation plan](project_deliverables/evaluation_plan_mini_deliverable_team_23.docx) and the implementation plan ([Word](project_deliverables/MLB_Game_Simulator_Implementation_Plan.docx), [PDF](project_deliverables/MLB_Game_Simulator_Implementation_Plan.pdf)) describe the intended approach:

- Simulate a game inning by inning about 1,000 times and turn the results into each team's win percentage.
- Compare those percentages with sportsbook odds on games held out from training.

No model or simulator has been built yet.

## What's in the repository

```text
notebooks/
  savant_scrape.ipynb            first exploration of data sources (2023 only, saves nothing)
  savant_scrape_updated.ipynb    collects and checks the season and game-level data
  weather_scrape.ipynb           collects game conditions (weather, start times, umpires)
data/raw/                        41 CSV files of season statistics, one row per player
data/games/                      48 CSV files of game-level data, keyed by game
project_deliverables/            course deliverables
requirements.txt                 Python package versions
```

### `data/raw/`: season statistics

Most files hold one season from one source. The file name tells you which: `savant_custom_batter_2024.csv` is 2024 batters from Baseball Savant, and `fangraphs_pitching_2025.csv` is 2025 pitchers from FanGraphs. The exception is `mlb_player_handedness.csv`, which has one row per player across all seasons.

The sources are kept in separate files. To combine them, match on MLB player ID and season. That's `player_id` and `year` in the Savant files, and `xMLBAMID` and `Season` in the FanGraphs files. Don't match on names, because the sources format them differently.

### `data/games/`: game-level data

Every table shares `game_pk`, MLB's game ID. Player columns such as `batter_id`, `pitcher_id` and `player_id` use the same MLB player IDs as `data/raw/`.

- `games.csv`: one row per game. `schedule_entries.csv` keeps every schedule listing, including postponed and suspended ones.
- `game_results.csv`: final scores and winners, for evaluating predictions only
- `game_coverage.csv`: whether each game is usable, flagged or excluded, and why. Check it before using a game.
- `lineups.csv`, `starting_pitchers.csv`, `bullpen_membership.csv`: who was available before each game
- `plate_appearances_<season>.csv`, `runner_movements_<season>.csv`, `between_pitch_events.csv`, `pitcher_appearances.csv`: play-by-play and pitcher usage, 2022–2025
- `savant_pitches/savant_pitches_<year>-<month>.csv`: Statcast pitches, 2022–2025
- `mlb_game_conditions.csv`: one row per game of every type, including spring training and the postseason, from `weather_scrape.ipynb`. MLB records these conditions at game time, so they are observations rather than forecasts. Indoor games show `Roof Closed` or `Dome` as the condition.

The raw API responses behind these tables are cached outside the repository, in `~/.cache/mlb_game_simulator`. You can change that location with the `MLB_GAME_CACHE_DIR` environment variable.

## Data sources

- [Baseball Savant](https://baseballsavant.mlb.com): season statistics, expected statistics, percentile rankings and Statcast pitches
- [FanGraphs](https://www.fangraphs.com): season batting and pitching leaderboards
- [MLB Stats API](https://statsapi.mlb.com): handedness, schedules, game feeds, box scores, rosters, transactions and game conditions

## Getting started

1. Create and activate a virtual environment, then install the pinned packages:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   source .venv/bin/activate     # macOS or Linux
   pip install -r requirements.txt
   ```

   The saved notebook run used Python 3.14. `requirements.txt` doesn't include a notebook editor, so open the notebooks in JupyterLab, VS Code or another editor you already use.

2. Open `notebooks/savant_scrape_updated.ipynb` and run all cells. The season files in `data/raw/` are checked and reused instead of downloaded again. The game-level section rebuilds its tables from the response cache and compares them with the saved CSVs. On a machine without that cache, the game-level section downloads everything again, which takes many hours.

3. To download fresh copies, set `OVERWRITE = True` in the configuration cell. To add a season, add it to `SEASONS` in the same cell. Only the missing files are downloaded.

4. `notebooks/weather_scrape.ipynb` builds `data/games/mlb_game_conditions.csv` from raw MLB game feeds. The saved CSV is all the other notebooks need. The raw feeds are one JSON Lines file of about 17 GB, shared through the team's Google folder rather than Git. To rebuild the CSV, put `game_score_raw_json.jsonl` in `data_files/` at the repository root, which Git ignores. Then run every cell except **Run the download**. That cell downloads the feeds again.

## Limitations

The statistics are full-season totals. A 2024 row includes every game from 2024.

Handedness tells you whether a player bats left, right or both. It doesn't show how players perform against left- or right-handed opponents. It also comes from MLB's current player profiles, not from each past season.

Some fields are empty in some seasons. For example, Savant's bat-tracking statistics start in 2023, so they're empty for 2022.

Bullpens are rebuilt from each team's previous game and the transactions since then, so they're approximate. The rebuilt bullpen exactly matches the staff MLB recorded for 20,240 of the 24,264 team-games checked. About 21,000 pitcher rows have `membership = uncertain`. Most of those come from roster moves dated on the game day, because MLB transactions have a date but no time. The `certainty` column gives the reason.

A few columns in the game tables are known only after the game, such as `status` and `first_pitch_utc` in `games.csv`. The notebook's "Game-level data" section lists them. Don't use them as prediction inputs.

## Deliverables

- [Evaluation plan](project_deliverables/evaluation_plan_mini_deliverable_team_23.docx)
- Implementation plan: [Word](project_deliverables/MLB_Game_Simulator_Implementation_Plan.docx), [PDF](project_deliverables/MLB_Game_Simulator_Implementation_Plan.pdf)
