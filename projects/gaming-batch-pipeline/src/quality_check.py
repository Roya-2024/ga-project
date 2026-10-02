import csv
from pathlib import Path

p=Path(__file__).resolve().parents[1]/"data"/"gaming_events.csv"
required={"event_id","player_id","property_id","gaming_date","coin_in","theo_win","net_win","free_play","minutes_played"}
with p.open(encoding="utf-8") as f:
    r=csv.DictReader(f)
    assert required.issubset(set(r.fieldnames or [])), "Missing required columns"
    rows=list(r)
assert rows, "Dataset is empty"
assert len({x["event_id"] for x in rows})==len(rows), "Duplicate event_id"
assert all(float(x["coin_in"])>=0 and float(x["free_play"])>=0 for x in rows), "Invalid monetary value"
print(f"Quality checks passed: {len(rows):,} rows")
