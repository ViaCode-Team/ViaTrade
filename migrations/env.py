from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from infrastructure.config.app import AppConfig
from domain.entity.base import BaseModel
from domain.entity import User, TradeType, TradeCode, Trade, UserTradeCode, TradeStrategy, UserTradeStrategy

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

app_config = AppConfig()
db_url = app_config.db.build_url()
config.set_main_option("sqlalchemy.url", str(db_url))

target_metadata = BaseModel.metadata

def run_migrations_offline():
    context.configure(
        url=str(db_url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
