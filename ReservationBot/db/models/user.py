from ReservationBot.db.db import Base
from sqlalchemy import Column, Integer, String


class User(Base):
    __tablename__ = 'users'
    chat_id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True
    )
    tg_id = Column(
        Integer,
        nullable=False,
        unique=True,
    )
    permission = Column(String)

