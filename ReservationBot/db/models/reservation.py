from ReservationBot.db.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Time, Date, BigInteger


class Reservation(Base):
    __tablename__ = 'reservations'
    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    date = Column(Date)
    time_start = Column(Time)
    time_end = Column(Time)
    description = Column(String)
    owner = Column(BigInteger,
                   ForeignKey('users.chat_id'))
    class_id = Column(
        Integer,
        ForeignKey('rooms.id')
    )