import asyncio
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from ReservationBot.db.db import get_session
from ReservationBot.db.models.user import User
from ReservationBot.db.models.reservation import Reservation
from ReservationBot.db.models.room import Room
from ReservationBot.db.models.token import Token
from ReservationBot.db.models.state import State


class Controller():
    """ Users """

    @staticmethod
    async def add_user(tg_id: str, chat_id: int):
        session: AsyncSession = await get_session()
        query = select(User).filter(User.tg_id == tg_id)
        res = (await session.execute(query)).scalars().all()
        print("res", res)
        if len(res) == 0:
            user = User(tg_id=tg_id, chat_id=chat_id, permission="Not")
            session.add(user)
            await session.commit()
            await Controller.update_state(chat_id=chat_id, number=0, data={"attempts": 0})
            return "User added"
        elif len(res) == 1:
            await session.commit()
            return "User already exists"
        else:
            await session.commit()
            return "Too many users with one tg_id"

    @staticmethod
    async def update_user(tg_id: str, chat_id: int):
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

    @staticmethod
    async def change_permission(tg_id: str, permission: str):
        try:
            session: AsyncSession = await get_session()
            user = (await session.execute(select(User).filter(User.tg_id == tg_id))).scalar()
            user.permission = permission
            await session.commit()
            if permission == "NOT":
                await Controller.update_state(chat_id=user.chat_id, number=0, data={"attempts": 0})
            else:
                await Controller.update_state(chat_id=user.chat_id, number=1, data={})
            return {"info": "Permission given", "chat_id": user.chat_id}
        except Exception:
            print("Error: change permission")
            return "Error: change permission"

    @staticmethod
    async def check_permission(chat_id: int):
        try:
            session: AsyncSession = await get_session()
            user = (await session.execute(select(User).filter(User.chat_id == chat_id))).scalar()
            return user.permission == "YES"
        except:
            pass

    """ States """

    @staticmethod
    async def update_state(chat_id: int, number=1, data=None):
        session: AsyncSession = await get_session()
        res = (await session.execute(select(State).filter(State.user_id == chat_id))).scalars().all()
        if len(res) == 0:
            state = State(user_id=chat_id, number=number, data=None)
            session.add(state)
            await session.commit()
            return "State for user didn't exist, state added"
        elif len(res) == 1:
            state = (await session.execute(select(State).filter(State.user_id == chat_id))).scalar()
            state.user_id = chat_id
            state.number = number
            if data:
                state.data = data
            await session.commit()
            return "State for user updated"
        else:
            await session.commit()
            return "Too many states for this user"

    @staticmethod
    async def get_state(chat_id: int, data=None):
        pass

    """ Reservations """

    @staticmethod
    async def add_reservation(date, time_start, time_end,
                              description, owner, class_id):
        session: AsyncSession = await get_session()
        reservation = Reservation(date=date,
                                  time_start=time_start,
                                  time_end=time_end,
                                  description=description,
                                  owner=owner,
                                  class_id=class_id)
        session.add(reservation)
        await session.commit()

    @staticmethod
    async def get_active_reservations(chat_id):
        # TODO: only active reservations
        session: AsyncSession = await get_session()
        res = (await session.execute(select(Reservation).filter(Reservation.owner == chat_id))).scalars().all()
        return res

    @staticmethod
    async def delete_reservation(id: int):
        session: AsyncSession = await get_session()
        await session.execute(delete(Reservation).filter(Reservation.id == id))
        await session.commit()

    """ Rooms """

    @staticmethod
    async def add_room(number: str,
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

    @staticmethod
    async def update_room(number: str,
                          type_class: str,
                          places: int,
                          computer_places: int,
                          multimedia: bool,
                          description: str):
        session: AsyncSession = await get_session()
        room = (await session.execute(select(Room).filter(Room.number == number))).scalar()
        room.type_class = type_class
        room.places = places
        room.computer_places = computer_places
        room.multimedia = multimedia
        room.description = description
        await session.commit()

    @staticmethod
    async def delete_room(number: str):
        session: AsyncSession = await get_session()
        await session.execute(delete(Room).filter(Room.number == number))
        await session.commit()

    @staticmethod
    async def get_all_rooms():
        session: AsyncSession = await get_session()
        rooms = (await session.execute(select(Room))).scalars()
        await session.commit()
        return rooms

    @staticmethod
    async def get_free_rooms():
        # TODO
        pass

    """ Tokens """

    @staticmethod
    async def add_token(token):
        session: AsyncSession = await get_session()
        token = Token(token=token)
        session.add(token)
        await session.commit()

    @staticmethod
    async def del_token(token):
        session: AsyncSession = await get_session()
        await session.execute(delete(Token).filter(Token.token == token))
        await session.commit()


controller = Controller()

#
# async def start():
#     await controller.del_token("lol")
#
#
# asyncio.run(start())
# asyncio.run(controller.update_state(324324, 2))
# asyncio.run(controller.add_user("dfsdfdsвпапавпавfd", 22334534524324))
