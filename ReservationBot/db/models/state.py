from ReservationBot.db.db import Base
from sqlalchemy import Column, ForeignKey, BigInteger, String, Boolean, JSON, Integer


class State(Base):
    __tablename__ = 'states'

    number = Column(Integer, default=0)
    data = Column(JSON, nullable=True)
    user_id = Column(
        BigInteger,
        ForeignKey('users.chat_id'),
        nullable=False,
        unique=True,
        primary_key=True
    )
