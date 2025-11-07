import json
import logging
from pydantic import ValidationError
from botocore.exceptions import ClientError
from models.product import Product
from common import db, _format_response, logger

def handler(event, context):
    """
    Handler para POST /items
    (Corresponde a tu PostItemLambda)
    """
    try:
        data = json.loads(event.get('body', '{}'))
        
        product = Product(**data)
        created = db.create_product(product)
        
        return _format_response(created.model_dump(), 201)

    except (ValidationError, json.JSONDecodeError) as e:
        logger.warning(f"Error de validación o JSON: {e}")
        details = e.errors() if isinstance(e, ValidationError) else str(e)
        return _format_response({'error': 'Validation/JSON error', 'details': details}, 400)
    except ClientError as e:
        logger.error(f"Error de DynamoDB: {e}")
        return _format_response({'error': 'DynamoDB error', 'details': e.response['Error']['Message']}, 500)
    except Exception as e:
        logger.error(f"Error inesperado del servidor: {e}")
        return _format_response({'error': 'Server error', 'details': str(e)}, 500)
