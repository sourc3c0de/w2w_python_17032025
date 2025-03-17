from app.database.db import Base, engine

def create_tables():
    """Crea todas las tablas en la base de datos"""
    Base.metadata.create_all(bind=engine)