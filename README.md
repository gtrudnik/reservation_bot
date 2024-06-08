# reservation_bot
Educational project in the University. Telegram bot for reserveing rooms.
Technology stack: telebot, sqlalchemy, fastapi.

### Before starting the project you need create .env file with parameteres:
TOKEN,
POSTGRES_USER,
POSTGRES_PASSWORD,
POSTGRES_HOST,
POSTGRES_PORT,
POSTGRES_DB

### Docker:

Create image: ```docker build -t reservationbot .```

Start: ```docker run -p 8081:8080  --env-file .env reservationbot```
