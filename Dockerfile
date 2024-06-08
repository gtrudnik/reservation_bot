FROM python:3.11 as builder

RUN mkdir app/

WORKDIR /app

# load poetry and build venv via poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 -
ADD pyproject.toml /app
ENV PATH=/opt/poetry/bin:$PATH
RUN poetry config virtualenvs.in-project true && poetry install

ADD ReservationBot /app/ReservationBot

FROM python:3.11-slim-bookworm

EXPOSE 8080
COPY --from=builder /app /app
WORKDIR /app
ENTRYPOINT [ "/app/.venv/bin/python", "-m", "uvicorn", "ReservationBot.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1" ]
