from contextlib import asynccontextmanager

from fastapi import FastAPI, Query

from app.database import SessionDep, create_db_tables
from app.schema import UrlCreate, UrlRead
from app.services import (
    analytics,
    create_url_service,
    delete_url,
    get_list_url,
    get_url_service,
    update_url_service,
)


@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_db_tables()
    yield

app= FastAPI(lifespan=lifespan )

@app.post("/urls",response_model=UrlRead)
async def create_url(url_code:UrlCreate,session:SessionDep):
    return await create_url_service(url_code,session)


@app.get("/urls",response_model=list[UrlRead])
async def list_url(session:SessionDep,skip: int = Query(0,ge=0,description="Number of rows to skip"),limit: int = Query(10,ge=10,description="Max rows to return")):
    return await get_list_url(session,skip,limit)

@app.get("/urls/{shortcode}")
async def redirect_url(shortcode:str,session:SessionDep):
    return await get_url_service(shortcode,session)


@app.patch("/urls/{shortcode}")
async def update(shortcode: str, session: SessionDep):
    return await update_url_service(shortcode,session)

@app.delete("/urls/{id}")
async def delete_urls(shortcode:str,session:SessionDep):
    return await delete_url(shortcode,session)

@app.get("/analytics")
async def anaylze(shortcode: int,session:SessionDep):
    return await analytics(shortcode,session)
    