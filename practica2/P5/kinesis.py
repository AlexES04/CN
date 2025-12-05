import boto3
from loguru import logger
import time
import json

STREAM_NAME = 'energy-stream'
INPUT_FILE = 'datos.json'

kinesis = boto3.client('kinesis')

def load_data(path: str):
    with open(path, 'r') as file:
        return json.load(file)
    
def run_producer():
    data = load_data(INPUT_FILE)
    records_sent = 0

    series_list = data.get('included', [])
    logger.info(f"Iniciando transmisión de {STREAM_NAME}")

    for serie in series_list:
        tipo_demanda = serie['attributes']['title']
        valores = serie['attributes']['values']

        for registro in valores:
            payload = {
                'tipo_demanda': tipo_demanda,
                'valor': registro['value'],
                'timestamp_origen': registro['datetime'],
                'portentaje': registro['percentage'],
            }

            response = kinesis.put_record(
                StreamName = STREAM_NAME,
                Data = json.dumps(payload),
                PartitionKey = tipo_demanda
            )

            records_sent += 1
            logger.info(f"Sent record {records_sent} data with {response=}")
            time.sleep(0.01)

if __name__ == "__main__":
    run_producer()
