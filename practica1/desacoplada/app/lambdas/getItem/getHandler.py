import logging
from botocore.exceptions import ClientError
from common import db, _format_response, logger

def handler(event, context):
    try:
        product_id = event['pathParameters']['id']
        
        product = db.get_product(product_id)
        
        if product:
            return _format_response(product.model_dump(), 200)
        else:
            return _format_response({'error': 'Item no encontrado'}, 404)

    except KeyError:
        logger.warning("Solicitud GET /item sin 'id' en pathParameters")
        return _format_response({'error': "Falta 'id' en la ruta"}, 400)
    except ClientError as e:
        logger.error(f"Error de DynamoDB: {e}")
        return _format_response({'error': 'DynamoDB error', 'details': e.response['Error']['Message']}, 500)
    except Exception as e:
        logger.error(f"Error inesperado del servidor: {e}")
        return _format_response({'error': 'Server error', 'details': str(e)}, 500)
    