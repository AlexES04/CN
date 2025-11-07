import logging
from botocore.exceptions import ClientError
from common import db, _format_response, logger # Importamos desde common

def handler(event, context):
    """
    Handler para GET /items
    (Corresponde a tu GetItemsLambda)
    """
    try:
        products = db.get_all_products()
        # Preparamos el cuerpo de la respuesta antes de pasarlo al helper
        body = [p.model_dump() for p in products]
        
        return _format_response(body, 200)

    except ClientError as e:
        logger.error(f"Error de DynamoDB: {e}")
        return _format_response({'error': 'DynamoDB error', 'details': e.response['Error']['Message']}, 500)
    except Exception as e:
        logger.error(f"Error inesperado del servidor: {e}")
        return _format_response({'error': 'Server error', 'details': str(e)}, 500)
