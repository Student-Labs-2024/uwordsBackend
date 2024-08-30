import logging


def setup_logger(
    name: str, level: int = logging.INFO, file: str = None
) -> logging.Logger:
    logger = logging.getLogger(name)
    
    if logger.hasHandlers():
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if file:
        fh = logging.FileHandler(file)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


scheduled_tasks_logger = setup_logger("[CELERY SCHEDULED WORDS]", logging.INFO)
celery_tasks_logger = setup_logger("[CELERY TASKS WORDS]", logging.INFO)
admin_router_logger = setup_logger("[ROUTER ADMIN]", logging.INFO)
auth_router_logger = setup_logger("[ROUTER AUTH]", logging.INFO)
topic_router_logger = setup_logger("[ROUTER TOPIC]", logging.INFO)
words_router_logger = setup_logger("[ROUTER WORDS]", logging.INFO)
audio_service_logger = setup_logger("[SERVICES AUDIO]", logging.INFO)
user_service_logger = setup_logger("[SERVICES USER]", logging.INFO)
image_service_logger = setup_logger("[SERVICES IMAGE]", logging.INFO)
censore_service_logger = setup_logger("[SERVICES CENSORE]", logging.INFO)
file_service_logger = setup_logger("[SERVICES FILE]", logging.INFO)
minio_service_logger = setup_logger("[SERVICES MINIO]", logging.INFO)
text_service_logger = setup_logger("[SERVICES TEXT]", logging.INFO)
topic_service_logger = setup_logger("[SERVICES TOPICS]", logging.INFO)
user_service_logger = setup_logger("[SERVICES USER]", logging.INFO)
user_word_service_logger = setup_logger("[SERVICES WORDS]", logging.INFO)
user_word_stop_list_service_logger = setup_logger(
    "[SERVICES USER WORD STOP LIST]", logging.INFO
)
word_service_logger = setup_logger("[SERVICES WORDS]", logging.INFO)
auth_utils_logger = setup_logger("[AUTH UTILS]", logging.INFO)
helpers_utils_logger = setup_logger("[HELPERS UTILS]", logging.INFO)
metric_utils_logger = setup_logger("[METRIC UTILS]", logging.INFO)
achievement_router_logger = setup_logger("[ACHIEVEMENT ROUTER]", logging.INFO)
