from ReservationBot.db.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, JSON


class State(Base):
    __tablename__ = 'states'

    number = Column(Integer, default=0)
    data = Column(JSON, nullable=True)
    user_id = Column(
        Integer,
        ForeignKey('users.chat_id'),
        nullable=False,
        unique=True,
        primary_key=True
    )
