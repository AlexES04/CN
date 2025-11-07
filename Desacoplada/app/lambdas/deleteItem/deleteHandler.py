import logging
from botocore.exceptions import ClientError
from common import db, _format_response, logger # Importamos desde common

def handler(event, context):
    """
    Handler para DELETE /items/{id}
    (Corresponde a tu DeleteItemLambda)
    """
    try:
        product_id = event['pathParameters']['id']
        
        if db.delete_product(product_id):
            # 204 No Content. El body debe estar vacío.
            return _format_response(None, 204)
        else:
            return _format_response({'error': 'Item no encontrado'}, 404)

    except KeyError:
        logger.warning("Solicitud DELETE /item sin 'id' en pathParameters")
        return _format_response({'error': "Falta 'id' en la ruta"}, 400)
    except ClientError as e:
        logger.error(f"Error de DynamoDB: {e}")
        return _format_response({'error': 'DynamoDB error', 'details': e.response['Error']['Message']}, 500)
    except Exception as e:
        logger.error(f"Error inesperado del servidor: {e}")
        return _format_response({'error': 'Server error', 'details': str(e)}, 500)
