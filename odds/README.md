# MLB Betting Odds, 2022–2026
This project collects opening and closing betting odds for every MLB regular season and playoff game
from 2022 to 2026, from three sportsbooks: **bet365, DraftKings and FanDuel**.

- Odds come from [SportsbookReview](https://www.sportsbookreview.com) (SBR), which shows historical odds for each date.

- Game IDs (`game_pk`) and schedules come from the free [MLB Stats API](https://statsapi.mlb.com).


## Files
| File | What it does |
|---|---|
| `01_collect_data.ipynb` | Downloads the MLB schedule and scrapes the odds from SBR for every game date |
| `02_build_dataset.ipynb` | Matches the odds to MLB games and builds the final CSV |
| `odds_helpers.py` | Functions used by both notebooks |
| `data/schedule.csv` | Every played game, 2022–2026 |
| `data/mlb_odds_2022_2026.csv` | The final dataset |

## How to run it
You will need Python 3 (tested on 3.13) with the packages in `requirements.txt` (`pip install -r requirements.txt`).

Open the notebooks in VS Code (or Jupyter), then run `01_collect_data.ipynb` and then `02_build_dataset.ipynb`.

The scraping in notebook 1 takes **about 3 hours** (1,031 game dates), because it waits 2 seconds after every page so it doesn't overload the website. Each date gets saved as it's scraped, so if it stops you can run it again and it will skip the dates it already has.

Set `TEST_RUN = True` to try it on just 3 dates first.

## The final dataset

**At a glance**
- 12,359 games (12,148 regular season, 211 playoff), 2022–2026, one row per game
- 79 columns: game info, plus moneyline, run line and total (open and close) for bet365, DraftKings and
  FanDuel, plus moneyline implied probabilities
- Each book has closing moneyline odds for about 94–100% of games per season; 111 games have none
  from any book (see "Some games are missing odds" below)
- Run lines are always ±1.5, totals are 5–15 runs, and odds are between -1000 and +1000 (run line odds
  within ±350 and total odds within ±200). Anything else was removed as a bad line

The first columns describe the game:

| Column | Description |
|---|---|
| `game_pk` | MLB's ID for the game |
| `date` | Game date |
| `season` | Year |
| `game_type` | regular, wild card, division series, league championship or world series |
| `away`, `home` | Team names (current names are used for every season, so the Oakland Athletics are "Athletics" in 2022–2024 too) |
| `start_time_utc` | Scheduled start time in UTC. For game 2 of some doubleheaders, MLB lists this as 5 minutes after game 1 instead of the real start time |

The odds columns are named `book_market_side_open/close`:

- **Books:** `b365` = bet365, `dk` = DraftKings, `fd` = FanDuel
- **Markets:** `ml` = moneyline, `rl` = run line, `total` = over/under

For example, for DraftKings:

| Columns | Description |
|---|---|
| `dk_ml_away_open`, `dk_ml_home_open`, `dk_ml_away_close`, `dk_ml_home_close` | Moneyline odds |
| `dk_rl_home_spread_open/close` | Home run line (-1.5 or +1.5; the away spread is the opposite) |
| `dk_rl_away_open/close`, `dk_rl_home_open/close` | Run line odds |
| `dk_total_open/close` | Over/under line (number of runs) |
| `dk_total_over_open/close`, `dk_total_under_open/close` | Over/under odds |
| `dk_ml_away_prob_open/close`, `dk_ml_home_prob_open/close` | Implied probability from the moneyline (includes the vig) |
| `dk_ml_away_novig_open/close`, `dk_ml_home_novig_open/close` | Implied probability with the vig removed (the two sides add up to 1) |

All odds are American odds (e.g. -150 or +130). A blank value means SBR didn't have odds from that book
(SBR sometimes shows these as 0), or the line was removed as a bad line (see below).

## Things to know

- **"Close" isn't guaranteed to be the exact closing line.** SBR shows an opening line and a "current" line.
  For past games the current line is the last one SBR saved, which is usually the closing line, but SBR
  doesn't promise it's the exact final price before first pitch.
- **Bad lines are removed.** About 1% of the time SBR saves a live in-game line as the "current" line, or
  mixes up the two games of a doubleheader. Notebook 2 compares each book's moneyline to the median of all
  the sportsbooks on SBR for that game, and if a book is more than 8 percentage points off, that book's
  open or close line for that game is blanked out (moneyline, run line and total).
- **Odds bigger than ±1000 are also removed.** This happens before the median check. Pregame MLB odds are
  almost never that big, so these are live in-game lines. This also catches live lines the median check
  would miss (when most books on SBR had a live line for the same game).
- **Odd run lines and totals are removed.** Only the standard ±1.5 run line is kept, and totals must be
  between 5 and 15 runs. Anything else (live lines, or junk values like 0 and 999) is blanked out along
  with its odds. This affects about 1% of run lines and 0.1% of totals.
- **Lopsided run line and total odds are removed.** Pregame run line odds stay within about ±300 and total
  odds within about ±150, so run line odds beyond ±350 or total odds beyond ±200 are live in-game lines
  (for example, a 12.5 total at +392/-620 for a game that opened at 7.5). Lines like this still have a normal
  margin, so the margin check below doesn't catch them. This removes 75 lines in 66 games, mostly 2026
  closing totals. Only that one line is removed; the rest of the game's odds are kept.
- **Lines with an impossible margin are removed.** A real pregame line always adds up to a bit more than 100%
  (the vig). If a book's two sides add up to less than 100% or more than 112%, it's a live in-game line, so it's
  blanked out. This removes 106 lines, almost all from 2026: closing run lines and totals that the moneyline
  check misses, plus bet365 opening run lines that SBR saved incorrectly (for example -1.5 at +160/+135).
  Only that one line is removed; the rest of the game's odds are kept.
- **Lines are removed as a whole.** If one side of a line is removed (for example, the home moneyline is
  over ±1000), the other side is removed too, along with the run line or total itself. So both sides of
  every line are either there or blank.
- **This check can't catch everything.** Sometimes the books on SBR split into two groups: some saved a live
  in-game line as the "current" line and the others saved the pregame line. What happens next depends on
  the split:
  - **The pregame books are the majority.** The median is a pregame line, so only the live lines are
    removed. This is the normal case.
  - **The groups are even and far apart** (more than 16 points). Every book ends up more than 8 points from
    the median, so every book's line is removed, including the good ones. This removed all the closing lines
    for 25 games (for example, 2022 World Series Game 1).
  - **The groups are even and fairly close.** Nothing gets removed.
  - **The live books are the majority.** The median is a live line, so the live lines are kept and the
    correct pregame line is removed. For example, for 2022-04-23 Rockies @ Tigers the dataset has a
    DraftKings "close" of -550/+360 (it opened at -105/-125), and bet365's close is blank.

  As a result, in 134 games (about 1%) our three books' closing moneylines still differ by more than
  8 points. Run lines and totals are only checked through the moneyline, the margin check and the lopsided
  check, so a few bad ones also remain: 17 games have a closing total 3 or more runs away from that book's
  opening total (for example, 2023-04-21 Athletics @ Rangers, where DraftKings goes from 8.5 to 11.5 while
  bet365 stays at 8.5). If you need clean closing lines, compare the books for the same game before using
  a line.
- **Some games are missing odds.** Notebook 2 shows how many games have odds from each book per season.
  111 games (under 1%) have no closing moneyline from any of the three books. They are still in the
  dataset, with blank odds:

  | Reason | Games |
  |---|---|
  | Doubleheader games, almost all ones where SBR only lists one of the two games | 33 |
  | Playoff games: 7 on dates with no odds on SBR at all (2022-10-23, 2022-11-05 and 2023-10-04), 9 that SBR doesn't list on its page for that date, and 2022 World Series Game 1 (closing lines all removed because the books split into two groups) | 17 |
  | Regular season games where every book's closing line was removed as a live line (mostly the books splitting into two groups, see above) | 29 |
  | Suspended games (see below) | 16 |
  | Regular season games SBR doesn't list on its page for that date (8 of these are on 2024-03-29, where SBR only has 2 of the 10 games) | 14 |
  | Games where SBR shows 0 for every book (2025-07-08 Blue Jays @ White Sox and 2025-07-09 Nationals @ Cardinals) | 2 |

- **Doubleheaders** are matched using the start time of each game (the earlier SBR game goes to game 1).
- **Suspended games** (games stopped partway and finished on a later day) are listed on the date they
  started, which is the date the pregame odds are for. SBR moves these games to the date they were
  finished, so they don't match and are left with blank odds. This is probably for the best: the odds SBR
  shows for them aren't always the pregame odds. For example, the "close" for 2024-06-26 Blue Jays @ Red Sox
  is exactly the close of the Aug 26 game between the same teams.
- Postponed and cancelled games are not included. Games that were postponed and made up later are
  included on the date they were actually played.

## Credit

The idea of reading odds from SBR's `__NEXT_DATA__` page data came from
[ArnavSaraogi/mlb-odds-scraper](https://github.com/ArnavSaraogi/mlb-odds-scraper).

Please check SportsbookReview's terms of use before sharing the raw data.

