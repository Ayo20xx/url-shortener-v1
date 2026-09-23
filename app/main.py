from fastapi import FastAPI, Query

from app.database import SessionDep
from app.schema import (
    AnalyticsResponse,
    DeleteResponse,
    UrlCreate,
    UrlRead,
    UrlUpdate,
    UrlUpdateResponse,
)
from app.services import (
    analytics,
    create_url_service,
    delete_url,
    get_list_url,
    get_url_service,
    update_url_service,
)


app = FastAPI()

@app.post("/urls",response_model=UrlRead)
async def create_url(url_code:UrlCreate,session:SessionDep):
    return await create_url_service(url_code,session)


@app.get("/urls",response_model=list[UrlRead])
async def list_url(
    session: SessionDep,
    skip: int = Query(0, ge=0, description="Number of rows to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max rows to return"),
):
    return await get_list_url(session,skip,limit)

@app.get("/urls/{shortcode}")
async def redirect_url(shortcode:str,session:SessionDep):
    return await get_url_service(shortcode,session)


@app.patch("/urls/{shortcode}", response_model=UrlUpdateResponse)
async def update(
    shortcode: str,
    session: SessionDep,
    input: UrlUpdate,
) -> UrlUpdateResponse:
    return await update_url_service(shortcode,session,input)

@app.delete("/urls/{shortcode}", response_model=DeleteResponse)
async def delete_urls(shortcode:str,session:SessionDep):
    return await delete_url(shortcode,session)

@app.get("/analytics", response_model=AnalyticsResponse)
async def anaylze(shortcode: str ,session:SessionDep):
    return await analytics(shortcode,session)
    