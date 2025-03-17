from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from dotenv import load_dotenv

# Añadir el directorio principal al path para poder importar app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Cargar variables de entorno
load_dotenv()

# this is the Alembic Config object
config = context.config

# Sobrescribir la URL con la de las variables de entorno
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Interpretar el archivo de configuración para Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Importar los modelos para que Alembic los detecte
from app.models.contact import Contact
from app.models.message import Message
from app.database.db import Base

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()