import pandas as pd

def clean(df: pd.DataFrame) -> pd.DataFrame:
    out = df.dropna(subset=["customer_id", "campaign_id"]).copy()
    return out.drop_duplicates(["customer_id", "campaign_id"])

def test_required_keys_and_deduplication():
    source = pd.DataFrame([
        {"customer_id": "C1", "campaign_id": "A"},
        {"customer_id": "C1", "campaign_id": "A"},
        {"customer_id": "C2", "campaign_id": "B"},
        {"customer_id": None, "campaign_id": "C"},
    ])
    result = clean(source)
    assert len(result) == 2
    assert result["customer_id"].notna().all()
    assert not result.duplicated(["customer_id", "campaign_id"]).any()
