from confluent_kafka import Consumer, KafkaException
import pandas as pd
import json
import os

# ===== Kafka Config =====
conf = {
    'bootstrap.servers': 'pkc-619z3.us-east1.gcp.confluent.cloud:9092',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': 'CWI6F64GWDVWBPJW',
    'sasl.password': 'RZE8DhS0Q+rei92kP9+WpJwS7hL/yb3g4QflgaFlBjNyMSa4l0UuQWrdYkSkeMLv',
    'group.id': 'nyc_traffic_consumer_group',
    'auto.offset.reset': 'earliest'
}

# Initialize Consumer
consumer = Consumer(conf)
consumer.subscribe(['nyc_traffic'])

traffic_data = []
print("📥 Kafka Consumer Connected — Listening for Traffic Routes...")

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())

        try:
            data = json.loads(msg.value().decode('utf-8'))

            # Flatten segment_ids
            if isinstance(data.get("segment_ids"), list):
                data["segment_ids"] = ",".join(map(str, data["segment_ids"]))

            traffic_data.append(data)

            if len(traffic_data) >= 5000:
                df = pd.DataFrame(traffic_data)

                # ✅ Replace the file instead of appending
                df.to_csv('nyc_traffic_data.csv', index=False)
                print("✅ Replaced nyc_traffic_data.csv with new 5000 routes")

                traffic_data = []

        except Exception as e:
            print(f"⚠️ Skipping invalid message: {e}")

except KeyboardInterrupt:
    print("🛑 Consumer stopped by user.")

finally:
    consumer.close()
