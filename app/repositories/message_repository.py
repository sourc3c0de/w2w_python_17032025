from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.models.message import Message

class MessageRepository:
    """Repositorio para operaciones con mensajes en la base de datos"""
    
    @staticmethod
    def create(
        db: Session, 
        wa_message_id: str, 
        contact_id: int, 
        direction: str, 
        message_type: str,
        content: str,
        timestamp: datetime,
        status: str = "received",
        ai_processed: bool = False,
        ai_response: Optional[str] = None
    ):
        """Crea un nuevo mensaje en la base de datos"""
        message = Message(
            wa_message_id=wa_message_id,
            contact_id=contact_id,
            direction=direction,
            message_type=message_type,
            content=content,
            timestamp=timestamp,
            status=status,
            ai_processed=ai_processed,
            ai_response=ai_response
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def get_by_wa_id(db: Session, wa_message_id: str):
        """Obtiene un mensaje por su ID de WhatsApp"""
        return db.query(Message).filter(Message.wa_message_id == wa_message_id).first()
    
    @staticmethod
    def update_status(db: Session, wa_message_id: str, status: str):
        """Actualiza el estado de un mensaje"""
        message = MessageRepository.get_by_wa_id(db, wa_message_id)
        if message:
            message.status = status
            db.commit()
            db.refresh(message)
        return message
    
    @staticmethod
    def get_conversation_history(db: Session, contact_id: int, limit: int = 5) -> List[Message]:
        """Obtiene el historial de conversación para un contacto"""
        return (
            db.query(Message)
            .filter(Message.contact_id == contact_id)
            .order_by(Message.timestamp.desc())
            .limit(limit * 2)
            .all()
        )