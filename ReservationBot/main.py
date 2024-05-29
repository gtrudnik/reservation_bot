import uvicorn
import asyncio
from fastapi import FastAPI
from multiprocessing import Process
from ReservationBot.db.controller import controller
from ReservationBot.config import settings
from ReservationBot.bot import start_bot
from ReservationBot.generate_token import generate_token


app = FastAPI(
    title=settings.app_name,
    version="0.0.1",
)


@app.post("/change_permission")
async def change_permission(user_login: str, permission: str):
    """ Change user permission  by telegram login"""
    await controller.change_permission(user_login, permission)


@app.get('/get_token')
async def get_token():
    token = generate_token()
    await controller.add_token(token)
    return {"token": token}


@app.post("/add_room/")
async def add_room(number: str,
                   type_class: str,
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
        return "Room add"
    else:
        return "Bad input type_class"



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
