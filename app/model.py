from pydantic import AnyHttpUrl, BaseModel


class url (BaseModel):
    id : int 
    short_code : str
    url : AnyHttpUrl