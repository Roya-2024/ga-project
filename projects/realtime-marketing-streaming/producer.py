"""Generate synthetic marketing events and publish them to Kafka."""
import json
import random
import time
from datetime import datetime, timezone
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

campaigns = ["DEMO-CAMPAIGN-A", "DEMO-CAMPAIGN-B", "DEMO-CAMPAIGN-C"]
events = ["impression", "click", "signup", "conversion"]

while True:
    payload = {
        "event_id": f"evt-{random.randint(100000, 999999)}",
        "customer_id": f"cust-{random.randint(1000, 9999)}",
        "campaign_id": random.choice(campaigns),
        "event_type": random.choice(events),
        "event_ts": datetime.now(timezone.utc).isoformat(),
        "value": round(random.random() * 100, 2),
    }
    producer.send("demo_marketing_events", payload)
    producer.flush()
    time.sleep(1)
