"""Alembic environment configuration for raw SQL migrations."""

import os
from logging.config import fileConfig
from urllib.parse import quote_plus

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get database URL — explicit DATABASE_URL takes precedence, otherwise construct from components
database_url = os.environ.get("DATABASE_URL", "")
if not database_url:
    db_user = os.environ.get("DB_USER", "")
    db_password = os.environ.get("DB_PASSWORD", "")
    db_name = os.environ.get("DB_NAME", "")
    cloud_sql_instance = os.environ.get("CLOUD_SQL_INSTANCE", "")
    if db_user and db_password and db_name and cloud_sql_instance:
        # SQLAlchemy uses postgresql:// with host parameter for Unix socket
        password = quote_plus(db_password)
        database_url = f"postgresql+psycopg2://{db_user}:{password}@/{db_name}?host=/cloudsql/{cloud_sql_instance}"
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=None,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    from sqlalchemy import create_engine

    url = config.get_main_option("sqlalchemy.url")
    connectable = create_engine(url)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=None)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
