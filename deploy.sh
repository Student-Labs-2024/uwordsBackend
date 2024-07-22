#!/bin/bash

# Остановить контейнера
sudo docker-compose stop

# Подгрузить новые изменения
git pull

# Поднять контейнера
sudo docker-compose build
sudo docker-compose up -d
sudo systemctl restart nginx.service