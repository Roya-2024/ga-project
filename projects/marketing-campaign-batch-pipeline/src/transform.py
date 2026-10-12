from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = {
    "customer_id",
    "campaign_id",
    "event_date",
    "channel",
    "spend",
    "conversion_value",
}


def transform_campaign_events(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate and standardize synthetic campaign event data."""
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    out = frame.copy()
    out["customer_id"] = out["customer_id"].astype(str).str.strip()
    out["campaign_id"] = out["campaign_id"].astype(str).str.strip()
    out["channel"] = out["channel"].astype(str).str.strip().str.lower()
    out["event_date"] = pd.to_datetime(out["event_date"], errors="coerce")
    out["spend"] = pd.to_numeric(out["spend"], errors="coerce").fillna(0.0)
    out["conversion_value"] = pd.to_numeric(
        out["conversion_value"], errors="coerce"
    ).fillna(0.0)

    out = out.dropna(subset=["event_date"])
    out = out[out["customer_id"].ne("") & out["campaign_id"].ne("")]
    out = out.drop_duplicates(
        subset=["customer_id", "campaign_id", "event_date", "channel"]
    )

    out["net_value"] = out["conversion_value"] - out["spend"]
    return out.reset_index(drop=True)
