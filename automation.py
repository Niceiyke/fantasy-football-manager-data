import argparse
import os
from datetime import datetime, timezone

from getters import get_data
from update_gameweek import update_gameweek, write_expected_points


def detect_season(today=None):
    today = today or datetime.now(timezone.utc).date()
    start_year = today.year if today.month >= 7 else today.year - 1
    end_year = (start_year + 1) % 100
    return f"{start_year}-{end_year:02d}"


def resolve_season(season):
    return season or detect_season()


def get_event_id(data, *, target):
    events = data["events"]

    if target == "next":
        for event in events:
            if event.get("is_next"):
                return event["id"]
        raise ValueError("Could not find the next gameweek in bootstrap data")

    if target == "current":
        for event in events:
            if event.get("is_current"):
                return event["id"]
        raise ValueError("Could not find the current gameweek in bootstrap data")

    if target == "latest_finished":
        finished = [event["id"] for event in events if event.get("finished")]
        if not finished:
            raise ValueError("Could not find a finished gameweek in bootstrap data")
        return max(finished)

    raise ValueError(f"Unknown target: {target}")


def capture_xp(season, gw=None, target="next"):
    season = resolve_season(season)
    data = get_data()
    resolved_gw = gw or get_event_id(data, target=target)
    base_dir = os.path.join("data", season) + "/"
    os.makedirs(os.path.join(base_dir, "gws"), exist_ok=True)
    write_expected_points(base_dir, resolved_gw, data)
    print(f"Wrote xP snapshot for {season} GW{resolved_gw}")


def rebuild_latest_finished(season, gw=None):
    season = resolve_season(season)
    data = get_data()
    resolved_gw = gw or get_event_id(data, target="latest_finished")
    update_gameweek(season, resolved_gw, write_xp=False)


def main():
    parser = argparse.ArgumentParser(description="Automation helpers for FPL data updates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    xp_parser = subparsers.add_parser("capture-xp", help="Capture an xP snapshot")
    xp_parser.add_argument(
        "--season",
        help="Season folder, e.g. 2025-26. Defaults to the active season.",
    )
    xp_parser.add_argument("--gw", type=int)
    xp_parser.add_argument(
        "--target",
        choices=["next", "current"],
        default="next",
        help="Used only when --gw is omitted",
    )

    rebuild_parser = subparsers.add_parser(
        "rebuild-latest", help="Rebuild the latest finished GW"
    )
    rebuild_parser.add_argument(
        "--season",
        help="Season folder, e.g. 2025-26. Defaults to the active season.",
    )
    rebuild_parser.add_argument("--gw", type=int)

    args = parser.parse_args()

    if args.command == "capture-xp":
        capture_xp(args.season, gw=args.gw, target=args.target)
    elif args.command == "rebuild-latest":
        rebuild_latest_finished(args.season, gw=args.gw)


if __name__ == "__main__":
    main()
