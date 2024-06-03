import datetime

from telebot.async_telebot import AsyncTeleBot
from ReservationBot.config import settings
from ReservationBot.db.controller import controller
from ReservationBot.db.models.reservation import Reservation
from ReservationBot.schemas.room_types import RoomTypes

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
    await bot.send_message(message.chat.id, "Напишите описание вашей встречи. /cancel - для остановки действий")


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
    await controller.update_state(chat_id=message.chat.id, number=3)
    count = await list_reservations(message)
    if count != 0:
        await bot.send_message(message.chat.id,
                               "Выберите бронь для удаления. (id - брони)  /cancel - для остановки действий")


@bot.message_handler(commands=['cancel'])
@check_permission
async def cancel(message):
    await controller.update_state(chat_id=message.chat.id, number=1)
    await bot.send_message(message.chat.id, "Все действия отменены.")


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
        # adding reservations
        k = len(state["data"])
        if k == 0:
            # description
            state["data"]["description"] = message.text
            await bot.send_message(message.chat.id, "Введите тип комнаты (лекционная, практическая, переговорная):")
        elif k == 1:
            # type room
            if message.text.lower() in RoomTypes:
                state["data"]["type_room"] = message.text.lower()
                await bot.send_message(message.chat.id, "Введите дату в формате 18.05")
            else:
                await bot.send_message(message.chat.id, "Тип комнаты введен неверно, попробуйте ещё раз")

        elif k == 2:
            # date
            try:
                text = message.text
                day, month = map(int, text.split('.'))
                if 1 <= month <= 12 and 1 <= day <= 31:
                    year = str(datetime.date.today().year)
                    date = year + "-" + str(month) + "-" + str(day)
                    state["data"]["date"] = date
                    await bot.send_message(message.chat.id, "Введите время начала в формате: 8:30")
                else:
                    await bot.send_message(message.chat.id, "Дата введена неверно, попробуйте ещё раз")
            except:
                await bot.send_message(message.chat.id, "Дата введена неверно, попробуйте ещё раз")
        elif k == 3:
            # time_start
            try:
                text = message.text
                hour, minute = map(int, text.split(':'))
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    state["data"]["time_start"] = message.text
                    await bot.send_message(message.chat.id, "Введите время окончания в формате: 8:30")
                else:
                    await bot.send_message(message.chat.id, "Время начала введено неверно, попробуйте ещё раз")
            except:
                await bot.send_message(message.chat.id, "Время начала введено неверно, попробуйте ещё раз")
        elif k == 4:
            # time_end
            try:
                text = message.text
                hour, minute = map(int, text.split(':'))
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    state["data"]["time_end"] = message.text
                    free_rooms = await controller.get_free_rooms(date=state["data"]["date"],
                                                                 time_start=state["data"]["time_start"],
                                                                 time_end=state["data"]["time_end"],
                                                                 type_room=state["data"]["type_room"])
                    if len(free_rooms) == 0:
                        await bot.send_message(message.chat.id, "Свободных аудиторий нет, "
                                                                "попробуйте выбрать другое время.")
                        await controller.update_state(chat_id=message.chat.id, number=1)
                        return
                    rooms_id = []
                    text = "Свободные аудтории на это время:\n\n"
                    for room in free_rooms:
                        rooms_id.append(room.id)
                        text += "id: " + str(room.id) + "\n"
                        text += "номер: " + room.number + "\n"
                        text += "тип аудитории: " + room.type_class + "\n"
                        text += "посадочные места: " + str(room.places) + "\n"
                        text += "компьютерные места: " + str(room.computer_places) + "\n"
                        text += "мультимедиа: " + str(room.multimedia) + "\n"
                        text += "описание: " + room.description + "\n\n"
                    state["data"]["rooms_id"] = rooms_id
                    await bot.send_message(message.chat.id, text)
                    await bot.send_message(message.chat.id, "Выберите аудиторию и напишите ее id")
                else:
                    await bot.send_message(message.chat.id, "Время окончания введено неверно, попробуйте ещё раз")
            except:
                await bot.send_message(message.chat.id, "Время окончания введено неверно, попробуйте ещё раз")

        elif k > 4:
            # id room
            if message.text.isdigit():
                id = int(message.text)
                if id in state["data"]["rooms_id"]:
                    await controller.add_reservation(date=state["data"]["date"],
                                                     time_start=state["data"]["time_start"],
                                                     time_end=state["data"]["time_end"],
                                                     description=state["data"]["description"],
                                                     owner=message.chat.id,
                                                     class_id=id)
                    await bot.send_message(message.chat.id, "Ваша бронь успешно зарегистрирована.")
                else:
                    await bot.send_message(message.chat.id, "Такого id нет.")
            else:
                await bot.send_message(message.chat.id, "id должен быть числом.")
        await controller.update_state(chat_id=message.chat.id, number=2, data=state["data"])
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
