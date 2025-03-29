from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
import asyncio
from users.models import Users, UserType, UserRegistration
from plants.models import Plants, PlantsClassifications
from core.config import settings
import sys
sys.path.append('.')  

from database import Base  
target_metadata = Base.metadata

config = context.config
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True
    )
    return context.run_migrations()

async def run_async_migrations():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()