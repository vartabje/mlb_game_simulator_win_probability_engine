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

A first version of the simulator is built in `notebooks/game_simulator.ipynb`, following the implementation plan ([Word](project_deliverables/MLB_Game_Simulator_Implementation_Plan.docx), [PDF](project_deliverables/MLB_Game_Simulator_Implementation_Plan.pdf)). It simulates each game one plate appearance at a time about 1,000 times and turns the share of simulated wins into each team's win probability. It's developed on 2022-2025 and tested as a retrospective backtest on the completed 2026 season, against actual results. The earlier [evaluation plan](project_deliverables/evaluation_plan_mini_deliverable_team_23.docx) proposed comparing with sportsbook odds; that comparison isn't part of this run. See [Running the simulator](#running-the-simulator).

## What's in the repository

```text
notebooks/
  savant_scrape_updated.ipynb    collects and checks the season and game-level data
  weather_scrape.ipynb           collects game conditions (weather, start times, umpires)
  game_simulator.ipynb           builds the simulator, tunes it on 2022-2025 and backtests 2026
data/raw/                        41 CSV files of season statistics, one row per player
data/games/                      48 CSV files of game-level data, keyed by game
data/simulation/                 simulator settings, 2026 predictions, evaluation tables and figures
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

1. Create a virtual environment with Python 3.14, install the pinned packages with that environment's Python, and register it as a Jupyter kernel:

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\python -m pip install -r requirements.txt
   .venv\Scripts\python -m ipykernel install --user --name mlb-game-simulator --display-name "Python (mlb-game-simulator)"
   # macOS or Linux
   .venv/bin/python -m pip install -r requirements.txt
   .venv/bin/python -m ipykernel install --user --name mlb-game-simulator --display-name "Python (mlb-game-simulator)"
   ```

   `requirements.txt` covers all three notebooks but doesn't include a notebook editor, so open the notebooks in JupyterLab, VS Code or another editor you already use. In the editor, choose the kernel **Python (mlb-game-simulator)**, or in VS Code the `.venv` interpreter. The generic "Python 3" kernel can start a different Python that lacks these packages.

2. Open `notebooks/savant_scrape_updated.ipynb` and run all cells. The season files in `data/raw/` are checked and reused instead of downloaded again. The game-level section rebuilds its tables from the response cache and compares them with the saved CSVs. On a machine without that cache, the game-level section downloads everything again, which takes many hours.

3. To download fresh copies, set `OVERWRITE = True` in the configuration cell. To add a season, add it to `SEASONS` in the same cell. Only the missing files are downloaded.

4. `notebooks/weather_scrape.ipynb` builds `data/games/mlb_game_conditions.csv` from raw MLB game feeds. The saved CSV is all the other notebooks need. The raw feeds are one JSON Lines file of about 17 GB, shared through the team's Google folder rather than Git. To rebuild the CSV, put `game_score_raw_json.jsonl` in `data_files/` at the repository root, which Git ignores. Then run every cell except **Run the download**. That cell downloads the feeds again.

## Running the simulator

Open `notebooks/game_simulator.ipynb` and run all cells from a fresh kernel. It reads only the saved CSVs in `data/games/` and `data/raw/`, so the collection notebooks don't need to be rerun first. A full run takes about 20-25 minutes and needs numpy, pandas, scipy and matplotlib. The saved run used Python 3.14.0 with numpy 2.4.2, pandas 3.0.1, scipy 1.17.1 and matplotlib 3.10.8. With the versions in `requirements.txt`, the notebook's correctness tests pass and a sample of 2026 games reproduces the saved predictions exactly. A full rerun with them hasn't been done.

The notebook:

1. Checks the game tables and builds player rates, log5 matchup probabilities, runner tables and a starter-removal model from development seasons only.
2. Runs correctness tests of the probabilities and game rules, and a timing pilot.
3. Chooses its settings on 2024 using 2022-2023, then checks them once on 2025 using 2022-2024.
4. Rebuilds everything from 2022-2025, simulates every 2026 game 1,000 times, and saves the predictions with a hash before reading any 2026 result.
5. Scores the predictions against actual 2026 results and two simple baselines.
6. Runs the weather comparison described below and saves it separately.

Outputs in `data/simulation/`:

