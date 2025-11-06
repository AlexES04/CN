import boto3
from botocore.exceptions import ClientError
from typing import List, Optional
from .db import Database
from models.product import Product
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
                print(f"Creando tabla DynamoDB '{self.table_name}'...")
                table = self.dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {
                            'AttributeName': 'product_id',
                            'KeyType': 'HASH'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'product_id',
                            'AttributeType': 'S'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                
                table.wait_until_exists()
                
                self.table = table
            else:
                raise
    
    def create_product(self, product: Product) -> Product:
        self.table.put_item(Item=product.model_dump())
        return product
    
    def get_product(self, product_id: str) -> Optional[Product]:
        response = self.table.get_item(Key={'product_id': product_id})
        if 'Item' in response:
            return Product(**response['Item'])
        return None
    
    def get_all_products(self) -> List[Product]:
        response = self.table.scan()
        products = [Product(**item) for item in response.get('Items', [])]
        return products
    
    def update_product(self, product_id: str, product: Product) -> Optional[Product]:
        product.update_timestamp()
        product.product_id = product_id
        self.table.put_item(Item=product.model_dump())
        return product
    
    def delete_product(self, product_id: str) -> bool:
        response = self.table.delete_item(
            Key={'product_id': product_id},
            ReturnValues='ALL_OLD'
        )
        return 'Attributes' in response