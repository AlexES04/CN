import psycopg2
import psycopg2.extras
import json
from typing import List, Optional
from .db import Database
from models.ticket import Ticket
import os

class PostgresDatabase(Database):
    
    def __init__(self):
        self.connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME')
        )
        self.connection.autocommit = True
        self.initialize()
    
    def initialize(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id         VARCHAR(36) PRIMARY KEY,
                    title             VARCHAR(255) NOT NULL,
                    description       TEXT,
                    status            VARCHAR(20) DEFAULT 'to do' CHECK (status IN ('to do', 'doing', 'done', 'blocked')),
                    priority          VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critic')),
                    position          INTEGER DEFAULT 0,
                    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    due_date          DATE,
                    tags              JSONB
                );
            """)
    
    def create_ticket(self, ticket: Ticket) -> Ticket:
        with self.connection.cursor() as cursor:
            sql = """
                INSERT INTO tickets 
                (ticket_id, title, description, status, priority, position, 
                 created_at, updated_at, due_date, tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                ticket.ticket_id, ticket.title, ticket.description, 
                ticket.status, ticket.priority, ticket.position,
                ticket.created_at, ticket.updated_at, ticket.due_date,
                json.dumps(ticket.tags)
            ))
        return ticket
    
    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            sql = "SELECT * FROM tickets WHERE ticket_id = %s"
            cursor.execute(sql, (ticket_id,))
            result = cursor.fetchone()
            if result:
                result = dict(result)
                result['tags'] = result['tags'] or []
                result['created_at'] = result['created_at'].isoformat() if result['created_at'] else None
                result['updated_at'] = result['updated_at'].isoformat() if result['updated_at'] else None
                result['due_date'] = result['due_date'].isoformat() if result['due_date'] else None
                return Ticket(**result)
        return None
    
    def get_all_tickets(self) -> List[Ticket]:
        with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            sql = "SELECT * FROM tickets ORDER BY position"
            cursor.execute(sql)
            results = cursor.fetchall()
            tickets = []
            for row in results:
                row = dict(row)
                row['tags'] = row['tags'] or []
                row['created_at'] = row['created_at'].isoformat() if row['created_at'] else None
                row['updated_at'] = row['updated_at'].isoformat() if row['updated_at'] else None
                row['due_date'] = row['due_date'].isoformat() if row['due_date'] else None
                tickets.append(Ticket(**row))
            return tickets
    
    def update_ticket(self, ticket_id: str, ticket: Ticket) -> Optional[Ticket]:
        ticket.update_timestamp()
        with self.connection.cursor() as cursor:
            sql = """
                UPDATE tickets 
                SET title=%s, description=%s, status=%s, priority=%s, 
                    position=%s, updated_at=%s, due_date=%s, tags=%s
                WHERE ticket_id=%s
            """
            cursor.execute(sql, (
                ticket.title, ticket.description, ticket.status, 
                ticket.priority, ticket.position, ticket.updated_at,
                ticket.due_date, json.dumps(ticket.tags), ticket_id
            ))
            if cursor.rowcount > 0:
                return self.get_ticket(ticket_id)
        return None
    
    def delete_ticket(self, ticket_id: str) -> bool:
        with self.connection.cursor() as cursor:
            sql = "DELETE FROM tickets WHERE ticket_id = %s"
            cursor.execute(sql, (ticket_id,))
            return cursor.rowcount > 0