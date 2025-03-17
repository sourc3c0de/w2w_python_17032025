from sqlalchemy.orm import Session as DBSession
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from app.models.conversation_session import ConversationSession
import logging

logger = logging.getLogger(__name__)

class SessionRepository:
    """Repositorio para operaciones con sesiones de conversación"""
    
    @staticmethod
    def create(
        db: DBSession, 
        contact_id: int, 
        context: Optional[str] = None
    ) -> ConversationSession:
        """Crea una nueva sesión de conversación"""
        session = ConversationSession(
            contact_id=contact_id,
            started_at=datetime.now(timezone.utc),
            last_activity=datetime.now(timezone.utc),
            is_active=True,
            status="in_progress",
            context=context
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info(f"Creada nueva sesión {session.id} para el contacto {contact_id}")
        return session
    
    @staticmethod
    def get_active_session(db: DBSession, contact_id: int) -> Optional[ConversationSession]:
        """Obtiene la sesión activa del contacto, si existe"""
        session = db.query(ConversationSession)\
            .filter(ConversationSession.contact_id == contact_id)\
            .filter(ConversationSession.is_active == True)\
            .order_by(ConversationSession.last_activity.desc())\
            .first()
        return session
    
    @staticmethod
    def update_last_activity(db: DBSession, session_id: int) -> ConversationSession:
        """Actualiza el timestamp de última actividad"""
        session = db.query(ConversationSession).filter(ConversationSession.id == session_id).first()
        if session:
            session.last_activity = datetime.now(timezone.utc)
            db.commit()
            db.refresh(session)
        return session
    
    @staticmethod
    def close_session(
        db: DBSession, 
        session_id: int, 
        status: str = "completed", 
        context: Optional[str] = None
    ) -> ConversationSession:
        """Cierra una sesión existente"""
        session = db.query(ConversationSession).filter(ConversationSession.id == session_id).first()
        if session:
            session.is_active = False
            session.ended_at = datetime.now(timezone.utc)
            session.status = status
            if context:
                session.context = context
            db.commit()
            db.refresh(session)
            logger.info(f"Sesión {session_id} cerrada con estado: {status}")
        return session
    
    @staticmethod
    def get_or_create_active_session(
        db: DBSession, 
        contact_id: int,
        business_id: Optional[int] = None
    ) -> ConversationSession:
        """
        Obtiene la sesión activa o crea una nueva si no existe
        
        Args:
            db: Sesión de base de datos
            contact_id: ID del contacto
            business_id: ID del negocio (opcional)
            
        Returns:
            ConversationSession: Sesión activa
        """
        active_session = SessionRepository.get_active_session(db, contact_id)
        if not active_session:
            active_session = ConversationSession(
                contact_id=contact_id,
                business_id=business_id,
                started_at=datetime.now(timezone.utc),
                last_activity=datetime.now(timezone.utc),
                is_active=True,
                status="in_progress"
            )
            db.add(active_session)
            db.commit()
            db.refresh(active_session)
            logger.info(f"Creada nueva sesión {active_session.id} para el contacto {contact_id}")
        return active_session
    
    @staticmethod
    def close_inactive_sessions(db: DBSession, timeout_minutes: int = 30) -> int:
        """
        Cierra sesiones inactivas después de cierto tiempo
        
        Args:
            db: Sesión de base de datos
            timeout_minutes: Minutos de inactividad para considerar una sesión expirada
            
        Returns:
            int: Número de sesiones cerradas
        """
        timeout_threshold = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
        
        # Buscar sesiones activas con última actividad anterior al umbral
        sessions_to_close = db.query(ConversationSession)\
            .filter(ConversationSession.is_active == True)\
            .filter(ConversationSession.last_activity < timeout_threshold)\
            .all()
        
        closed_count = 0
        for session in sessions_to_close:
            session.is_active = False
            session.ended_at = datetime.now(timezone.utc)
            session.status = "timed_out"
            closed_count += 1
        
        if closed_count > 0:
            db.commit()
            logger.info(f"Cerradas {closed_count} sesiones inactivas")
        
        return closed_count
    
    @staticmethod
    def get_session_messages(db: DBSession, session_id: int) -> List:
        """Obtiene todos los mensajes de una sesión específica"""
        session = db.query(ConversationSession).filter(ConversationSession.id == session_id).first()
        if session:
            return session.messages
        return []