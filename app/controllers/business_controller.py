from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.repositories.business_repository import BusinessRepository
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessInDB
import logging

logger = logging.getLogger(__name__)

class BusinessController:
    """Controlador para la lógica de negocios"""
    
    @staticmethod
    def create_business(db: Session, business_data: BusinessCreate) -> BusinessInDB:
        """Crea un nuevo negocio"""
        business = BusinessRepository.create(db, business_data.dict(exclude_unset=True))
        return BusinessInDB.model_validate(business)
    
    @staticmethod
    def get_business(db: Session, business_id: int) -> Optional[BusinessInDB]:
        """Obtiene un negocio por su ID"""
        business = BusinessRepository.get_by_id(db, business_id)
        if business:
            return BusinessInDB.model_validate(business)
        return None
    
    @staticmethod
    def get_businesses(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[BusinessInDB]:
        """Obtiene todos los negocios"""
        businesses = BusinessRepository.get_all(db, skip, limit, active_only)
        return [BusinessInDB.model_validate(business) for business in businesses]
    
    @staticmethod
    def update_business(db: Session, business_id: int, business_data: BusinessUpdate) -> Optional[BusinessInDB]:
        """Actualiza un negocio existente"""
        business = BusinessRepository.update(db, business_id, business_data.dict(exclude_unset=True))
        if business:
            return BusinessInDB.model_validate(business)
        return None
    
    @staticmethod
    def delete_business(db: Session, business_id: int, hard_delete: bool = False) -> bool:
        """Elimina un negocio"""
        return BusinessRepository.delete(db, business_id, hard_delete)
    
    @staticmethod
    def search_businesses(db: Session, name_query: str) -> List[BusinessInDB]:
        """Busca negocios por nombre"""
        businesses = BusinessRepository.search_by_name(db, name_query)
        return [BusinessInDB.model_validate(business) for business in businesses]