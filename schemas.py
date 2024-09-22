from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    # confirm_password: str
    name: str
    tag: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str
