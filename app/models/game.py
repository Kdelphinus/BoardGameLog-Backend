from sqlalchemy import Column, String, Float, Integer
from sqlalchemy.orm import relationship

from app.db.database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)  # 게임 이름
    weight = Column(Float, nullable=False)  # 보드 게임의 weight
    min_possible_num = Column(Integer, nullable=False)  # 게임할 수 있는 최소 인원
    max_possible_num = Column(Integer, nullable=False)  # 게임할 수 있는 최대 인원

    logs = relationship("GameLog", back_populates="game")
