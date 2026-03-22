import argparse
import os

from getters import get_data, get_fixtures_data
from parsers import parse_fixtures, parse_team_data


def update_fixtures_and_teams(season):
    base_dir = os.path.join("data", season) + "/"
    os.makedirs(base_dir, exist_ok=True)

    print(f"Updating fixtures for {season}")
    parse_fixtures(get_fixtures_data(), base_dir)

    print(f"Updating teams for {season}")
    data = get_data()
    parse_team_data(data["teams"], base_dir)

    print(f"Finished updating fixtures and teams for {season}")


def main():
    parser = argparse.ArgumentParser(
        description="Update fixtures.csv and teams.csv for a season."
    )
    parser.add_argument("--season", default="2025-26", help="Season folder, e.g. 2025-26")
    args = parser.parse_args()

    update_fixtures_and_teams(args.season)


if __name__ == "__main__":
    main()
