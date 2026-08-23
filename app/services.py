from secrets import token_urlsafe

from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse
from sqlmodel import select

from app.database import SessionDep
from app.model import Url
from app.schema import UrlCreate


def shortcode_generator():
    return token_urlsafe(6)
async def create_url_service(input:UrlCreate,session:SessionDep):
     new_url= Url(
          url = str(input.url),
          shortcode= shortcode_generator()
     )

     session.add(new_url)
     await session.commit()
     await session.refresh(new_url)
     return new_url


async def get_url_service(input:str,session:SessionDep):
    statement=select(Url).where(Url.shortcode == input)
    result=await session.execute(statement)
    url= result.scalars().first()
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Url Not Found")
    return RedirectResponse(
        url = url.url,
        status_code= status.HTTP_302_FOUND
    )


async def get_list_url(session: SessionDep):
    statement= select(Url)
    result= await session.execute(statement)
    return result.scalars().all()


async def delete_Url(id:int, session:SessionDep):
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

