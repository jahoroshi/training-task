import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

engine = create_async_engine(os.getenv("DATABASE_URL"))

async_session = async_sessionmaker(engine, expire_on_commit=False)

local_session = async_sessionmaker(engine, expire_on_commit=False, autocommit=False, autoflush=False)

class Base(DeclarativeBase):
    pass

async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def delete_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def get_session() -> AsyncSession:
    async with local_session() as session:
        yield session