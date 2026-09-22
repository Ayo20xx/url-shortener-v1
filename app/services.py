from datetime import datetime,timezone ,timedelta
from secrets import token_urlsafe

from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import exists, func, select

from app.model import Clicks, Url
from app.schema import UrlCreate, UrlUpdate


def shortcode_generator():
    return token_urlsafe(6)

async def is_exists(session:AsyncSession,shortcode:str) -> bool:
    statement=select(exists().where(Url.shortcode == shortcode))
    is_exists= await session.scalar(statement)
    return is_exists


def to_naive_utc(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt

async def create_url_service(input:UrlCreate,session:AsyncSession):
    if input.custom_shortcode:
     if input.custom_shortcode in ["docs", "health", "urls"]:
         raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Custom shortcode is already taken.")
     if await is_exists(session,input.custom_shortcode):
         raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Custom shortcode is already taken.") 
     shortcode = input.custom_shortcode

    else:
        shortcode = shortcode_generator()
        max_attempts = 5
        attempts = 0
        while await is_exists(session, shortcode):
            attempts += 1
            if attempts >= max_attempts:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Could not generate a unique shortcode."
                )
            shortcode = shortcode_generator()

    expires_at = (
        to_naive_utc(input.expires_at)
        if input.expires_at is not None
        else (datetime.now(timezone.utc) + timedelta(days=30)).replace(tzinfo=None)
    )

    new_url = Url(
        url=str(input.url),
        shortcode=shortcode,
        expires_at=expires_at,
    )

    session.add(new_url)
    await session.commit()
    await session.refresh(new_url)
    return new_url


async def get_url_service(input: str, session: AsyncSession):
    statement=select(Url).where(Url.shortcode == input)
    result=await session.scalars(statement)
    url= result.first()
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Url Not Found")
    if url.expires_at <  to_naive_utc(datetime.now(timezone.utc)):
        raise HTTPException(status_code=status.HTTP_410_GONE,detail="expired url code" )

    new_click = Clicks(url_id=url.id)
    session.add(new_click)
    await session.commit()

    return RedirectResponse(
        url = url.url,
        status_code= status.HTTP_302_FOUND
    )


async def get_list_url(session: AsyncSession,skip: int = 0,limit: int = 10):
    statement= select(Url).offset(skip).limit(limit=limit)
    result= await session.scalars(statement)
    return result.all()


async def delete_url(shortcode: str, session:AsyncSession):
    statement = select(Url). where(Url.shortcode == shortcode )
    result = await session .scalars(statement)
    query = result.first()
    if not query:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"data with id {shortcode } can not be found"
        )
    await session.delete(query)
    await session.commit()
    return {"detail": f"Successfully deleted item {shortcode}"}


async def update_url_service(shortcode: str ,session: AsyncSession,input:UrlUpdate):

    statement=select(Url).where(Url.shortcode == shortcode)
    result=await session.scalars(statement)
    url= result.first()
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Url Not Found")

    update_data = input.model_dump(exclude_unset=True)
    if await is_exists(session,input.custom_shortcode):
             raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Custom shortcode is already taken.") 
    for field,value in update_data.items():
        setattr(url,field,value)

    session.add(url)
    await session.commit()
    await session.refresh(url)
    return url

async def analytics(shortcode:str,session:AsyncSession):
    statement=select(Url).where(Url.shortcode == shortcode)
    result=await session.scalars(statement)
    url= result.first()
    if not url:
        raise HTTPException(status.HTTP_404_NOT_FOUND,detail="url not found ")

    count_statement =  select(func.count(Clicks.id)).where(Clicks.url_id==url.id)
    total_clicks = await session.scalar(count_statement)
    return {"shortcode":shortcode,
            "clicks" : total_clicks}
