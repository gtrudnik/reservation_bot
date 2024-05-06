import asyncio
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from ReservationBot.db.db import get_session
from ReservationBot.db.models.user import User
from ReservationBot.db.models.reservation import Reservation
from ReservationBot.db.models.room import Room
from ReservationBot.db.models.token import Token


class Controller():
    """ Users """
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

    """ Reservations """
    async def add_reservation(self):
        pass

    """ Rooms """

    async def add_room(self,
                       number: str,
                       type_class: str,
                       places: int,
                       computer_places: int,
                       multimedia: bool,
                       description: str):
        session: AsyncSession = await get_session()
        room = Room(number=number, type_class=type_class,
                    places=places, computer_places=computer_places,
                    multimedia=multimedia, description=description)
        session.add(room)
        await session.commit()

    async def get_free_rooms(self):
        pass

    """ Tokens """
    async def add_token(self, token):
        session: AsyncSession = await get_session()
        token = Token(token=token)
        session.add(token)
        await session.commit()

    async def del_token(self, token):
        session: AsyncSession = await get_session()
        token = (await session.execute(select(Token).filter(Token.token == token))).scalar()
        await session.delete(token)
        await session.commit()


controller = Controller()

#
# async def start():
#     await controller.del_token("lol")
#
#
# asyncio.run(start())
