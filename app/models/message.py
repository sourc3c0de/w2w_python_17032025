from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.db import Base

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    wa_message_id = Column(String(100), unique=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    direction = Column(String(10))  # "incoming" o "outgoing"
    message_type = Column(String(20))  # "tegxt", "imae", "audio", etc.
    content = Column(Text)
    timestamp = Column(DateTime)
    status = Column(String(20), default="received")  # received, sent, delivered, read, failed
    ai_processed = Column(Boolean, default=False)
    ai_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    # Relación con contacto
    contact = relationship("Contact", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, type={self.message_type}, direction={self.direction})>"