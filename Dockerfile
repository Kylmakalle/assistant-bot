FROM python:3.7.1-stretch

RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot
ADD . /usr/src/bot

RUN pip install -r requirements.txt
