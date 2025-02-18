from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Table
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    played_the_games = relationship("GameLog", back_populates="user")


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    min_possible_num = Column(Integer, nullable=False)
    max_possible_num = Column(Integer, nullable=False)

    logs = relationship("GameLog", back_populates="game")


class GameLog(Base):
    __tablename__ = "game_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"))
    date = Column(DateTime, nullable=False)
    during_time = Column(Integer)
    participant_num = Column(Integer)
    text_data = Column(Text)
    picture = Column(String)

    user = relationship("User", back_populates="played_the_games")
    game = relationship("Game", back_populates="logs")
