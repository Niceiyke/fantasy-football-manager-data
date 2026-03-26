# Niceiyke's Fantasy Football Manager Data Repository

Maintained by Niceiyke.

Lean Fantasy Premier League data repository for analytics, modeling, and downstream product use.

This repo is no longer trying to preserve every scraper output from the original upstream project. It is now focused on a smaller set of high-value datasets that are useful for weekly analysis and long-term historical work.

This repository was originally forked from Vaastav Anand's Fantasy Premier League dataset project and has been repurposed into a leaner analytics-focused maintenance repo.

## Scope

Maintained seasons:

- `2020-21`
- `2021-22`
- `2022-23`
- `2023-24`
- `2024-25`
- `2025-26`

Maintained files per season:

- `data/<season>/gws/gw<gw>.csv`
- `data/<season>/gws/merged_gw.csv`
- `data/<season>/players_raw.csv`
- `data/<season>/cleaned_players.csv`
- `data/<season>/fixtures.csv`
- `data/<season>/teams.csv`
- `data/<season>/gws/xP<gw>.csv` when captured before deadline
- `data/<season>/gws/status<gw>.csv` when captured before deadline
- `data/<season>/gws/ownership<gw>.csv` when captured before deadline

Everything else has been trimmed out to keep the repo lighter and easier to maintain.

## Data Layout

Each season folder is structured around the files that matter most for analytics:

- `players_raw.csv`
  Current FPL bootstrap snapshot for the season. Includes live fields like price, ownership, position, availability, `ep_this`, `ep_next`, and season totals.

- `cleaned_players.csv`
  Smaller, cleaner player summary file with common columns used in quick analysis.

- `fixtures.csv`
  Fixture list for the season, including fixture ids, teams, kickoff times, scores, and event mappings.

- `teams.csv`
  Team reference table used to resolve team ids and names.

- `gws/gw<gw>.csv`
  Player-by-player data for a single gameweek.

- `gws/merged_gw.csv`
  All gameweeks combined into one table with a `GW` column. This is usually the main file for modeling and analysis.

- `gws/xP<gw>.csv`
  Saved expected-points snapshot for a given gameweek, captured from FPL live data before that week starts.

- `gws/status<gw>.csv`
  Saved player availability snapshot for a given gameweek, including fields like `status`, `news`, and chance-of-playing values before they change later.

- `gws/ownership<gw>.csv`
  Saved player ownership snapshot for a given gameweek, including fields like `selected_by_percent` and ownership ranks before they move later.

## What Each File Is For

`gw<gw>.csv`

- Best when you want to inspect one specific gameweek.
- Useful for debugging weekly pipelines, validating points, and building weekly reports.

`merged_gw.csv`

- Best file for historical analysis.
- Useful for machine learning, backtesting, trend analysis, and dashboards.

`players_raw.csv`

- Best file for the current state of the game.
- Useful when your app needs current price, ownership, status, `ep_this`, `ep_next`, and live totals.

`cleaned_players.csv`

- Best for lightweight joins and simpler exploratory analysis.

`fixtures.csv`

- Needed for opponent context, fixture timing, home/away mapping, BGW/DGW logic, and schedule-aware analysis.

`teams.csv`

- Needed to resolve team ids cleanly and support team-level analysis.

`xP<gw>.csv`

- Important if you care about preserving historical FPL expected points.
- Once a gameweek passes, true historical FPL xP is usually not recoverable unless it was saved ahead of time.

`status<gw>.csv`

- Important if you care about preserving injury, suspension, and availability context before that gameweek starts.
- Useful because FPL player status and news text are live fields that change and can disappear later.

`ownership<gw>.csv`

- Important if you care about preserving pre-deadline ownership context for historical analysis.
- Useful because FPL ownership percentages and ranks are live fields that move continuously throughout the week.

## Update Workflow

There are two different update moments each week.

### 1. Before the deadline

Capture the next gameweek's FPL expected-points, status, and ownership snapshots:

```bash
python automation.py capture-xp
```

This writes:

- `data/<season>/gws/xP<gw>.csv`
- `data/<season>/gws/status<gw>.csv`
- `data/<season>/gws/ownership<gw>.csv`

You can also force a specific week:

```bash
python automation.py capture-xp --season 2025-26 --gw 31
```

If you need to recreate only an ownership snapshot from the ownership fields currently stored in `players_raw.csv`:

```bash
python automation.py backfill-ownership --season 2025-26 --gw 31
```

This is a repair utility, not true historical recovery. It copies whatever ownership values are currently in `players_raw.csv` into `ownership<gw>.csv`.

### 2. After the gameweek is finished

Refresh the latest finished gameweek and regenerate merged data:

```bash
python automation.py rebuild-latest
```

This updates:

- `gws/gw<gw>.csv`
- `gws/merged_gw.csv`
- `players_raw.csv`
- `cleaned_players.csv`
- `fixtures.csv`
- `teams.csv`

You can also force a specific week:

```bash
python update_gameweek.py --season 2025-26 --gw 30
```

## Fixtures-Only Update

If you only want to refresh team and fixture information:

```bash
python update_fixtures.py --season 2025-26
```

This updates:

- `data/2025-26/fixtures.csv`
- `data/2025-26/teams.csv`

## Automation

GitHub Actions workflows are included:

- `.github/workflows/capture-xp.yml`
- `.github/workflows/update-latest-finished-gw.yml`

Recommended usage:

- run `Capture Next GW Snapshots` before each deadline
- run `Update Latest Finished GW` after the final match of the week

The workflows can run on schedule or manually from the GitHub Actions tab.

## Notes About xP

This repo stores historical FPL expected points as `xP<gw>.csv`.

Important caveat:

- repo `xP` is captured from FPL live `ep_this`
- player availability is captured from live `status`, `news`, `chance_of_playing_this_round`, and `chance_of_playing_next_round`
- ownership is captured from live `selected_by_percent`, `selected_rank`, and `selected_rank_type`
- if a snapshot was not saved before that gameweek passed, it usually cannot be reconstructed later
- actual gameweek stats can still be rebuilt from FPL player history, but historical FPL xP usually cannot

## Python Example

```python
import pandas as pd

df = pd.read_csv("data/2025-26/gws/merged_gw.csv")
print(df.head())
```

## Data Dictionary

See [DATA_DICTIONARY.md](DATA_DICTIONARY.md) for field descriptions.

## Repo Goal

The goal of this repo is simple:

- keep a clean historical FPL dataset from `2020-21` onward
- update the current season reliably every week
- preserve the files that are most useful for future analytics

## Weekly Maintenance Checklist

Use this as the default weekly operating routine.

Before the deadline:

```bash
python automation.py capture-xp
```

After the final match of the gameweek:

```bash
python automation.py rebuild-latest
```

If you only need fixture updates:

```bash
python update_fixtures.py --season 2025-26
```

Files worth checking before commit:

- `data/<season>/gws/xP<gw>.csv`
- `data/<season>/gws/status<gw>.csv`
- `data/<season>/gws/ownership<gw>.csv`
- `data/<season>/gws/gw<gw>.csv`
- `data/<season>/gws/merged_gw.csv`
- `data/<season>/players_raw.csv`
- `data/<season>/cleaned_players.csv`
- `data/<season>/fixtures.csv`
- `data/<season>/teams.csv`
