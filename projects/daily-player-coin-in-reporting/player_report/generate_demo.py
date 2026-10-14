"""Create deterministic, fully synthetic session data. Never uses employer data."""
import argparse
import csv
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from .pipeline import FIELDS


def generate(path, day="2026-10-08", seed=42):
    rng = random.Random(seed)
    start = datetime.combine(date.fromisoformat(day), datetime.min.time(), ZoneInfo("America/Los_Angeles"))
    rows = []
    for player in range(1, 41):
        for visit in range(rng.randint(1, 4)):
            dt = start + timedelta(hours=rng.randint(0, 23), minutes=rng.randint(0, 59))
            rows.append([f"DEMO-S{len(rows)+1:04}", f"DEMO-P{player:04}",
                         rng.choice(["Demo North", "Demo South", "Demo West"]),
                         dt.astimezone(timezone.utc).isoformat(), f"{rng.randint(5000, 750000)/100:.2f}"])
    # Deliberate boundary cases: one exclusion, one inclusion, duplicate, invalid, adjacent date.
    rows += [["DEMO-BOUNDARY", "DEMO-P1000", "Demo North", start.isoformat(), "10000.00"],
             ["DEMO-OVER", "DEMO-P1001", "Demo South", start.isoformat(), "10000.01"],
             rows[0].copy(),
             ["DEMO-BAD", "DEMO-P1002", "Demo North", start.isoformat(), "-25.00"],
             ["DEMO-PREVIOUS", "DEMO-P1003", "Demo North", (start-timedelta(minutes=1)).isoformat(), "25000.00"]]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(FIELDS)
        writer.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="data/demo_sessions.csv")
    parser.add_argument("--date", default="2026-10-08")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    print(f"Created {generate(args.output, args.date, args.seed)} synthetic rows: {args.output}")
