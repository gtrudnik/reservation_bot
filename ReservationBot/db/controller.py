import asyncio
import datetime
from sqlalchemy import select, update, delete, and_, or_
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
    async def change_permission(permission: str, tg_id: str | None = None, chat_id: int | None = None):
        try:
            session: AsyncSession = await get_session()
            if tg_id is not None:
                user = (await session.execute(select(User).filter(User.tg_id == tg_id))).scalar()
            elif chat_id is not None:
                user = (await session.execute(select(User).filter(User.chat_id == chat_id))).scalar()
            user.permission = permission
            await session.commit()
            if permission == "NOT":
                await Controller.update_state(chat_id=user.chat_id, number=0, data={"attempts": 0})
            else:
                await Controller.update_state(chat_id=user.chat_id, number=1)
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
            state = State(user_id=chat_id, number=number, data=data)
            session.add(state)
            await session.commit()
            return "State for user didn't exist, state added"
        elif len(res) == 1:
            state = (await session.execute(select(State).filter(State.user_id == chat_id))).scalar()
            state.user_id = chat_id
            state.number = number
            if data or number == 1:
                state.data = data
            await session.commit()
            return "State for user updated"
        else:
            await session.commit()
            return "Too many states for this user"

    @staticmethod
    async def get_state(chat_id: int, data=None):
        session: AsyncSession = await get_session()
        res = (await session.execute(select(State).filter(State.user_id == chat_id))).scalar()
        await session.commit()
        if res is not None:
            return {"number": res.number, "data": res.data}
        else:
            return "User not exist"

    """ Reservations """

    @staticmethod
    async def add_reservation(date, time_start, time_end,
                              owner, class_id, description=""):
        """
            date (str) in format year-month-day
            time_start (str) in format hours:minutes
            time_end (str) in format hours:minutes
        """
        session: AsyncSession = await get_session()
        year, month, day = map(int, date.split('-'))
        time_start = datetime.datetime.strptime(time_start, '%H:%M').time()
        time_end = datetime.datetime.strptime(time_end, '%H:%M').time()
        reservation = Reservation(date=datetime.date(year=year, month=month, day=day),
                                  time_start=time_start,
                                  time_end=time_end,
                                  description=description,
                                  owner=owner,
                                  class_id=class_id)
        session.add(reservation)
        await session.commit()

    @staticmethod
    async def get_active_reservations(chat_id):
        session: AsyncSession = await get_session()
        query = select(Reservation).filter(and_(Reservation.owner == chat_id,
                                                or_(
                                                    and_(Reservation.date == datetime.date.today(),
                                                         Reservation.time_end >= datetime.datetime.now().time()),
                                                    Reservation.date > datetime.date.today()))
                                           )
        res = (await session.execute(query)).scalars().all()
        await session.commit()
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
    async def get_free_rooms(date, time_start, time_end):
        """
            date (str) in format year-month-day
            time_start (str) in format hours:minutes
            time_end (str) in format hours:minutes
        """
        session: AsyncSession = await get_session()
        year, month, day = map(int, date.split('-'))
        time_start = datetime.datetime.strptime(time_start, '%H:%M').time()
        time_end = datetime.datetime.strptime(time_end, '%H:%M').time()
        query = select(Reservation.class_id).filter(
            and_(
                Reservation.date == datetime.date(year=year, month=month, day=day),
                or_(
                    and_(Reservation.time_start <= time_start, time_start <= Reservation.time_end),
                    and_(Reservation.time_start <= time_end, time_start <= Reservation.time_end)
                )
            )
        )
        classes_id = (await session.execute(query)).scalars().all()
        all_rooms = await Controller.get_all_rooms()
        free_rooms = []
        for room in all_rooms:
            if room.id not in classes_id:
                free_rooms.append(room)
        await session.commit()
        return free_rooms

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

    @staticmethod
    async def check_token(token, chat_id):
        session: AsyncSession = await get_session()
        res = (await session.execute(select(Token).filter(Token.token == token))).scalar()
        await session.commit()
        if res is not None:
            await Controller.change_permission(chat_id=chat_id, permission="YES")
            await Controller.del_token(token)
        return res is not None


controller = Controller()

#
# async def start():
#     await controller.del_token("lol")
#
#
# asyncio.run(start())
# asyncio.run(controller.update_state(324324, 2))
# print(type(datetime.datetime.strptime('16:00', '%H:%M').time()))
# asyncio.run(controller.add_reservation(date="2024-06-02", time_start="11:30", time_end="12:00", description="",
#                                        owner=661467077, class_id=1))
# print(datetime.datetime.now().time())
# res = asyncio.run(controller.get_active_reservations(chat_id=661467077))
# res = asyncio.run(controller.get_free_rooms(date="2024-06-02", time_start="11:30", time_end="12:00"))
# for i in res:
#     print(i.id)
# res = asyncio.run(controller.get_state(661467077))
# print(res)
