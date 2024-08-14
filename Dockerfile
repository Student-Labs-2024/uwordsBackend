FROM python:3.11-slim

WORKDIR /backend

COPY requirements.txt .

RUN apt-get -y update && apt-get -y upgrade && apt-get install -y ffmpeg --fix-missing && pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY . .
