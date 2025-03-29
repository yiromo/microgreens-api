from pydantic import BaseModel

class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserRead(UserBase):
    id: str
    is_active: bool
    is_superuser: bool
    user_type: str = "user"

    class Config:
        from_attributes = True

class UserTypeBase(BaseModel):
    user_type: str

class UserTypeCreate(UserTypeBase):
    pass

class UserTypeRead(UserTypeBase): 
    id: str