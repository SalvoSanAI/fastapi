from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from pydantic import EmailStr
from datetime import datetime

class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

class PostResponse(BaseModel):
    id: int
    title: str
    # content: str
    # published: bool
    # rating: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    # class Config:
    #     from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str   

class TokenData(BaseModel):
    id: Optional[int] = None
    

    
