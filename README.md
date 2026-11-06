# MLB Game Simulator and Win Probability Engine

University of Michigan MADS capstone, Team 23.

We're building a tool to estimate each team's chance of winning an MLB game.

## Team

- Andrew Rebits
- Bradley Hofmeister
- Jeffrey Vartabedian
- Zain-Ul-Abidin Adhami

## Status

**Done so far:** collecting player statistics. The notebooks download player-season stats for 2022-2026 and save them as CSV files.

**Planned** (from the [evaluation plan](project_deliverables/evaluation_plan_mini_deliverable_team_23.docx)):

- Simulate games inning by inning and repeat each game about 1,000 times to get win percentages.
- Compare those percentages with sportsbook odds on games held out from training.

There is no model or simulator in the repository yet.

## What's in the repository

| Path | Contents |
|---|---|
| `notebooks/savant_scrape.ipynb` | First exploration of data sources (2023 only, saves no files) |
| `notebooks/savant_scrape_updated.ipynb` | Current notebook that collects and checks the data |
| `data/raw/` | 41 CSV files produced by the current notebook |
| `project_deliverables/` | Course deliverables |
| `requirements.txt` | Python package versions |

Each season file in `data/raw/` has one row per player per season. Files are named by source, player type and season, for example `savant_custom_batter_2024.csv` or `fangraphs_pitching_2025.csv`. The one exception is `mlb_player_handedness.csv`, which has one row per player.

The files are kept separate, not merged. To combine them later, match on MLB player ID and season: `player_id` and `year` in Savant files, `xMLBAMID` and `Season` in FanGraphs files.

## Data sources

| Source | What we collect |
|---|---|
| [Baseball Savant](https://baseballsavant.mlb.com) | Season stats, expected stats, and percentile rankings for batters and pitchers |
| [FanGraphs](https://www.fangraphs.com) | Season batting and pitching leaderboards |
| [MLB Stats API](https://statsapi.mlb.com) | Which side each player bats from and which hand they throw with |

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
```

The saved notebook run used Python 3.14. You'll also need a way to open notebooks, such as JupyterLab or VS Code. `requirements.txt` doesn't include one.

Open `notebooks/savant_scrape_updated.ipynb` and run all cells. The CSVs are already in `data/raw/`, so the notebook reuses them instead of downloading again. To download again, set `OVERWRITE = True` in the configuration cell.

## Limitations

- **Stats cover full seasons.** A 2024 row includes games from the whole 2024 season. It shouldn't be used to predict a 2024 game, because it contains results from after that game.
- **Handedness isn't a split.** We record whether a player bats left, right or both. We don't have stats on how players perform against left- or right-handed opponents. Handedness comes from MLB's current player profiles, not from each past season.
- **No game data yet.** There are no schedules, lineups, ballparks, weather or betting odds.
- **Some fields are missing.** For example, Savant's bat-tracking stats are empty for 2022.

## Deliverables

- [Evaluation plan](project_deliverables/evaluation_plan_mini_deliverable_team_23.docx)
