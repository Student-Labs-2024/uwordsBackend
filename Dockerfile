FROM python:3.11.9-slim

WORKDIR /backend

COPY requirements.txt .

RUN apt-get -y update && apt-get -y upgrade && apt-get install -y ffmpeg --fix-missing && pip3 install --upgrade pip && pip3 install -r requirements.txt && pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

COPY . .
