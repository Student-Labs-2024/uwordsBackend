# UWORDS
Кросплатформенное приложение для изучения языков

## Особенности
- Онбординг: Введение в приложение для новых пользователей

- Система обучения: Различные упраженения для изучения слов.

- Анализ аудио: Возможность составить список слов для изучения на основе любой записи, предоставленной пользователем.

- Авторизация: Авторизация через Google и vk/почту

- Личный кабинет: Удобный интерфейс для получения статистики по изученным словам.

- Геймификация: Разнообразные достижения за прогресс пользователя.

- Система подписки: Безопасная оплата заказов через встроенные платежные системы.

## Stack
Python 3.11, FastAPI, PostgreSQL, Celery, Redis, gunicorn, Docker

## Packages
asyncpg, alembic, yt-dlp, librosa, speech_recognition, gTTS, requests, minio, pymorphy3, chromadb, nltk, pydub

## Запуск проекта
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

Настройка локального окружения pre-commit:
```shell
pre-commit install
pre-commit run --all-files
pre-commit install --hook-type commit-msg
```

Пример .env можно увидеть в следующих файлах:
- env.dev.example
- env.dev.db.example

## Authors
Daniil Kolevatykh - CTO, python software developer

Azamat Aubakirov - python software developer

Dmitry Prasolov - python software developer
