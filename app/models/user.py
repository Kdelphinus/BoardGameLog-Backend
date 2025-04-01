from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # 사용자의 이름
    email = Column(String, unique=True, nullable=False)  # 사용자의 이메일
    password = Column(String, nullable=False)  # 사용자의 비밀번호

    # 추후 쿼리 효율이 떨어지면 인덱싱 고려
    is_deleted = Column(Boolean, nullable=False, default=False)  # 탈퇴 유무
    deleted_at = Column(DateTime, nullable=True)  # 탈퇴한 날짜

    played_the_games = relationship("GameLog", back_populates="user")
