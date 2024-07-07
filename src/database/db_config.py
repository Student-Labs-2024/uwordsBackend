from datetime import datetime
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy import TIMESTAMP, Boolean, DateTime, Integer, MetaData, String
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase

from src.config.instance import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USER,
    POSTGRES_PASSWORD
)

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
Base: DeclarativeMeta = declarative_base()

metadata = MetaData()

class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    firstname: Mapped[str] = mapped_column(String, nullable=False)
    lastname: Mapped[str] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=True)

    created_at = mapped_column(TIMESTAMP, default=datetime.now)
    birth_date = mapped_column(DateTime, nullable=True)

    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker: AsyncSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
