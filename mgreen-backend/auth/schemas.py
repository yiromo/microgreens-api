from pydantic import BaseModel

class BaseToken(BaseModel):
    access_token: str

class TokenRead(BaseToken):
    refresh_token: str