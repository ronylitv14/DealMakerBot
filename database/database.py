import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from dotenv import load_dotenv
from .models import Base

load_dotenv(".env")

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
db_name = os.getenv("POSTGRES_DB")

SQLALCHEMY_DATABASE_URL_LOCAL = f"postgresql+asyncpg://postgres:postgres@localhost:5432/dealmakerbot"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL_LOCAL, echo=True)

async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, future=True
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        # await conn.run_sync(Base.metadata.create_all)

# asyncio.run(init_db())
