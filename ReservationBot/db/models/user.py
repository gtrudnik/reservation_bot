from ReservationBot.db.db import Base
from sqlalchemy import Column, BigInteger, String


class User(Base):
    __tablename__ = 'users'
    chat_id = Column(
        BigInteger,
        nullable=False,
        unique=True,
        primary_key=True
    )
    tg_id = Column(
        String,
        nullable=False,
        unique=True,
    )
    permission = Column(String)

