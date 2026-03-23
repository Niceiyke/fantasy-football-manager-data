import argparse
import csv
import os
import tempfile

from cleaners import clean_players
from collector import collect_gw, regenerate_merged_gw
from getters import get_data, get_fixtures_data, get_individual_player_data
from parsers import (
    parse_fixtures,
    parse_player_gw_history,
    parse_players,
    parse_team_data,
)


def refresh_season_basics(base_dir, data):
    parse_players(data["elements"], base_dir)
    clean_players(os.path.join(base_dir, "players_raw.csv"), base_dir)
    parse_team_data(data["teams"], base_dir)
    parse_fixtures(get_fixtures_data(), base_dir)


def get_player_ids_from_data(data):
    return {
        player["id"]: f"{player['first_name']}_{player['second_name']}"
        for player in data["elements"]
    }


def refresh_player_histories(players_dir, player_ids):
    for player_id, player_name in player_ids.items():
        player_data = get_individual_player_data(player_id)
        parse_player_gw_history(
            player_data["history"], players_dir, player_name, player_id
        )


def write_expected_points(base_dir, gw, data):
    gw_dir = os.path.join(base_dir, "gws")
    os.makedirs(gw_dir, exist_ok=True)
    out_path = os.path.join(gw_dir, f"xP{gw}.csv")
    rows = [{"id": e["id"], "xP": e["ep_this"]} for e in data["elements"]]
    with open(out_path, "w", newline="", encoding="utf-8") as outf:
        writer = csv.DictWriter(outf, fieldnames=["id", "xP"])
        writer.writeheader()
        writer.writerows(rows)


def write_player_status_snapshot(base_dir, gw, data):
    gw_dir = os.path.join(base_dir, "gws")
    os.makedirs(gw_dir, exist_ok=True)
    out_path = os.path.join(gw_dir, f"status{gw}.csv")
    fieldnames = [
        "id",
        "status",
        "news",
        "chance_of_playing_this_round",
        "chance_of_playing_next_round",
    ]
    rows = []
    for player in data["elements"]:
        rows.append(
            {
                "id": player["id"],
                "status": player.get("status", ""),
                "news": player.get("news", ""),
                "chance_of_playing_this_round": player.get(
                    "chance_of_playing_this_round", ""
                ),
                "chance_of_playing_next_round": player.get(
                    "chance_of_playing_next_round", ""
                ),
            }
        )

    with open(out_path, "w", newline="", encoding="utf-8") as outf:
        writer = csv.DictWriter(outf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def update_gameweek(season, gw, write_xp=False):
    base_dir = os.path.join("data", season) + "/"
    gw_dir = os.path.join(base_dir, "gws")

    print(f"Refreshing season metadata for {season}")
    data = get_data()
    refresh_season_basics(base_dir, data)

    print(f"Refreshing player histories for {season}")
    player_ids = get_player_ids_from_data(data)

    if write_xp:
        print(f"Writing xP snapshot for GW{gw}")
        write_expected_points(base_dir, gw, data)
        print(f"Writing player status snapshot for GW{gw}")
        write_player_status_snapshot(base_dir, gw, data)

    with tempfile.TemporaryDirectory(prefix=f"fpl-{season}-gw{gw}-") as temp_dir:
        players_dir = os.path.join(temp_dir, "players") + "/"
        refresh_player_histories(players_dir, player_ids)

        print(f"Collecting GW{gw}")
        collect_gw(gw, players_dir, gw_dir, base_dir)

    print("Regenerating merged_gw.csv")
    regenerate_merged_gw(gw_dir)

    print(f"Finished updating {season} GW{gw}")


def main():
    parser = argparse.ArgumentParser(
        description="Backfill or refresh a specific FPL gameweek for a season."
    )
    parser.add_argument("--season", default="2025-26", help="Season folder, e.g. 2025-26")
    parser.add_argument("--gw", type=int, required=True, help="Gameweek number to build")
    parser.add_argument(
        "--write-xp",
        action="store_true",
        help="Write xP and player status snapshots for the chosen GW using the current bootstrap payload.",
    )
    args = parser.parse_args()

    update_gameweek(args.season, args.gw, write_xp=args.write_xp)


if __name__ == "__main__":
    main()
