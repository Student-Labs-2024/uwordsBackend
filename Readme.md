# UWORDS FASTAPI


Чтобы сделать миграцию к БД, нужно прописать в контейнере docker следующую команду
```shell
alembic -c src/alembic.ini revision --autogenerate -m "комментарий для миграции"
```

Применить миграции
```shell
alembic -c src/alembic.ini upgrade head
```

Запуск проекта на локальной машине
```shell
docker-compose -f "docker-compose.dev.yml" up --build
```