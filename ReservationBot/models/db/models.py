from sqlalchemy import Column, ForeignKey, Integer, String, Time, Text, Date, Boolean, DateTime, create_engine
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.orm import declarative_base

sqlite_database = "sqlite:///tgremotecontrollerbot.db"
engine = create_engine(sqlite_database)

Base = declarative_base()


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
    permissiom = Column(
        String
    )


class Class(Base):
    __tablename__ = 'classes'
    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    number = Column(
        String
    )
    type_class = Column(
        String
    )
    places = Column(
        Integer
    )
    computer_places = Column(
        Integer
    )
    multimedia = Column(
        Boolean
    )
    description = Column(
        String
    )


class Reservation(Base):
    __tablename__ = 'reservations'
    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    date = Column(
        Date
    )
    time_start = Column(
        Time
    )
    time_end = Column(
        Time
    )
    description = Column(
        String
    )
    class_id = Column(
        Integer,
        ForeignKey('classes.id')
    )
