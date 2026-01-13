import json
import base64
import datetime

def lambda_handler(event, context):
    # CÓDIGO DE LAMBDA
    output = []
    for record in event['records']:
        payload = base64.b64decode(record['data']).decode('utf-8')
        data_json = json.loads(payload)
        
        volume = int(data_json.get('volume', 0))
        
        range_start = (volume // 10) * 10
        range_end = range_start + 9

        partition_value = f"{range_start:02d}-{range_end:02d}"
        processed_data = json.dumps(data_json) + '\n'
        
        output_record = {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': base64.b64encode(processed_data.encode('utf-8')).decode('utf-8'),
            'metadata': {
                'partitionKeys': {
                    'volume_range': partition_value
                }
            }
        }
        output.append(output_record)
    
    return {'records': output}