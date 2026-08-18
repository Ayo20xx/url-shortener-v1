from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel


class UrlCreate (BaseModel):
    
    url: AnyHttpUrl

class UrlRead(UrlCreate):
    id: int 

    created_at: datetime

    expires_at: datetime |None  

