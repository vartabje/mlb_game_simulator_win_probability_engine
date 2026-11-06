# MLB Game Simulator and Win Probability Engine

University of Michigan MADS capstone project, Team 23.

The goal is a model that estimates the chance each team has of winning an MLB game. It will simulate a game inning by inning from player statistics and game data, then repeat the simulation about 1,000 times. The share of simulated wins becomes each team's win probability, for example 60% vs. 40%.

## Current status

**Implemented: data collection only.** The repository contains notebooks that collect player-season statistics and the 41 CSV files they produced.

**Planned, not yet implemented** (from the [evaluation plan](project_deliverables/evaluation_plan_mini_deliverable_team_23.docx)):

- Game-level data for five historical seasons.
- The inning-by-inning game simulator and repeated-simulation win probabilities.
- Evaluation against sportsbook odds converted to win percentages. A prediction counts as a success when it is within ±5 percentage points of the sportsbook's figure. The team plans to adjust that range after seeing early results.
- An 80/20 train/test split of games, with test games held out from training.
- Checks for data leakage.

There is no model, simulation, game-level dataset, or merged player dataset in the repository yet.

## Repository structure

```text
.
├── README.md
├── requirements.txt
├── .gitignore
├── notebooks/
│   ├── savant_scrape.ipynb            # original exploration notebook (2023 only)
│   └── savant_scrape_updated.ipynb    # current data-collection notebook
├── data/
│   └── raw/                           # 41 CSV files written by savant_scrape_updated.ipynb
└── project_deliverables/
    └── evaluation_plan_mini_deliverable_team_23.docx
```

## Notebooks

### `notebooks/savant_scrape.ipynb` (original exploration)

This notebook tests data sources for the 2023 season using `pybaseball` and one direct request to Baseball Savant. It does not save any files. Its saved outputs show two problems:

- `pb.batting_stats()` returned an empty table with only an `IDfg` column.
- The pitcher percentile cell raised `NameError: name 'pitcher_columns' is not defined`.

### `notebooks/savant_scrape_updated.ipynb` (current collection)

This notebook calls each source directly with `requests` instead of `pybaseball`, covering five seasons. How it works:

- **Requests:** every request uses timeouts and retries only temporary errors (HTTP 429 and 5xx), pausing 2 seconds after each successful request.
- **Response checks:** HTML pages and empty CSVs are rejected.
- **Field names:** the Savant custom-leaderboard fields it requests are checked against the field names Savant's own page uses.
- **Saving:** each file is written to a temporary `.partial` file, read back to confirm it matches, then renamed into place.
- **Reruns:** existing files are re-validated and reused.
- **Validation section:** compares coverage, identifiers, missing values, and agreement between sources.

The saved outputs in this notebook come from a rerun in which every file already existed: all 41 files were reused and the run made 0 network requests.

## Data sources and coverage

Seasons: **2022, 2023, 2024, 2025, 2026** (set by `SEASONS` in the configuration cell).

| Source | Endpoint | What it provides |
|---|---|---|
| Baseball Savant custom leaderboard | `baseballsavant.mlb.com/leaderboard/custom` | 190 batter fields and 314 pitcher fields, including pitch repertoire |
| Baseball Savant expected statistics | `baseballsavant.mlb.com/leaderboard/expected_statistics` | Actual vs. expected BA, SLG and wOBA; ERA vs. xERA for pitchers |
| Baseball Savant percentile rankings | `baseballsavant.mlb.com/leaderboard/percentile-rankings` | 1-100 percentile **ranks** for qualified players (not raw statistics) |
| FanGraphs major-league leaderboards | `www.fangraphs.com/leaders/major-league` | Every FanGraphs batting (475) and pitching (544) column, read from the JSON embedded in the page |
| MLB Stats API | `statsapi.mlb.com/api/v1/people` | Each player's listed batting side and throwing hand |

## CSV contents (`data/raw/`)

Every season table has **one row per player per season**. Players traded mid-season have one combined row. Row counts below are from the notebook's recorded validation output.

| File pattern | Rows per season | Columns | Player ID | Season column |
|---|---|---|---|---|
| `savant_custom_batter_{season}.csv` | 651-693 | 193 | `player_id` (MLBAM) | `year` |
| `savant_custom_pitcher_{season}.csv` | 805-819 | 317 | `player_id` (MLBAM) | `year` |
| `savant_expected_stats_batter_{season}.csv` | 651-693 | 14 | `player_id` (MLBAM) | `year` |
| `savant_expected_stats_pitcher_{season}.csv` | 855-873 | 17 | `player_id` (MLBAM) | `year` |
| `savant_percentile_ranks_batter_{season}.csv` | 606-628 | 23 | `player_id` (MLBAM) | `year` |
| `savant_percentile_ranks_pitcher_{season}.csv` | 696-712 | 22 | `player_id` (MLBAM) | `year` |
| `fangraphs_batting_{season}.csv` | 1,454-1,495 | 475 | `playerid` (FanGraphs); `xMLBAMID` (MLBAM) | `Season` |
| `fangraphs_pitching_{season}.csv` | 855-873 | 544 | `playerid` (FanGraphs); `xMLBAMID` (MLBAM) | `Season` |
| `mlb_player_handedness.csv` | 2,635 players (not seasonal) | 8 | `player_id` (MLBAM) | none |

