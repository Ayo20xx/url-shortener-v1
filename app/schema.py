from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, Field


class UrlCreate (BaseModel):
    custom_shortcodes : str | None =Field(default=None, max_length=10, pattern=r"^[a-zA-Z0-9]*$")
    url: AnyHttpUrl
    expires_at : datetime | None 

class UrlUpdate(UrlCreate):
    pass

    

class UrlRead(UrlCreate):
    id: int 

    created_at: datetime
    shortcode: str
    expires_at: datetime |None  

