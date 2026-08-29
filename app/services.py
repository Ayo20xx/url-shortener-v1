from secrets import token_urlsafe

from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.model import Url
from app.schema import UrlCreate, UrlUpdate


def shortcode_generator():
    return token_urlsafe(6)

async def create_url_service(input:UrlCreate,session:AsyncSession):
     new_url= Url(
          url = str(input.url),
          shortcode= shortcode_generator()
     )

     session.add(new_url)
     await session.commit()
     await session.refresh(new_url)
     return new_url


async def get_url_service(input:str,session:AsyncSession):
    statement=select(Url).where(Url.shortcode == input)
    result=await session.execute(statement)
    url= result.scalars().first()
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Url Not Found")
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
    result = await session .execute (statement)
    query = result.scalars().first()
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
    url.url=input.url

    session.add(url)
    await session.commit()
    await session.refresh(url)
    return url




