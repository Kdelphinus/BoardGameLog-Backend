from pydantic import BaseModel


class GameLogLike(BaseModel):
    user_name: str

    class Config:
        from_attributes = True
