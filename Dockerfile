FROM python:3.11-slim

WORKDIR /backend

COPY requirements.txt .

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg --fix-missing

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY . .