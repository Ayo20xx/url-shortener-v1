from secrets import token_urlsafe

from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import exists, select

from app.model import Url,Clicks
from app.schema import UrlCreate, UrlUpdate


def shortcode_generator():
    return token_urlsafe(6)

async def is_exists(session:AsyncSession,shortcode:str) -> bool:
    statement=select(exists().where(Url.shortcode == shortcode))
    is_exists= await session.scalar(statement)
    return is_exists




async def create_url_service(input:UrlCreate,session:AsyncSession):
    if input.custom_shortcodes:
     if await is_exists(session,input.custom_shortcodes):
         raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Custom shortcode is already taken.") 
     shortcode = input.custom_shortcodes
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

    new_url= Url(
          url = str(input.url),
          shortcode= shortcode
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


async def delete_url(id:int, session:AsyncSession):
    statement = select(Url). where(Url.id == id )
    result = await session .scalars(statement)
    query = result.first()
    if not query:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"data with id {id } can not be found"
        )
    session.delete(query)
    await session.commit()
    return {"detail": f"Successfully deleted item {id}"}


async def update_url_service(id:int ,session: AsyncSession,input:UrlUpdate):

    statement=select(Url).where(Url.id == id)
    result=await session.execute(statement)
    url= result.scalars().first()
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Url Not Found")

    update_data = input.model_dump(exclude_unset=True)
    for field,value in update_data.items():
        setattr(url,field,value)

    session.add(url)
    await session.commit()
    await session.refresh(url)
    return url




