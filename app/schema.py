from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel


class UrlCreate (BaseModel):
    custom_shortcodes : str | None = None
    url: AnyHttpUrl
    expires_at : datetime | None 

class UrlUpdate(UrlCreate):
    pass

    

class UrlRead(UrlCreate):
    id: int 

    created_at: datetime
    shortcode: str
    expires_at: datetime |None  

