from secrets import token_urlsafe

from fastapi import HTTPException, status
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
    url=await session.exec(statement).first()
    if not url :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Url Not Found")
    return url



async def generate_token():
    def functionize():
        yield 

    return functionize()