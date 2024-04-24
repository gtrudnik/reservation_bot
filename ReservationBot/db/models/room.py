from ReservationBot.db.db import Base
from sqlalchemy import Column, Integer, String, Boolean


class Room(Base):
    __tablename__ = 'rooms'
    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    number = Column(String, unique=True)
    type_class = Column(String)
    places = Column(Integer)
    computer_places = Column(Integer)
    multimedia = Column(Boolean)
    description = Column(String)
