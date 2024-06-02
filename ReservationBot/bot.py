from telebot.async_telebot import AsyncTeleBot
from ReservationBot.config import settings
from ReservationBot.db.controller import controller
from ReservationBot.db.models.reservation import Reservation

bot = AsyncTeleBot(settings.token)


def check_permission(func):
    async def wrapper(message):
        if await controller.check_permission(chat_id=message.chat.id):
            return await func(message)
        else:
            return await bot.send_message(message.chat.id, "Вам не доступна эта функция. "
                                                           "Для получения доступа введите токен, "
                                                           "или попросите администратора выдать вам доступ")

    return wrapper


async def send_message(chat_id: int, message: str):
    """ Function for send message """
    await bot.send_message(chat_id, message)


@bot.message_handler(commands=['start'])
async def start_message(message):
    """ Function save user in db and send info message with list of commands """
    await controller.add_user(message.chat.username, message.chat.id)
    await bot.send_message(message.chat.id, settings.start_text + "\n" + settings.list_commands)


@bot.message_handler(commands=['help'])
async def info_message(message):
    """ Function senf info message with list of commands """
    await bot.send_message(message.chat.id, settings.list_commands)


@bot.message_handler(commands=['save'])
async def save_message(message):
    """ Function update user id in Telegram in db and send info message """
    await controller.update_user(message.chat.username, message.chat.id)
    await bot.send_message(message.chat.id, settings.save_text)


@bot.message_handler(commands=['new_reservation'])
@check_permission
async def new_reservation(message):
    """ Function for create new reservation """
    await controller.update_state(chat_id=message.chat.id, number=2, data={})


@bot.message_handler(commands=['list_reservations'])
@check_permission
async def list_reservations(message):
    """ Function for get list reservations """
    reservations = await controller.get_active_reservations(message.chat.id)
    if len(reservations) == 0:
        await bot.send_message(message.chat.id, "У вас нет активных броней аудитории.")
    else:
        text_message = "Список ваших активных броней:\n\n"
        for reservation in reservations:
            text_message += "ID: " + str(reservation.id) + "\n"
            text_message += "Дата: " + str(reservation.date) + "\n"
            text_message += "Время начала: " + str(reservation.time_start) + "\n"
            text_message += "Время окончания: " + str(reservation.time_end) + "\n"
            room = await controller.get_room(reservation.class_id)
            text_message += "Номер аудитории: " + str(room.number) + "\n"
            text_message += "Описание: " + str(reservation.description) + "\n\n"
        await bot.send_message(message.chat.id, text_message)
    return len(reservations)


@bot.message_handler(commands=['delete_reservation'])
@check_permission
async def delete_reservation(message):
    """ Function for delete reservation """
    await controller.update_state(chat_id=message.chat.id, number=3, data={})
    count = await list_reservations(message)
    if count != 0:
        await bot.send_message(message.chat.id, "Выберите бронь для удаления. (id - брони)")


@bot.message_handler(content_types=['text'])
async def new_message(message):
    state = await controller.get_state(message.chat.id)
    if state == "User not exist":
        res = await controller.add_user(message.chat.username, message.chat.id)
        if "User already exists":
            await controller.update_state(chat_id=message.chat.id, number=0, data={"attempts": 0})
        await bot.send_message(message.chat.id, "Для получения доступа введите токен, "
                                                "или попросите администратора выдать вам доступ")
    elif state["number"] == 0:
        # check token
        if await controller.check_token(chat_id=message.chat.id, token=message.text):
            await bot.send_message(message.chat.id, "Вы получили доступ к сервису!")
        else:
            state["data"]["attempts"] += 1
            await controller.update_state(chat_id=message.chat.id, number=0, data=state["data"])
            await bot.send_message(message.chat.id, "Такого токена нет!")
        await bot.delete_message(message.chat.id, message.id)
    elif state["number"] == 2:
        pass
        # adding reservations
    elif state["number"] == 3:
        # delete reservation
        if message.text.isdigit():
            id = int(message.text)
            try:
                res = await controller.delete_reservation(id)
                if res == "Wrong id":
                    await bot.send_message(message.chat.id, "Неверный id")
                else:
                    await bot.send_message(message.chat.id, "Бронь удалена.")
                    await controller.update_state(chat_id=message.chat.id, number=1)
            except:
                await bot.send_message(message.chat.id, "Такой брони нет.")
        else:
            await bot.send_message(message.chat.id, "id брони должно быть числом.")


async def start_bot():
    await bot.infinity_polling()