The tables are separate files; nothing is merged. For later joins, use the MLBAM player ID plus season: (`player_id`, `year`) in Savant tables and (`xMLBAMID`, `Season`) in FanGraphs tables. Don't join on player names, because the formats differ between sources.

Notes on reading the data:

- **FanGraphs batting** also lists pitchers with 0 plate appearances.
- **Innings** (`p_formatted_ip` on Savant, `IP` on FanGraphs) use baseball notation: `61.1` means 61⅓ innings.
- **Two plate-appearance counts:** Savant has both a Statcast-tracked count (`pa`) and a standard count (`b_total_pa`, `p_total_pa`). In the recorded validation, the standard counts matched FanGraphs `PA` for 99.7-100% of batters and `TBF` for 100% of pitchers.

## Setup

The recorded run used Python 3.14.0 on Windows.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

`requirements.txt` pins `pandas==3.1.0` and `requests==2.34.2`. The current notebook imports only those two plus the Python standard library. `pybaseball==2.2.7` is needed only for the original exploration notebook. `ipykernel` is included, but a notebook front end (JupyterLab, Jupyter Notebook, or the VS Code Jupyter extension) is not.

## Running the collection notebook

Open `notebooks/savant_scrape_updated.ipynb` and run all cells. The notebook finds the repository root on its own, so it works whether Jupyter starts in the repository root or in `notebooks/`.

Settings in the configuration cell:

| Setting | Default | Effect |
|---|---|---|
| `SEASONS` | `[2022, 2023, 2024, 2025, 2026]` | Seasons to collect |
| `OVERWRITE` | `False` | `False` re-validates and reuses existing files. `True` downloads them again. |
| `SAVANT_CUSTOM_MIN_BATTER` / `SAVANT_CUSTOM_MIN_PITCHER` | `0` / `0` | Minimum plate appearances (batters) or innings pitched (pitchers) |
| `SAVANT_XSTATS_MIN_PA` | `0` | Minimum plate appearances for expected statistics |
| `FANGRAPHS_QUAL` | `0` | Minimum PA (batting) or IP (pitching) on FanGraphs |
| `REQUEST_PAUSE_SECONDS` | `2` | Pause after each successful request |

Because every CSV is already in `data/raw/`, running the notebook with the defaults reuses the files and makes no network requests.

- **Adding a season:** add it to `SEASONS`. Only the missing files are downloaded, and only new player IDs are looked up for handedness.
- **Problem files:** a file that fails validation stops the run instead of being replaced.

## Limitations

- **Full-season statistics leak future information.** A 2024 row includes games played after any given 2024 date. Same-season rows shouldn't be used as information known before a 2024 game. This matters for the evaluation plan's random train/test split of games across seasons.
- **Handedness is not a performance split.** `mlb_player_handedness.csv` records whether a player bats left, right, or switch (`S`) and which hand they throw with. It is MLB's current listed profile, not a per-season or per-plate-appearance record. There is no data on how players perform against left- or right-handed opponents.
- **No game-level data.** The repository has no schedules, lineups, ballparks, dome/roof status, weather, or sportsbook odds.
- **Missing or partial fields.** The validation output reports these gaps but doesn't fill them:
  - bat-tracking fields are empty in 2022 and partly filled in 2023
  - repertoire columns are empty for pitches a pitcher doesn't throw
  - defensive fields apply only to some positions
  - some FanGraphs columns are empty in some seasons
- **Different player lists.** The Savant custom pitcher board omits 49-61 pitchers per season, mostly position players who pitched. They appear in Savant expected statistics and FanGraphs. Percentile rankings cover qualified players only.
- **Source disagreements.** One player (MLBAM 666801) is listed as a switch hitter by FanGraphs and as right-handed by MLB.
- **FanGraphs format.** FanGraphs data is read from an undocumented JSON block in its public page. If that format changes, the notebook stops with an error.

## Project deliverables

- [Evaluation plan mini-deliverable (Team 23)](project_deliverables/evaluation_plan_mini_deliverable_team_23.docx)

## Credits

- Original exploration notebook (`notebooks/savant_scrape.ipynb`) and repository: Jeffrey ([vartabje](https://github.com/vartabje)).
- Updated collection notebook and collected data: Zainulabidin Adhami.
- Evaluation plan: Team 23.
