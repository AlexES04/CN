import json
import logging
from pydantic import ValidationError
from botocore.exceptions import ClientError
from models.product import Product
from common import db, _format_response, logger

def handler(event, context):
    try:
        product_id = event['pathParameters']['id']
        data = json.loads(event.get('body', '{}'))
        
        data.pop('product_id', None)
        data.pop('created_at', None)
        
        product = Product(**data)
        updated = db.update_product(product_id, product)
        
        if updated:
            return _format_response(updated.model_dump(), 200)
        else:
            return _format_response({'error': 'Item no encontrado'}, 404)
            
    except (ValidationError, json.JSONDecodeError) as e:
        logger.warning(f"Error de validación o JSON: {e}")
        details = e.errors() if isinstance(e, ValidationError) else str(e)
        return _format_response({'error': 'Validation/JSON error', 'details': details}, 400)
    except KeyError:
        logger.warning("Solicitud PUT /item sin 'id' en pathParameters")
        return _format_response({'error': "Falta 'id' en la ruta"}, 400)
    except ClientError as e:
        logger.error(f"Error de DynamoDB: {e}")
        return _format_response({'error': 'DynamoDB error', 'details': e.response['Error']['Message']}, 500)
    except Exception as e:
        logger.error(f"Error inesperado del servidor: {e}")
        return _format_response({'error': 'Server error', 'details': str(e)}, 500)