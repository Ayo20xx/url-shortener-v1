from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class UrlCreate (BaseModel):
    custom_shortcode : str | None =Field(default=None, max_length=10, pattern=r"^[a-zA-Z0-9]+$")
    url: AnyHttpUrl
    expires_at : datetime | None = None 

class UrlUpdate(BaseModel):
    custom_shortcode: str | None = Field(
        default=None, max_length=10, pattern=r"^[a-zA-Z0-9]+$"
    )
    url: AnyHttpUrl | None = None
    expires_at: datetime | None = None


class UrlRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int 
    url: AnyHttpUrl
    shortcode: str
    created_at: datetime
    expires_at: datetime | None


class UrlUpdateResponse(UrlRead):
    pass


class DeleteResponse(BaseModel):
    detail: str


class AnalyticsResponse(BaseModel):
    shortcode: str
    clicks: int
