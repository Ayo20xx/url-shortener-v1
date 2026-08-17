from secrets import token_urlsafe

from sqlmodel import select

from app.database import SessionDep
from app.model import Url
from app.schema import UrlCreate


def shortcode_generator():
    return token_urlsafe(6)
async def create_url_service(input:UrlCreate,session:SessionDep):
     new_url= Url(
          url = input.url,
          shortcode= shortcode_generator()
     )

     session.add(new_url)
     await session.commit()
     await session.refresh(new_url)
     return new_url
