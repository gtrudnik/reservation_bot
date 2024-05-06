from telebot.async_telebot import AsyncTeleBot
from ReservationBot.config import settings
from ReservationBot.db.controller import controller
bot = AsyncTeleBot(settings.token)


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
async def new_reservation(message):
    """ Function for create new reservation """


@bot.message_handler(commands=['list_reservations'])
async def list_reservations(message):
    """ Function for get list reservations """


@bot.message_handler(commands=['delete_reservation'])
async def new_reservation(message):
    """ Function for delete reservation """


async def start_bot():
    await bot.infinity_polling()
