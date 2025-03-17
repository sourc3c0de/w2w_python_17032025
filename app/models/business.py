from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.db import Base

class Business(Base):
    """Modelo para representar negocios (restaurantes, tiendas, etc.)"""
    __tablename__ = "businesses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    business_type = Column(String(50), nullable=True)  # restaurant, store, service, etc.
    address = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    website = Column(String(100), nullable=True)
    logo_url = Column(String(255), nullable=True)
    
    # Configuración del bot
    system_prompt = Column(Text, nullable=True)  # Prompt personalizado para este negocio
    
    # Metadatos
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    contacts = relationship("Contact", back_populates="business")
    sessions = relationship("ConversationSession", back_populates="business")
    
    def __repr__(self):
        return f"<Business(id={self.id}, name='{self.name}')>"