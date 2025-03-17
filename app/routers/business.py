from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.db import get_db
from app.controllers.business_controller import BusinessController
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessInDB

router = APIRouter(
    prefix="/businesses",
    tags=["businesses"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=BusinessInDB, status_code=status.HTTP_201_CREATED)
def create_business(
    business: BusinessCreate, 
    db: Session = Depends(get_db)
):
    """Crea un nuevo negocio"""
    return BusinessController.create_business(db, business)

@router.get("/{business_id}", response_model=BusinessInDB)
def get_business(
    business_id: int, 
    db: Session = Depends(get_db)
):
    """Obtiene un negocio específico por su ID"""
    business = BusinessController.get_business(db, business_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return business

@router.get("/", response_model=List[BusinessInDB])
def get_businesses(
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Obtiene una lista de negocios"""
    return BusinessController.get_businesses(db, skip, limit, active_only)

@router.put("/{business_id}", response_model=BusinessInDB)
def update_business(
    business_id: int, 
    business: BusinessUpdate, 
    db: Session = Depends(get_db)
):
    """Actualiza un negocio existente"""
    updated_business = BusinessController.update_business(db, business_id, business)
    if updated_business is None:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return updated_business

@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_business(
    business_id: int, 
    hard_delete: bool = False,
    db: Session = Depends(get_db)
):
    """Elimina un negocio"""
    success = BusinessController.delete_business(db, business_id, hard_delete)
    if not success:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return {"message": "Negocio eliminado correctamente"}

@router.get("/search/", response_model=List[BusinessInDB])
def search_businesses(
    query: str = Query(..., min_length=1, description="Término de búsqueda"),
    db: Session = Depends(get_db)
):
    """Busca negocios por nombre"""
    return BusinessController.search_businesses(db, query)