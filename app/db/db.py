from abc import ABC, abstractmethod
from typing import List, Optional
from models.ticket import Ticket

class Database(ABC):
    
    @abstractmethod
    def initialize(self):
        pass
    
    @abstractmethod
    def create_ticket(self, ticket: Ticket) -> Ticket:
        pass
    
    @abstractmethod
    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        pass
    
    @abstractmethod
    def get_all_tickets(self) -> List[Ticket]:
        pass
    
    @abstractmethod
    def update_ticket(self, ticket_id: str, ticket: Ticket) -> Optional[Ticket]:
        pass
    
    @abstractmethod
    def delete_ticket(self, ticket_id: str) -> bool:
        pass