- `run_settings.json`: chosen settings, seeds, model coefficients, package versions and the predictions hash
- `development_comparison.csv`, `development_games.csv`: 2024 tuning and the 2025 check
- `predictions_2026.csv`: one row per simulated 2026 game, with fallback counts
- `evaluation_2026.csv`, `calibration_2026.csv`, `coverage_2026.csv`, `calibration_2026.png`, `runs_2026.png`
- `weather_development.csv`, `weather_settings.json`, `weather_predictions_2026.csv`, `weather_evaluation_2026.csv`: the weather comparison

A rerun must reproduce every existing output exactly, or it stops. To replace outputs on purpose, set `OVERWRITE_RESULTS = True` in the configuration cell.

The evaluation is conditional on each game's actual starting lineups and starting pitchers. Simplifications in this first version:

- The nine starters bat all game.
- After the starter leaves, each team pitches with one pooled bullpen profile. Individual relievers, their rest and the three-batter minimum aren't represented.
- Players without 2022-2025 history get league-average rates. That is about 9.5% of 2026 lineup slots; newcomers usually hit worse than average.
- There is no home-field advantage beyond batting last. The 2026 predictions average 50% for home teams, while home teams won 52.9%.
- Simulated games average about 9.1 runs, against 9.0 in 2026 and 8.8-8.9 in the 2024-2025 development checks.

### Weather comparison

Weather is tested as an extension and isn't part of the main result. The conditions table joins one to one with every game on `game_pk`.

- **How weather enters:** it changes each plate appearance's outcome probabilities, as a multiplier on the log5 probabilities fitted by maximum likelihood. Runner tables and pitching changes aren't affected.
- **Predictors:** temperature, and wind speed blowing out or in. Both are measured against the park's usual outdoor conditions in the training seasons, so park effects don't enter.
- **No adjustment:** indoor games (dome or roof closed), games with missing conditions, and parks with fewer than 30 outdoor games of history keep the baseline probabilities exactly.
- **Training:** coefficients come only from earlier seasons; for 2026, from 2023-2025.
- **Coefficients:** home runs rise about 10% per 10 °F warmer than the park's norm, and about 7% per 10 mph blowing out.

The 2026 comparison covers the same 2,429 games, with the same 1,000 simulations and the same seeds as the baseline, and a second seed as a check. 1,956 games (81%) were adjusted.

- **Plate appearances (development):** log loss improved slightly in both checks, by 0.00014 in 2024 and 0.00020 in 2025, with intervals below zero.
- **Games (2026):** log loss was 0.6893 against 0.6887 for the baseline, and Brier score 0.2481 against 0.2478. Both are slightly worse with both seeds, and the intervals include zero.
- **Total runs (2026):** slightly better. The mean absolute error fell by about 0.01 runs, and the correlation with actual totals rose from about 0.05 to 0.10.

Weather shifts how many runs both teams score more than it shifts who wins. The baseline therefore stays the default, as the decision rule set before the 2026 results required. MLB records conditions at game time, so this test is also optimistic compared with pregame forecasts.

## Limitations

The statistics are full-season totals. A 2024 row includes every game from 2024.

Handedness tells you whether a player bats left, right or both. It doesn't show how players perform against left- or right-handed opponents. It also comes from MLB's current player profiles, not from each past season.

Some fields are empty in some seasons. For example, Savant's bat-tracking statistics start in 2023, so they're empty for 2022.

Bullpens are rebuilt from each team's previous game and the transactions since then, so they're approximate. The rebuilt bullpen exactly matches the staff MLB recorded for 20,240 of the 24,264 team-games checked. About 21,000 pitcher rows have `membership = uncertain`. Most of those come from roster moves dated on the game day, because MLB transactions have a date but no time. The `certainty` column gives the reason.

A few columns in the game tables are known only after the game, such as `status` and `first_pitch_utc` in `games.csv`. The notebook's "Game-level data" section lists them. Don't use them as prediction inputs.

## Deliverables

- [Evaluation plan](project_deliverables/evaluation_plan_mini_deliverable_team_23.docx)
- Implementation plan: [Word](project_deliverables/MLB_Game_Simulator_Implementation_Plan.docx), [PDF](project_deliverables/MLB_Game_Simulator_Implementation_Plan.pdf)
