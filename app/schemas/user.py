from pydantic import BaseModel, field_validator, EmailStr
from pydantic_core.core_schema import FieldValidationInfo
from typing import Optional

from app.core.exceptions import NotAcceptableException


class User(BaseModel):
    id: int
    name: str
    email: str


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
    def password_match(cls, v: str, info: FieldValidationInfo) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise NotAcceptableException("Password does not match.")
        return v


class UserUpdate(BaseModel):
    email: Optional[str] = None


class Token(BaseModel):
    """
    로그인 API의 출력항목에 해당하는 스키마
    """

    access_token: str
    token_type: str
    name: str
