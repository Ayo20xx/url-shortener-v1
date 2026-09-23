from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Url (SQLModel,table=True):
    id : int | None = Field(default=None,primary_key=True)
    url : str
    shortcode : str = Field( unique=True, index= True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None

class Clicks (SQLModel,table=True):
    id : int | None = Field(default=None,primary_key=True)
    url_id: int = Field(foreign_key="url.id", ondelete="CASCADE")
    clicked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))