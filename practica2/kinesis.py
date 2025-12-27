import boto3
from loguru import logger
import time
import json
import csv

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
        payload = {
            'Chapter': int(row.get('Chapter_Number', 0)),
            'Volume': int(row.get('Volume', 0)),
            'Title': row.get('Name', 'N/A'),
            'Japanese_title': row.get('Romanized_title', 'N/A'),
            'Pages': int(row.get('Pages', 0)),
            'Release': row.get('Date', 'N/A')
        }

        response = kinesis.put_record(
            StreamName = STREAM_NAME,
            Data = json.dumps(payload),
            PartitionKey = str(payload['Volume'])
        )

        records_sent += 1
        logger.info(f"Sent record {records_sent}:\nEpisode {payload['Chapter']} of Volume {payload['Volume']} data with {response=}")
        time.sleep(0.01)

if __name__ == "__main__":
    run_producer()
