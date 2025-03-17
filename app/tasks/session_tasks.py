import logging
from fastapi import Depends
from sqlalchemy.orm import Session
from app.repositories.session_repository import SessionRepository
from app.database.db import get_db
import asyncio

logger = logging.getLogger(__name__)

async def close_inactive_sessions(db: Session):
    """Cierra sesiones que han estado inactivas por más de 30 minutos"""
    try:
        closed_count = SessionRepository.close_inactive_sessions(db, timeout_minutes=30)
        if closed_count > 0:
            logger.info(f"Tarea programada: Cerradas {closed_count} sesiones inactivas")
    except Exception as e:
        logger.error(f"Error en tarea de cierre de sesiones: {str(e)}", exc_info=True)

async def start_session_cleanup_task():
    """Inicia la tarea programada para limpiar sesiones inactivas"""
    while True:
        # Crear una nueva sesión de base de datos para la tarea
        db = next(get_db())
        try:
            await close_inactive_sessions(db)
        finally:
            db.close()
        
        # Esperar 10 minutos antes de la próxima ejecución
        await asyncio.sleep(10 * 60)