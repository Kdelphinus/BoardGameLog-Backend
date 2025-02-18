from pydantic import BaseModel, field_validator
from pydantic_core.core_schema import FieldValidationInfo


class Game(BaseModel):
    id: int
    name: str
    weight: float
    max_possible_num: int
    min_possible_num: int


class GameCreate(BaseModel):
    name: str
    weight: float
    max_possible_num: int
    min_possible_num: int

    @field_validator("name")
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v.lower()

    @field_validator("weight")
    def check_weight(cls, v: float) -> float:
        if 0 <= v <= 5:
            return v
        raise ValueError("weight 값은 0~5 사이의 값만 가능합니다.")

    @field_validator("min_possible_num")
    def check_min_possible_num(cls, v: int, info: FieldValidationInfo) -> int:
        if 0 >= v:
            raise ValueError("인원은 0명보다 많아야 합니다.")
        elif v > info.data["max_possible_num"]:
            raise ValueError("최대 인원 게임은 최소 게임 인원보다 항상 커야 합니다.")
        return v
