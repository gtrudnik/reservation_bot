from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Creates basic application settings"""

    app_name: str = "TokenBot"
    db_driver: str = "postgresql+asyncpg"
    postgres_user: str = os.getenv('POSTGRES_USER')
    postgres_password: str = os.getenv('POSTGRES_PASSWORD')
    postgres_host: str = os.getenv('POSTGRES_HOST')
    postgres_port: str = os.getenv('POSTGRES_PORT')
    postgres_db: str = os.getenv('POSTGRES_DB')
    tokenbot_url: str = "localhost"
    token: str = os.getenv('TOKEN')
    start_text: str = ("Добрый день! Для получения доступа к сервису необходимо ввести токен "
                       "или попросить администратора выдать вам доступ.")
    list_commands: str = ("/help - список всех комнад\n/save - обновить информацию о вашем аккаунте"
                          "\n/new_reservation - забронировать аудиторию"
                          "\n/list_reservations - получить список своих активных броней"
                          "\n/delete_reservation - удалить бронь"
                          "\n/cancel - отменить все действия")


settings = Settings()
