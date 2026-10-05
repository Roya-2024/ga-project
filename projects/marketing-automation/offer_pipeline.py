"""Sanitized portfolio example based on a real marketing-operations workflow."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

INPUT_FILE = Path("sample_winners.csv")
OUTPUT_FILE = Path("offer_upload.csv")

REQUIRED_COLUMNS = {"Location", "Patron ID", "Patron Name", "Prize Rank"}
OFFER_MAP = {
    1: {"free_play": 100, "offer_id": "DEMO-OFFER-100"},
    2: {"free_play": 50, "offer_id": "DEMO-OFFER-050"},
    3: {"free_play": 25, "offer_id": "DEMO-OFFER-025"},
}


def load_and_validate(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.replace("\ufeff", "", regex=False).str.strip()

    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    return df


def clean_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = []
    for location, block in df.groupby("Location", dropna=False):
        block = block.drop_duplicates(subset=["Patron ID"])
        block = block.drop_duplicates(subset=["Patron Name"])
        cleaned.append(block)
    return pd.concat(cleaned, ignore_index=True)


def build_offer_upload(df: pd.DataFrame) -> pd.DataFrame:
    today = datetime.now()
    activation = today.replace(hour=0, minute=0, second=0, microsecond=0)
    expiration = (today + timedelta(days=60)).replace(hour=23, minute=59, second=0, microsecond=0)

    rows = []
    for row in df.itertuples(index=False):
        config = OFFER_MAP.get(int(row._asdict()["Prize Rank"]))
        if not config:
            continue

        rows.append({
            "Patron ID": row._asdict()["Patron ID"],
            "Offer ID": config["offer_id"],
            "Activation Date": activation.strftime("%m/%d/%Y %H:%M"),
            "Offer Expiration": expiration.strftime("%m/%d/%Y %H:%M"),
            "Free Play": config["free_play"],
        })

    return pd.DataFrame(rows)


def main() -> None:
    source = load_and_validate(INPUT_FILE)
    source = clean_duplicates(source)
    upload = build_offer_upload(source)
    upload.to_csv(OUTPUT_FILE, index=False)
    print(f"Created {len(upload):,} upload rows -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
