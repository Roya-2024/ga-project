from __future__ import annotations
import csv, random
from datetime import date, timedelta
from pathlib import Path

OUT=Path(__file__).resolve().parents[1]/"data"/"gaming_events.csv"
OUT.parent.mkdir(parents=True,exist_ok=True)
random.seed(42)

def main(rows:int=50000):
    start=date(2026,1,1)
    with OUT.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["event_id","player_id","property_id","gaming_date","coin_in","theo_win","net_win","free_play","minutes_played"])
        w.writeheader()
        for i in range(1,rows+1):
            coin=round(random.uniform(10,2500),2)
            theo=round(coin*random.uniform(.04,.14),2)
            w.writerow({
                "event_id":i,"player_id":random.randint(10000,19999),
                "property_id":random.randint(1,12),
                "gaming_date":start+timedelta(days=random.randint(0,179)),
                "coin_in":coin,"theo_win":theo,
                "net_win":round(random.uniform(-300,500),2),
                "free_play":round(random.choice([0,0,0,5,10,20,50]),2),
                "minutes_played":random.randint(5,360)})
    print(f"Wrote {rows:,} synthetic rows to {OUT}")

if __name__=="__main__":
    main()
