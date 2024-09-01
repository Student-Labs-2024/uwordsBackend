FROM python:3.11.9-slim

WORKDIR /backend

COPY requirements.txt .

RUN apt-get -y update && apt-get -y upgrade && apt-get install -y ffmpeg --fix-missing 

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt 
RUN pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu126

COPY . .