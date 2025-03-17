from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.db import Base

class ConversationSession(Base):
    __tablename__ = "conversation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    started_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_activity = Column(DateTime, default=datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    status = Column(String(50), default="in_progress")  # in_progress, completed, timed_out, closed_by_user
    context = Column(String(500), nullable=True)  # información sobre el propósito de la sesión
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=True)
    
    # Relaciones
    contact = relationship("Contact", back_populates="sessions")
    messages = relationship("Message", back_populates="session")
    business = relationship("Business", back_populates="sessions")
    
    def __repr__(self):
        return f"<ConversationSession(id={self.id}, contact_id={self.contact_id}, active={self.is_active})>"