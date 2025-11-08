import logging
from botocore.exceptions import ClientError
from common import db, _format_response, logger

def handler(event, context):
    try:
        products = db.get_all_products()
        body = [p.model_dump() for p in products]
        
        return _format_response(body, 200)

    except ClientError as e:
        logger.error(f"Error de DynamoDB: {e}")
        return _format_response({'error': 'DynamoDB error', 'details': e.response['Error']['Message']}, 500)
    except Exception as e:
        logger.error(f"Error inesperado del servidor: {e}")
        return _format_response({'error': 'Server error', 'details': str(e)}, 500)
