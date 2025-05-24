from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class GameLogLike(Base):
    __tablename__ = "game_log_likes"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, ForeignKey("users.name", ondelete="CASCADE"))
    game_log_id = Column(Integer, ForeignKey("game_logs.id", ondelete="CASCADE"))
    flag = Column(Boolean, nullable=False)

    user = relationship("User", back_populates="game_log_likes")
    game_log = relationship("GameLog", back_populates="likes")

    # 한 사용자가 같은 게시글에 여러 번 좋아요를 누를 수 없도록 제한
    __table_args__ = (
        UniqueConstraint("user_name", "game_log_id", name="unique_game_log_like"),
    )
