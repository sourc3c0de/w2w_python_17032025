from sqlalchemy.orm import Session
from app.models.contact import Contact

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
    def get_or_create(db: Session, wa_id: str, phone_number: str, name: str):
        """ Obtiene un contacto por su ID de WhatsApp o lo crea si no existe """
        contact = ContactRepository.get_by_wa_id(db, wa_id)
        if not contact:
            contact = ContactRepository.create(db, wa_id, phone_number or wa_id, name)
        return contact