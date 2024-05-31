from ReservationBot.db.db import Base
from sqlalchemy import Column, ForeignKey, BigInteger, String, Boolean, JSON, Integer


class State(Base):
    """"
    0 - auth
    1 - main menu
    2 - create reservation
    3 - delete reservations
    """
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
