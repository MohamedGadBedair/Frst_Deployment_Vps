from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker,create_async_engine

from config import settings

# path= 'sqlite+aiosqlite:///db.sqlite'
database_url= f'{settings.db_name}://{settings.database_username}:{settings.database_password.get_secret_value()}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine=create_async_engine(database_url)

AsyncSessionLocal=async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
    )
class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db 
