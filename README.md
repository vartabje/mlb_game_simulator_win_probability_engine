# MLB Game Simulator and Win Probability Engine

This is Team 23's capstone project for the University of Michigan Master of Applied Data Science program. The goal is to estimate how likely each team is to win an MLB game by simulating the game many times from player statistics.

## Team

- Andrew Rebits
- Bradley Hofmeister
- Jeffrey Vartabedian
- Zain-Ul-Abidin Adhami

## Project status

So far, the repository covers data collection. A notebook downloads season statistics for MLB batters and pitchers from 2022 through 2026, checks each download, and saves the results as CSV files. The files from that run are included, so you don't need to download anything to start working with the data.

The simulator itself is still planned. Our [evaluation plan](project_deliverables/evaluation_plan_mini_deliverable_team_23.docx) describes the intended approach:

- Simulate a game inning by inning about 1,000 times and turn the results into each team's win percentage.
- Compare those percentages with sportsbook odds on games held out from training.

None of this is built yet. There is no model, simulator or game-level data in the repository.

## What's in the repository

```text
notebooks/
  savant_scrape.ipynb            first exploration of data sources (2023 only, saves nothing)
  savant_scrape_updated.ipynb    collects and checks the data used now
data/raw/                        41 CSV files written by savant_scrape_updated.ipynb
project_deliverables/            course deliverables
requirements.txt                 Python package versions
```

Most CSV files hold one season from one source, with one row per player. The file name tells you which: `savant_custom_batter_2024.csv` is 2024 batters from Baseball Savant, and `fangraphs_pitching_2025.csv` is 2025 pitchers from FanGraphs. The exception is `mlb_player_handedness.csv`, which has one row per player across all seasons.

The sources are kept in separate files. To combine them, match on MLB player ID and season. That's `player_id` and `year` in the Savant files, and `xMLBAMID` and `Season` in the FanGraphs files. Don't match on names, because the sources format them differently.

## Data sources

- [Baseball Savant](https://baseballsavant.mlb.com): season statistics, expected statistics and percentile rankings
- [FanGraphs](https://www.fangraphs.com): season batting and pitching leaderboards
- [MLB Stats API](https://statsapi.mlb.com): which side each player bats from and which hand they throw with

## Getting started

1. Create and activate a virtual environment, then install the pinned packages:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   source .venv/bin/activate     # macOS or Linux
   pip install -r requirements.txt
   ```

   The saved notebook run used Python 3.14. `requirements.txt` doesn't include a notebook editor, so open the notebooks in JupyterLab, VS Code or another editor you already use.

2. Open `notebooks/savant_scrape_updated.ipynb` and run all cells. Because the CSV files are already in `data/raw/`, the notebook checks and reuses them instead of downloading again.

3. To download fresh copies, set `OVERWRITE = True` in the configuration cell. To add a season, add it to `SEASONS` in the same cell. Only the missing files are downloaded.

## Limitations

The statistics are full-season totals. A 2024 row includes every game from 2024, so it shouldn't be used to predict a 2024 game.

Handedness tells you whether a player bats left, right or both. It doesn't show how players perform against left- or right-handed opponents. It also comes from MLB's current player profiles, not from each past season.

Some fields are empty in some seasons. For example, Savant's bat-tracking statistics start in 2023, so they're empty for 2022.

## Deliverables

- [Evaluation plan](project_deliverables/evaluation_plan_mini_deliverable_team_23.docx)
