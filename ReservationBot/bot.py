import datetime

from telebot.async_telebot import AsyncTeleBot
from telebot import types
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


def add_buttons(text_buttons: list[str]):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for text in text_buttons:
        keyboard.add(types.KeyboardButton(text))
    return keyboard


menu_text = ["Забронировать аудиторию", "Список броней", "Удалить бронь"]
menu_buttons = add_buttons(menu_text)
date_buttons_text = ["сегодня", "завтра"]
date_buttons = add_buttons(date_buttons_text)


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
    await bot.send_message(message.chat.id, settings.list_commands, reply_markup=menu_buttons)


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
    reserv_id = []
    if len(reservations) == 0:
        await bot.send_message(message.chat.id, "У вас нет активных броней аудитории.")
    else:
        text_message = "Список ваших активных броней:\n\n"
        for reservation in reservations:
            reserv_id.append(str(reservation.id))
            date = ".".join(str(reservation.date).split("-")[::-1])
            text_message += "ID: " + str(reservation.id) + "\n"
            text_message += "Дата: " + date + "\n"
            text_message += "Время начала: " + str(reservation.time_start)[:-3] + "\n"
            text_message += "Время окончания: " + str(reservation.time_end)[:-3] + "\n"
            room = await controller.get_room(reservation.class_id)
            text_message += "Номер аудитории: " + str(room.number) + "\n"
            text_message += "Описание: " + str(reservation.description) + "\n\n"
        await bot.send_message(message.chat.id, text_message)
    return reserv_id


@bot.message_handler(commands=['delete_reservation'])
@check_permission
async def delete_reservation(message):
    """ Function for delete reservation """
    reserv_id = await list_reservations(message)
    if len(reserv_id) != 0:
        await controller.update_state(chat_id=message.chat.id, number=3)
        buttons = add_buttons(reserv_id)
        await bot.send_message(message.chat.id,
                               "Выберите бронь для удаления. (id - брони)  /cancel - для остановки действий",
                               reply_markup=buttons)


@bot.message_handler(commands=['cancel'])
@check_permission
async def cancel(message):
    await controller.update_state(chat_id=message.chat.id, number=1)
    await bot.send_message(message.chat.id, "Все действия отменены.", reply_markup=menu_buttons)


@bot.message_handler(content_types=['text'])
async def new_message(message):
    state = await controller.get_state(message.chat.id)
    if state == "User not exist":
        res = await controller.add_user(message.chat.username, message.chat.id)
        if "User already exists":
            await controller.update_state(chat_id=message.chat.id, number=0, data={"attempts": 0})
        await bot.send_message(message.chat.id, "Для получения доступа введите токен, "
                                                "или попросите администратора выдать вам доступ")
    elif state["number"] == 1:
        if message.text == menu_text[0]:
            await new_reservation(message)
        elif message.text == menu_text[1]:
            await list_reservations(message)
        elif message.text == menu_text[2]:
            await delete_reservation(message)
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
            buttons = add_buttons(["лекционная", "практическая", "переговорная"])
            await bot.send_message(message.chat.id,
                                   "Выберите тип комнаты:",
                                   reply_markup=buttons)
        elif k == 1:
            # type room
            if message.text.lower() in ["лекционная", "практическая", "переговорная"]:
                state["data"]["type_room"] = message.text.lower()
                await bot.send_message(message.chat.id, "Введите дату в формате 18.05", reply_markup=date_buttons)
            else:
                await bot.send_message(message.chat.id, "Тип комнаты введен неверно, попробуйте ещё раз")

        elif k == 2:
            # date
            try:
                text = message.text
                if text in date_buttons_text:
                    delta_time = date_buttons_text.index(text)
                    date = datetime.date.today() + datetime.timedelta(days=delta_time)
                    date = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
                    state["data"]["date"] = date
                    await bot.send_message(message.chat.id, "Введите время начала в формате: 8:30")
                else:
                    day, month = map(int, text.split('.'))
                    if 1 <= month <= 12 and 1 <= day <= 31:
                        year = datetime.date.today().year
                        if datetime.date.today() <= datetime.date(year=year, month=month, day=day):
                            date = str(year) + "-" + str(month) + "-" + str(day)
                            state["data"]["date"] = date
                            await bot.send_message(message.chat.id, "Введите время начала в формате: 8:30")
                        else:
                            await bot.send_message(message.chat.id, "Дата введена неверно, "
                                                                    "так как этот день уже прошёл, попробуйте ещё раз")
                    else:
                        await bot.send_message(message.chat.id, "Дата введена неверно, попробуйте ещё раз")
            except:
                await bot.send_message(message.chat.id, "Дата введена неверно, попробуйте ещё раз")
        elif k == 3:
            # time_start
            try:
                text = message.text
                hour, minute = map(int, text.split(':'))
                time_now = datetime.datetime.now()
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    year, month, day = map(int, state["data"]["date"].split('-'))
                    if (datetime.date.today() == datetime.date(year=year, month=month, day=day)
                            and datetime.time(hour=time_now.hour, minute=time_now.minute) >=
                            datetime.time(hour=hour, minute=minute)):
                        await bot.send_message(message.chat.id, "Это время сегодня уже прошло, попробуйте ещё раз")
                        return
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
                    hour_start, minute_start = map(int, state["data"]["time_start"].split(':'))
                    if datetime.time(hour=hour, minute=minute) <= datetime.time(hour=hour_start, minute=minute_start):
                        await bot.send_message(message.chat.id,f"Время окончания должно быть позже чем "
                                                               f"время начала: {state['data']['time_start']}.")
                        return
                    state["data"]["time_end"] = message.text
                    free_rooms = await controller.get_free_rooms(date=state["data"]["date"],
                                                                 time_start=state["data"]["time_start"],
                                                                 time_end=state["data"]["time_end"],
                                                                 type_room=state["data"]["type_room"])
                    if len(free_rooms) == 0:
                        await bot.send_message(message.chat.id, "Свободных аудиторий нет, "
                                                                "попробуйте выбрать другое время.")
                        await controller.update_state(chat_id=message.chat.id, number=1)
                        await info_message(message)
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
                        text += "мультимедиа: " + ("есть" if room.multimedia else "нет") + "\n"
                        text += "описание: " + room.description + "\n\n"
                    state["data"]["rooms_id"] = rooms_id
                    await bot.send_message(message.chat.id, text)
                    buttons = add_buttons([str(i) for i in rooms_id])
                    await bot.send_message(message.chat.id, "Выберите аудиторию и напишите ее id",
                                           reply_markup=buttons)
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
                    await controller.update_state(chat_id=message.chat.id, number=1)
                    await bot.send_message(message.chat.id, "Ваша бронь успешно зарегистрирована.")
                    await info_message(message)
                    return
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
                res = await controller.delete_reservation(id, message.chat.id)
                if res == "Wrong id":
                    await bot.send_message(message.chat.id, "Неверный id")
                else:
                    await bot.send_message(message.chat.id, "Бронь удалена.")
                    await controller.update_state(chat_id=message.chat.id, number=1)
                    await info_message(message)
            except:
                await bot.send_message(message.chat.id, "Такой брони нет.")
        else:
            await bot.send_message(message.chat.id, "id брони должно быть числом.")


async def start_bot():
    await bot.infinity_polling()
