#!/bin/bash

# Остановить контейнера
sudo docker-compose stop

# Подгрузить новые изменения
git pull

# Поднять контейнера
sudo docker-compose build
sudo docker-compose up -d
sudo docker-compose exec app alembic -c src/alembic.ini revision --autogenerate
sudo docker-compose exec app alembic -c src/alembic.ini upgrade head
sudo systemctl restart nginx.service