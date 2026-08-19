from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import SessionDep, create_db_tables
from app.schema import UrlCreate, UrlRead
from app.services import create_url_service, get_url_service


@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_db_tables()
    yield

app= FastAPI(lifespan=lifespan )

@app.post("/shorten",response_model=UrlRead)
async def create_url(url_code:UrlCreate,session:SessionDep):
    return await create_url_service(url_code,session)


@app.get("/url/{shortcode}")
async def redirect_url(shortcode:str,session:SessionDep):
    return await get_url_service(shortcode,session)