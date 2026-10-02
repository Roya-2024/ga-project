import json, random, time, uuid
from datetime import datetime, timezone
from kafka import KafkaProducer

producer=KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

while True:
    coin=round(random.uniform(5,500),2)
    event={
        "event_id":str(uuid.uuid4()),
        "event_time":datetime.now(timezone.utc).isoformat(),
        "player_id":random.randint(10000,19999),
        "property_id":random.randint(1,12),
        "coin_in":coin,
        "theo_win":round(coin*random.uniform(.04,.14),2),
        "free_play":random.choice([0,0,0,5,10,20]),
    }
    producer.send("gaming-events",event)
    producer.flush()
    time.sleep(.25)
