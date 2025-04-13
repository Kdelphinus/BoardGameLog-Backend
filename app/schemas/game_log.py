from pydantic import BaseModel, field_validator

from app.core.exceptions import NotAcceptableException


class GameLog(BaseModel):
    id: int
    user_id: int
    game_id: int
    during_time: int
    participant_num: int
    subject: str
    content: str | None = None
    picture: str | None = None


class GameLogCreate(BaseModel):
    game_name: str
    during_time: int
    participant_num: int
    subject: str
    content: str | None = None
    picture: str | None = None

    @field_validator("during_time")
    def not_zero(cls, v: int) -> int:
        if 0 >= v:
            raise NotAcceptableException(
                "During_time dose not allow values less than or equal to 0."
            )
        return v

    @field_validator("subject")
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise NotAcceptableException("Empty values are not allowed.")
        return v


class GameLogUpdate(BaseModel):
    game_id: int
    during_time: int
    participant_num: int
    subject: str
    content: str | None = None
    picture: str | None = None
