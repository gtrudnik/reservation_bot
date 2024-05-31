import uvicorn
import asyncio
from fastapi import FastAPI
from multiprocessing import Process
from ReservationBot.db.controller import controller
from ReservationBot.config import settings
from ReservationBot.bot import start_bot
from ReservationBot.generate_token import generate_token
from ReservationBot.schemas.room_types import RoomTypes
from ReservationBot.schemas.RoomsResponse import RoomsResponse
from ReservationBot.schemas.permission_types import PermissionsTypes
from ReservationBot.bot import send_message

app = FastAPI(
    title=settings.app_name,
    version="0.0.1",
)


@app.post("/change_permission")
async def change_permission(user_login: str, permission: PermissionsTypes):
    """ Change user permission  by telegram login"""
    res = await controller.change_permission(user_login, permission)
    if res["info"] == "Permission given":
        if permission == "YES":
            await send_message(chat_id=res["chat_id"], message="Администратор предоставил доступ к сервису.")
        elif permission == "NOT":
            await send_message(chat_id=res["chat_id"], message="Администратор отменил доступ к сервису.")


@app.get('/get_token')
async def get_token():
    token = generate_token()
    await controller.add_token(token)
    return {"token": token}


@app.post("/add_room/")
async def add_room(number: str,
                   type_class: RoomTypes,
                   places: int,
                   computer_places: int,
                   multimedia: bool,
                   description: str):
    """ Function for add room
        - type_class: "лекционная", "практическая", "переговорная"
        - places - сидячие места (без учёта компьютерных мест)
        - computer places - компьютерные места
    """
    if type_class in ["лекционная", "практическая", "переговорная"]:
        await controller.add_room(number, type_class,
                                  places, computer_places,
                                  multimedia, description)
        return "Room added"
    else:
        return "Bad input type_class"


@app.post("/update_room/")
async def update_room(number: str,
                      type_class: RoomTypes,
                      places: int,
                      computer_places: int,
                      multimedia: bool,
                      description: str):
    """ Function for update room
        - type_class: "лекционная", "практическая", "переговорная"
        - places - сидячие места (без учёта компьютерных мест)
        - computer places - компьютерные места
    """
    if type_class in ["лекционная", "практическая", "переговорная"]:
        await controller.update_room(number, type_class,
                                     places, computer_places,
                                     multimedia, description)
        return "Room updated"
    else:
        return "Bad input type_class"


@app.post("/get_all_rooms/")
async def get_all_rooms():
    """ Function for get all rooms"""
    try:
        res = await controller.get_all_rooms()
        response = []
        for room in res:
            print(room)
            response.append(RoomsResponse(number=room.number,
                                          type_class=room.type_class,
                                          places=room.places,
                                          computer_places=room.computer_places,
                                          multimedia=room.multimedia,
                                          description=room.description))
        return response
    except:
        return f"error"


@app.post("/delete_room/")
async def delete_room(number: str):
    """ Function for delete room """
    try:
        await controller.delete_room(number)
        return "room deleted"
    except:
        return "error"


def bot_app():
    asyncio.run(start_bot())


@app.on_event('startup')
async def on_startup():
    """Function for starting TelegramBot"""
    try:
        proc = Process(target=bot_app)
        proc.start()
    except:
        pass


if __name__ == "__main__":
    uvicorn.run('main:app', host="127.0.0.1", port=8080, reload=True)
