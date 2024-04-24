import asyncio
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from ReservationBot.db.db import get_session
from ReservationBot.db.models.user import User
from ReservationBot.db.models.reservation import Reservation
from ReservationBot.db.models.room import Room


class Controller():
    async def add_user(self, tg_id: str, chat_id: int):
        session: AsyncSession = await get_session()
        res = (await session.execute(select(User).filter(User.tg_id == tg_id))).scalars().all()
        if len(res) == 0:
            user = User(tg_id=tg_id, chat_id=chat_id, permission="Not")
            session.add(user)
            await session.commit()
            return "User added"
        elif len(res) == 1:
            await session.commit()
            return "User already exists"
        else:
            await session.commit()
            return "Too many users with one tg_id"

    async def update_user(self, tg_id: str, chat_id: int):
        session: AsyncSession = await get_session()
        res = (await session.execute(select(User).filter(User.chat_id == chat_id))).scalars().all()
        if len(res) == 0:
            user = User(tg_id=tg_id, chat_id=chat_id, permission="Not")
            session.add(user)
            await session.commit()
            return "User didn't exist, user added"
        elif len(res) == 1:
            user = (await session.execute(select(User).filter(User.chat_id == chat_id))).scalar()
            user.tg_id = tg_id
            await session.commit()
            return "User updated"
        else:
            await session.commit()
            return "Too many users with one chat_id"

    async def change_permission(self, tg_id: str, permission: str):
        try:
            session: AsyncSession = await get_session()
            user = (await session.execute(select(User).filter(User.tg_id == tg_id))).scalar()
            user.permission = permission
            await session.commit()
            return "Permission given"
        except Exception:
            print("Error: change permission")
            return "Error: change permission"

    async def add_reservation(self):
        pass

    async def add_room(self):
        pass

    async def get_free_rooms(self):
        pass


controller = Controller()


# async def start():
#     # x = await controller.update_user('505', 11)
#     x = await controller.change_permission('505', "Not")
#     print(x)
#
#
# asyncio.run(start())
