import json
import logging
from db.dynamodb_db import DynamoDBDatabase


logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    db = DynamoDBDatabase()
    logger.info("Conexión a DynamoDB inicializada con éxito.")
except ValueError as e:
    logger.error(f"Error fatal inicializando la BBDD: {e}")
    raise RuntimeError(f"Error inicializando DB: {e}") from e

# --- Función de Ayuda para Respuestas ---

def _format_response(body, status_code=200):
    """
    Formatea la respuesta en el formato que AWS API Gateway Proxy espera.
    """

    response_body = ""
    if body is not None:
        response_body = json.dumps(body)

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,x-api-key",
            "Access-Control-Allow-Methods": "POST,GET,PUT,DELETE,OPTIONS"
        },
        "body": response_body
    }
