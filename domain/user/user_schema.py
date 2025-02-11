from pydantic import BaseModel, field_validator, EmailStr
from pydantic_core.core_schema import FieldValidationInfo


class UserCreate(BaseModel):
    name: str
    password: str
    check_password: str
    email: EmailStr

    @field_validator("name", "password", "check_password", "email")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v

    @field_validator("check_password")
    def password_match(cls, v, info: FieldValidationInfo):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        return v


# 로그인 API의 출력항목에 해당하는 스키마
class Token(BaseModel):
    access_token: str
    token_type: str
    name: str


class User(BaseModel):
    id: int
    name: str
    email: str
