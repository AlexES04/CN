from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
import uuid

class Product(BaseModel):

    product_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    name: str = Field(..., min_length=1, max_length=255)

    sku: Optional[str] = None
    
    quantity: int = Field(..., ge=0)
    
    category: Literal[
        'Lácteos', 
        'Snacks', 
        'Bebidas', 
        'Frutas y Verduras', 
        'Carnicería', 
        'Limpieza', 
        'Otros'
    ] = Field(...)
    
    status: Literal['to do', 'done'] = 'to do'
    position: Optional[int] = 0
    
    tags: List[str] = Field(default_factory=list)
    
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Yogur Griego Fresa",
                "sku": "YG-FRS-150G",
                "quantity": 120,
                "category": "Lácteos",
                "status": "to do",
                "position": 0,
                "tags": ["frio", "desayuno"]
            }
        }
    
    def update_timestamp(self):
        """Actualiza el campo updated_at a la hora UTC actual."""
        self.updated_at = datetime.utcnow().isoformat()
        