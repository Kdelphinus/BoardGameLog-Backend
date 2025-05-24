from fastapi import Depends
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
    select,
    func,
    and_,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from app.api.dependencies import get_db
from app.db.database import Base
from app.models.game_log_like import GameLogLike


class GameLog(Base):
    __tablename__ = "game_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(
        String, ForeignKey("users.name", ondelete="CASCADE")
    )  # 기록한 사용자의 id
    game_name = Column(
        String, ForeignKey("games.name", ondelete="CASCADE")
    )  # 작성할 게임의 id
    created_at = Column(
        DateTime, default=func.now(), nullable=False
    )  # 기록을 작성하 날짜
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )  # 기록을 수정한 날짜
    during_time = Column(Integer, nullable=False)  # 게임을 한 시간
    participant_num = Column(Integer, nullable=False)  # 게임을 한 인원
    subject = Column(String, nullable=False)  # 제목
    content = Column(Text, nullable=True)  # 내용
    picture = Column(String, nullable=True)  # 사진
    like_num = Column(Integer, default=0, nullable=False)  # 좋아요 수

    user = relationship("User", back_populates="played_the_games")
    game = relationship("Game", back_populates="logs")
    likes = relationship("GameLogLike", back_populates="game_log")

    async def update_like_num(self, db: AsyncSession = Depends(get_db)):
        query = select(func.count()).where(
            and_(GameLogLike.game_log_id == self.id, GameLogLike.flag == True)
        )
        result = await db.execute(query)
        self.like_num = result.scalar()
        await db.commit()
