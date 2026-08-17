from typing import Annotated  # noqa: I001

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from config import postgres_url
from fastapi import Depends

engine= create_async_engine(
    url= postgres_url,
    echo = True
)


async def create_db_tables():
    async with engine.begin() as connection:
        from app.model import Url  # noqa: F401
        await connection.run_sync(SQLModel.metadata.create_all)



asyncsession= async_sessionmaker(
        bind= engine,
        class_= AsyncSession,
        expire_on_commit= False
    )


async def get_session ():
    async with asyncsession as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]