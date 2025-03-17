from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.business import Business
import logging

logger = logging.getLogger(__name__)

class BusinessRepository:
    """Repositorio para operaciones relacionadas con negocios"""
    
    @staticmethod
    def create(db: Session, business_data: Dict[str, Any]) -> Business:
        """
        Crea un nuevo negocio en la base de datos
        
        Args:
            db: Sesión de base de datos
            business_data: Diccionario con los datos del negocio
            
        Returns:
            Business: Objeto de negocio creado
        """
        business = Business(**business_data)
        db.add(business)
        db.commit()
        db.refresh(business)
        logger.info(f"Nuevo negocio creado: {business.name} (ID: {business.id})")
        return business
    
    @staticmethod
    def get_by_id(db: Session, business_id: int) -> Optional[Business]:
        """Obtiene un negocio por su ID"""
        return db.query(Business).filter(Business.id == business_id).first()
    
    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Business]:
        """Obtiene un negocio por su nombre (búsqueda exacta)"""
        return db.query(Business).filter(Business.name == name).first()
    
    @staticmethod
    def search_by_name(db: Session, name_query: str) -> List[Business]:
        """Busca negocios por nombre (búsqueda parcial)"""
        return db.query(Business).filter(Business.name.ilike(f"%{name_query}%")).all()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Business]:
        """Obtiene todos los negocios"""
        query = db.query(Business)
        if active_only:
            query = query.filter(Business.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, business_id: int, business_data: Dict[str, Any]) -> Optional[Business]:
        """
        Actualiza un negocio existente
        
        Args:
            db: Sesión de base de datos
            business_id: ID del negocio a actualizar
            business_data: Diccionario con los datos a actualizar
            
        Returns:
            Business: Objeto de negocio actualizado o None si no existe
        """
        business = BusinessRepository.get_by_id(db, business_id)
        if not business:
            return None
        
        for key, value in business_data.items():
            setattr(business, key, value)
        
        db.commit()
        db.refresh(business)
        logger.info(f"Negocio actualizado: {business.name} (ID: {business.id})")
        return business
    
    @staticmethod
    def delete(db: Session, business_id: int, hard_delete: bool = False) -> bool:
        """
        Elimina un negocio
        
        Args:
            db: Sesión de base de datos
            business_id: ID del negocio a eliminar
            hard_delete: Si es True, elimina el registro; si es False, marca como inactivo
            
        Returns:
            bool: True si se eliminó correctamente, False si no
        """
        business = BusinessRepository.get_by_id(db, business_id)
        if not business:
            return False
        
        if hard_delete:
            db.delete(business)
        else:
            business.is_active = False
        
        db.commit()
        logger.info(f"Negocio {'eliminado' if hard_delete else 'desactivado'}: {business.name} (ID: {business.id})")
        return True