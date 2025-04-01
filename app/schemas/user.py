from pydantic import BaseModel, field_validator, EmailStr
from pydantic_core.core_schema import ValidationInfo
from typing import Optional

from app.core.exceptions import NotAcceptableException


class UserData(BaseModel):
    id: int
    name: str
    email: EmailStr


class UserResponse(BaseModel):
    name: str
    email: EmailStr

    class Config:
        orm_mode = True
        exclude = {"id", "password"}


class UserCreate(BaseModel):
    name: str
    password: str
    check_password: str
    email: EmailStr

    @field_validator("name", "password", "check_password", "email")
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise NotAcceptableException("Empty values are not allowed.")
        return v

    @field_validator("check_password")
    def password_match(cls, v: str, info: ValidationInfo) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise NotAcceptableException("Password does not match.")
        return v


class UserUpdate(BaseModel):
    email: Optional[str] = None


class AccessToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    name: str


class RefreshToken(BaseModel):
    access_token: str
    token_type: str


class PasswordResetRequest(BaseModel):
    name: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class RestoreUserRequest(BaseModel):
    name: str


class RestoreUserConfirm(BaseModel):
    token: str
