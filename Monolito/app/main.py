from flask import Flask, request, jsonify
from pydantic import ValidationError
from botocore.exceptions import ClientError
from models.product import Product
from db.dynamodb_db import DynamoDBDatabase

app = Flask(__name__)

try:
    db = DynamoDBDatabase()
except ValueError as e:
    raise RuntimeError(f"Error initializing DB: {e}") from e

@app.after_request
def add_cors_headers(response):
    """Añade cabeceras CORS a todas las respuestas."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,x-api-key'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

@app.route('/items', methods=['POST'])
def create_item():
    """Crea un nuevo producto."""
    try:
        data = request.get_json()
        product = Product(**data)
        created = db.create_product(product)
        return jsonify(created.model_dump()), 201
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 400
    except ClientError as e:
        return jsonify({'error': 'DynamoDB error', 'details': e.response['Error']['Message']}), 500
    except Exception as e:
        return jsonify({'error': 'Server error', 'details': str(e)}), 500

@app.route('/items/<product_id>', methods=['GET'])
def get_item(product_id):
    """Obtiene un producto por su ID."""
    try:
        product = db.get_product(product_id)
        if product:
            return jsonify(product.model_dump()), 200
        return jsonify({'error': 'Item no encontrado'}), 404
    except ClientError as e:
        return jsonify({'error': 'DynamoDB error', 'details': e.response['Error']['Message']}), 500
    except Exception as e:
        return jsonify({'error': 'Server error', 'details': str(e)}), 500

@app.route('/items', methods=['GET'])
def get_all_items():
    """Obtiene todos los productos."""
    try:
        products = db.get_all_products()
        return jsonify([p.model_dump() for p in products]), 200
    except ClientError as e:
        return jsonify({'error': 'DynamoDB error', 'details': e.response['Error']['Message']}), 500
    except Exception as e:
        return jsonify({'error': 'Server error', 'details': str(e)}), 500

@app.route('/items/<product_id>', methods=['PUT'])
def update_item(product_id):
    """Actualiza un producto."""
    try:
        data = request.get_json()
        data.pop('product_id', None)
        data.pop('created_at', None)
        
        product = Product(**data)
        updated = db.update_product(product_id, product)
        
        if updated:
            return jsonify(updated.model_dump()), 200
        return jsonify({'error': 'Item no encontrado'}), 404
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 400
    except ClientError as e:
        return jsonify({'error': 'DynamoDB error', 'details': e.response['Error']['Message']}), 500
    except Exception as e:
        return jsonify({'error': 'Server error', 'details': str(e)}), 500

@app.route('/items/<product_id>', methods=['DELETE'])
def delete_item(product_id):
    """Elimina un producto."""
    try:
        if db.delete_product(product_id):
            return '', 204
        return jsonify({'error': 'Item no encontrado'}), 404
    except ClientError as e:
        return jsonify({'error': 'DynamoDB error', 'details': e.response['Error']['Message']}), 500
    except Exception as e:
        return jsonify({'error': 'Server error', 'details': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint para el Load Balancer."""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)