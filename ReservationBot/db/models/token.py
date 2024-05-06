from ReservationBot.db.db import Base
from sqlalchemy import Column, Integer, String


class Token(Base):
    __tablename__ = 'tokens'
    token = Column(
        String,
        nullable=False,
        primary_key=True,
        unique=True,
    )
