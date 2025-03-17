from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.db import Base

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    wa_id = Column(String(30), unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    name = Column(String(20), index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relación con el modelo de mensajes
    messages = relationship("Message", back_populates="contact")
    
    # Añadir esto a tu modelo Contact existente
    sessions = relationship("ConversationSession", back_populates="contact")
    
    def __repr__(self):
        return f"<Contact(id={self.id}, name={self.name}, phone_number={self.phone_number})>"
