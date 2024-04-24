import uvicorn
import asyncio
from fastapi import FastAPI
from multiprocessing import Process
from ReservationBot.config import settings
from ReservationBot.bot import start_bot


app = FastAPI(
    title=settings.app_name,
    version="0.0.1",
)


@app.post("/delete_user/{user_id}")
async def delete_user(user_id: int):
    pass


@app.get('/get_token')
async def get_token():
    token = 555
    # save token in db
    return {"token": token}


@app.post("/add_room/")
async def add_room():
    pass


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
