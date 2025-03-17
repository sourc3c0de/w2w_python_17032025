from sqlalchemy.orm import Session
from app.models.contact import Contact
from typing import Optional

class ContactRepository:
    """ Repositorio para la entidad Contacto """
    
    @staticmethod
    def get_by_wa_id(db: Session, wa_id: str):
        """ Obtiene un contacto por su ID de WhatsApp """
        return db.query(Contact).filter(Contact.wa_id == wa_id).first()
    
    @staticmethod
    def create(db: Session, wa_id: str, phone_number: str, name: str):
        """ Crea un nuevo contacto"""
        contact = Contact(
            wa_id=wa_id,
            phone_number=phone_number,
            name=name
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact
    
    @staticmethod
    def get_or_create(
        db: Session, 
        wa_id: str, 
        phone: str, 
        name: str = "Unknown",
        business_id: Optional[int] = None
    ) -> Contact:
        """
        Obtiene un contacto existente o crea uno nuevo si no existe
        
        Args:
            db: Sesión de base de datos
            wa_id: ID de WhatsApp del contacto
            phone: Número de teléfono
            name: Nombre del contacto
            business_id: ID del negocio asociado (opcional)
            
        Returns:
            Contact: El contacto obtenido o creado
        """
        contact = ContactRepository.get_by_wa_id(db, wa_id)
        
        if contact:
            # Actualizar nombre si ha cambiado
            if contact.name != name and name != "Unknown":
                contact.name = name
                db.commit()
                db.refresh(contact)
            # Actualizar business_id si se proporciona y es diferente
            if business_id and contact.business_id != business_id:
                contact.business_id = business_id
                db.commit()
                db.refresh(contact)
            return contact
        
        # Crear nuevo contacto
        new_contact = Contact(
            wa_id=wa_id,
            phone=phone,
            name=name,
            business_id=business_id
        )
        
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        
        return new_contact