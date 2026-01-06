import boto3
from loguru import logger
import time
import json
import csv
from datetime import datetime

STREAM_NAME = 'chapters-stream'
INPUT_FILE = 'datos.csv'

kinesis = boto3.client('kinesis')

def load_data(path: str):
    with open(path, 'r') as file:
        reader = csv.DictReader(file, delimiter=';')
        return list(reader)
    
def run_producer():
    data = load_data(INPUT_FILE)
    records_sent = 0

    logger.info(f"Initializing sending of {STREAM_NAME}. Reading {len(data)} registers.")

    for row in data:
        raw_date = row.get('Date', 'N/A')
        iso_date = datetime.strptime(raw_date, '%d/%m/%Y').strftime('%Y-%m-%d')

        payload = {
            'chapter': int(row.get('Chapter_Number', 0)),
            'volume': int(row.get('Volume', 0)),
            'title': row.get('Name', 'N/A'),
            'japanese_title': row.get('Romanized_title', 'N/A'),
            'pages': int(row.get('Pages', 0)),
            'release': iso_date,
            'rating': float(row.get('Rating', 0))
        }

        response = kinesis.put_record(
            StreamName = STREAM_NAME,
            Data = json.dumps(payload),
            PartitionKey = str(payload['volume'])
        )

        records_sent += 1
        logger.info(f"Sent record {records_sent}:\nEpisode {payload['chapter']} of Volume {payload['volume']} data with {response=}")
        time.sleep(0.01)

if __name__ == "__main__":
    run_producer()
