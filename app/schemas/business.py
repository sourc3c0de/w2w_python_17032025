from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class BusinessBase(BaseModel):
    """Esquema base para negocios"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    business_type: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None  # Cambiado de HttpUrl a str
    logo_url: Optional[str] = None  # Cambiado de HttpUrl a str
    system_prompt: Optional[str] = None

class BusinessCreate(BusinessBase):
    """Esquema para crear un nuevo negocio"""
    pass

class BusinessUpdate(BusinessBase):
    """Esquema para actualizar un negocio existente"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None

class BusinessInDB(BusinessBase):
    """Esquema para representar un negocio en la base de datos"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True  # Corregido para Pydantic V2