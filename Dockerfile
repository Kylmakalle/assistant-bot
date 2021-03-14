FROM python:3.9.2-slim

RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /usr/src/bot

ENTRYPOINT ["python3", "bot.py"]
