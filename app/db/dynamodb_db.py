import boto3
from botocore.exceptions import ClientError
from typing import List, Optional
from .db import Database
from models.ticket import Ticket
import os

class DynamoDBDatabase(Database):
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.table_name = os.getenv('DB_DYNAMONAME')
        self.table = self.dynamodb.Table(self.table_name)
        self.initialize()
    
    def initialize(self):
        try:
            self.table.load()
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # La tabla no existe, crearla
                print(f"Creando tabla DynamoDB '{self.table_name}'...")
                table = self.dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {
                            'AttributeName': 'ticket_id',
                            'KeyType': 'HASH'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'ticket_id',
                            'AttributeType': 'S'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                
                # Esperar a que la tabla esté activa
                table.wait_until_exists()
                
                # Actualizar referencia a la tabla
                self.table = table
            else:
                raise
    
    def create_ticket(self, ticket: Ticket) -> Ticket:
        self.table.put_item(Item=ticket.model_dump())
        return ticket
    
    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        response = self.table.get_item(Key={'ticket_id': ticket_id})
        if 'Item' in response:
            return Ticket(**response['Item'])
        return None
    
    def get_all_tickets(self) -> List[Ticket]:
        response = self.table.scan()
        tickets = [Ticket(**item) for item in response.get('Items', [])]
        return sorted(tickets, key=lambda x: x.position)
    
    def update_ticket(self, ticket_id: str, ticket: Ticket) -> Optional[Ticket]:
        ticket.update_timestamp()
        ticket.ticket_id = ticket_id
        self.table.put_item(Item=ticket.model_dump())
        return ticket
    
    def delete_ticket(self, ticket_id: str) -> bool:
        response = self.table.delete_item(
            Key={'ticket_id': ticket_id},
            ReturnValues='ALL_OLD'
        )
        return 'Attributes' in response