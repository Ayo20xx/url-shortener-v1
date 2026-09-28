from datetime import datetime,timezone ,timedelta
from secrets import token_urlsafe

from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import exists, func, select

from app.model import Clicks, Url
from app.schema import UrlCreate, UrlUpdate

RESERVED_SHORTCODES = frozenset({"docs", "health", "urls"})


def shortcode_generator():
    return token_urlsafe(6)

async def is_exists(
    session: AsyncSession,
    shortcode: str,
    exclude_url_id: int | None = None,
) -> bool:
    conditions = [Url.shortcode == shortcode]
    if exclude_url_id is not None:
        conditions.append(Url.id != exclude_url_id)

    statement = select(exists().where(*conditions))
    is_exists= await session.scalar(statement)
    return is_exists


def normalize_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

async def create_url_service(input:UrlCreate,session:AsyncSession):
    if "expires_at" not in input.model_fields_set:
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    elif input.expires_at is None:
        expires_at = None
    else:
        expires_at = normalize_utc(input.expires_at)

    custom_shortcode = input.custom_shortcode
    if custom_shortcode in RESERVED_SHORTCODES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Custom shortcode is already taken.",
        )

    max_attempts = 1 if custom_shortcode else 5
    for _ in range(max_attempts):
        shortcode = custom_shortcode or shortcode_generator()
        if await is_exists(session, shortcode):
            if custom_shortcode:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Custom shortcode is already taken.",
                )
            continue

        new_url = Url(
            url=str(input.url),
            shortcode=shortcode,
            expires_at=expires_at,
        )
        session.add(new_url)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            if await is_exists(session, shortcode):
                if custom_shortcode:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Custom shortcode is already taken.",
                    )
                continue
            raise

        await session.refresh(new_url)
        return new_url

    if custom_shortcode:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Custom shortcode is already taken.",
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not generate a unique shortcode.",
    )


async def get_url_service(input: str, session: AsyncSession):
    statement=select(Url).where(Url.shortcode == input)
    result=await session.scalars(statement)
    url= result.first()
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Url Not Found")
    if (
        url.expires_at is not None
        and url.expires_at < normalize_utc(datetime.now(timezone.utc))
    ):
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
    url_id = url.id

    update_data = input.model_dump(exclude_unset=True)
    new_shortcode = update_data.pop("custom_shortcode", None)
    if new_shortcode is not None:
        if new_shortcode in RESERVED_SHORTCODES:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Custom shortcode is already taken.",
            )
        if await is_exists(session, new_shortcode, exclude_url_id=url.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Custom shortcode is already taken.",
            )
        update_data["shortcode"] = new_shortcode

    for field,value in update_data.items():
        if field == "url":
            value = str(value)
        setattr(url,field,value)

    session.add(url)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        if new_shortcode is not None and await is_exists(
            session, new_shortcode, exclude_url_id=url_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Custom shortcode is already taken.",
            )
        raise
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
