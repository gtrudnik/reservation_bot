import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ReservationBot.db.db import get_session
from ReservationBot.db.models.user import User
from ReservationBot.db.models.reservation import Reservation
from ReservationBot.db.models.room import Room


class Controller():
    def add_user(selfself, tg_id: int, chat_id: int):
        pass

    def update_user(self, tg_id: int, chat_id: int):
        pass

    def change_permission(self, tg_id: int):
        pass

    def add_reservation(self):
        pass

    def add_room(self):
        pass

    def get_free_rooms(self):
        pass


controller = Controller()
