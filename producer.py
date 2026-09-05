import json 
import time
from confluent_kafka import Producer

KAFKA_BROKER = "localhost:9092"
TOPIC_NAME = "pubmed_topic"

def delivery_report(err, msg):
    if err is not None:
        print(f"Failed to deliver message: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def main():
    # creating a Kafka producer instance
    conf = {'bootstrap.servers': KAFKA_BROKER}
    producer = Producer(conf)

    count = 0
    print(f"Starting to send records to Kafka topic '{TOPIC_NAME}'...")

    with open("pubmed_data.json", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            record = json.loads(line)   
            payload = json.dumps(record).encode('utf-8')
            producer.produce(TOPIC_NAME, value=payload, callback=delivery_report)
            producer.poll(0)  # Trigger delivery report callbacks
            count += 1


    producer.flush()  # Wait for all messages to be delivered
    print(f"All {count} records have been successfully sent to Kafka!")

if __name__ == "__main__":
    main()
