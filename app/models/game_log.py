from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class GameLog(Base):
    __tablename__ = "game_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )  # 기록한 사용자의 id
    game_id = Column(
        Integer, ForeignKey("games.id", ondelete="CASCADE")
    )  # 작성할 게임의 id
    date = Column(DateTime, nullable=False)  # 기록을 작성한 일시
    during_time = Column(Integer, nullable=False)  # 게임을 한 시간
    participant_num = Column(Integer, nullable=False)  # 게임을 한 인원
    subject = Column(String, nullable=False)  # 제목
    content = Column(Text, nullable=True)  # 내용
    picture = Column(String, nullable=True)  # 사진

    user = relationship("User", back_populates="played_the_games")
    game = relationship("Game", back_populates="logs")
