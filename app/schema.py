from datetime import timedelta

from pydantic import AnyHttpUrl, BaseModel, Field


class urlcreate (BaseModel):
    id : int 
    short_code : str
    url : AnyHttpUrl
    created_at : timedelta= Field(default=timedelta())

class url_read(urlcreate):
    url : AnyHttpUrl

