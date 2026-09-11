from datetime import datetime, timedelta, timezone

from sqlmodel import Field, SQLModel


class Url (SQLModel,table=True):
    id : int | None = Field(default=None,primary_key=True)
    url : str
    shortcode : str = Field( unique=True, index= True)
    created_at: datetime = Field( default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    expires_at: datetime | None = Field(default_factory=lambda: (datetime.now(timezone.utc) + timedelta(days=30)).replace(tzinfo=None))

class Clicks (SQLModel,table=True):
    id : int | None = Field(default=None,primary_key=True)
    url_id: int = Field(foreign_key="url.id")
    clicked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))