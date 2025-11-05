from flask import Flask, request, jsonify
from pydantic import ValidationError
import psycopg2
from botocore.exceptions import ClientError
from models.ticket import Ticket
from db.dynamodb_db import DynamoDBDatabase

app = Flask(__name__)

try:
    db = DynamoDBDatabase()
except ValueError as e:
    raise RuntimeError(f"Error initializing DB: {e}") from e

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,x-api-key'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

@app.route('/items', methods=['POST'])
def create_item():
    try:
        data = request.get_json()
        ticket = Ticket(**data)
        created = db.create_ticket(ticket)
        return jsonify(created.model_dump()), 201
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 400
    except psycopg2.IntegrityError as e:
        return jsonify({'error': 'Database integrity error', 'details': str(e)}), 409
    except psycopg2.OperationalError as e:
        return jsonify({'error': 'Database connection error', 'details': str(e)}), 503
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except ClientError as e:
        return jsonify({'error': 'DynamoDB error', 'details': e.response['Error']['Message']}), 500

@app.route('/items/<ticket_id>', methods=['GET'])
def get_item(ticket_id):
    try:
        ticket = db.get_ticket(ticket_id)
        if ticket:
            return jsonify(ticket.model_dump()), 200
        return jsonify({'error': 'Item no encontrado'}), 404
    except psycopg2.OperationalError as e:
        return jsonify({'error': 'Database connection error', 'details': str(e)}), 503
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except ClientError as e:
        return jsonify({'error': 'DynamoDB error', 'details': e.response['Error']['Message']}), 500

@app.route('/items', methods=['GET'])
def get_all_items():
    try:
        tickets = db.get_all_tickets()
        return jsonify([t.model_dump() for t in tickets]), 200
    except psycopg2.OperationalError as e:
        return jsonify({'error': 'Database connection error', 'details': str(e)}), 503
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except ClientError as e:
        return jsonify({'error': 'DynamoDB error', 'details': e.response['Error']['Message']}), 500

@app.route('/items/<ticket_id>', methods=['PUT'])
def update_item(ticket_id):
    try:
        data = request.get_json()
        data.pop('ticket_id', None)
        data.pop('created_at', None)
        ticket = Ticket(**data)
        updated = db.update_ticket(ticket_id, ticket)
        if updated:
            return jsonify(updated.model_dump()), 200
        return jsonify({'error': 'Item no encontrado'}), 404
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 400
    except psycopg2.IntegrityError as e:
        return jsonify({'error': 'Database integrity error', 'details': str(e)}), 409
    except psycopg2.OperationalError as e:
        return jsonify({'error': 'Database connection error', 'details': str(e)}), 503
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except ClientError as e:
        return jsonify({'error': 'DynamoDB error', 'details': e.response['Error']['Message']}), 500

@app.route('/items/<ticket_id>', methods=['DELETE'])
def delete_item(ticket_id):
    try:
        if db.delete_ticket(ticket_id):
            return '', 204
        return jsonify({'error': 'Item no encontrado'}), 404
    except psycopg2.OperationalError as e:
        return jsonify({'error': 'Database connection error', 'details': str(e)}), 503
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except ClientError as e:
        return jsonify({'error': 'DynamoDB error', 'details': e.response['Error']['Message']}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)