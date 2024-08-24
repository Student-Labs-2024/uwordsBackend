USER_REGISTER_TITLE = """\
Регистрация пользователя (собственная аутентификация)\
"""

USER_REGISTER_DESCRIPTION = """\
Метод, отвечающий за регистрацию пользователя через собственную аутентификацию. \
Перед регистрацией нужно запросить код (метод ниже). Все поля обязательны для заполения\
"""

USER_REGISTER_VK_TITLE = """\
Регистрация пользователя через ВКонтакте\
"""

USER_REGISTER_VK_DESCRIPTION = """\
Метод, отвечающий за регистрацию пользователя через провайдера ВКонтакте. \
Нужно в заголовоках передавать ключ доступа, который генирирует сам ВКонтакте, \
а также два обязательных поля в теле запроса: имя и фамилию, которые передаёт сам ВК\
"""

USER_REGISTER_GOOGLE_TITLE = """\
Регистрация пользователя через Google\
"""

USER_REGISTER_GOOGLE_DESCRIPTION = """\
Метод, отвечающий за регистрацию пользователя через провайдера Google. \
В теле запроса передается google_id\
"""

USER_LOGIN_TITLE = """\
Вход в аккаунт (собственная аутентификация)\
"""

USER_LOGIN_DESCRIPTION = """\
Метод, отвечающий за вход в приложение через собственную аутентификацию. \
В теле нужно передать почту и пароль. На выходе получается JWT ACCESS токен \
(нужный для доступа к системе) и JWT REFRESH токен (нужный для обновления ACCESS)\
"""

USER_LOGIN_VK_TITLE = """\
Вход в аккаунт (через ВКонтакте)\
"""

USER_LOGIN_GOOGLE_TITLE = """\
Вход в аккаунт (через Google)\
"""

USER_LOGIN_VK_DESCRIPTION = """\
Метод, отвечающий за вход в приложение через провайдера ВК. \
В заголовка нужно передавать ключ доступа, который генирирует сам ВКонтакте. \
На выходе получается JWT ACCESS токен (нужный для доступа к системе) \
и JWT REFRESH токен (нужный для обновления ACCESS)\
"""

USER_LOGIN_GOOGLE_DESCRIPTION = """\
Метод, отвечающий за вход в приложение через провайдера Google. \
В теле запроса нужно передавать uid от firebase. \
На выходе получается JWT ACCESS токен (нужный для доступа к системе) \
и JWT REFRESH токен (нужный для обновления ACCESS)\
"""

TOKEN_REFRESH_TITLE = """\
Обновление ACCESS токена\
"""

TOKEN_REFRESH_DESCRIPTION = """\
Метод для обновления ACCESS токена с помощью REFRESH токена \
(передавать в заголовках запроса). На выходе получается новый JWT ACCESS токен\
"""

USER_ME_TITLE = """\
Информация о "себе"\
"""

USER_ME_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для получения информации о "себе" (профиль)\
"""

USER_ME_UPDATE_TITLE = """\
Обновить информацию о "себе"
"""

USER_ME_UPDATE_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для обновления информации о "себе" (профиль)\
"""

USER_ME_DELETE_TITLE = """\
Удалить "свой" аккаунт
"""

USER_ME_DELETE_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для удаления "своего" аккаунта\
"""

USER_PROFILE_TITLE = """\
Получение профиля пользователя по его ID\
"""

USER_PROFILE_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для получения профиля \
(общедоступной информации) пользователя по его ID\
"""

ADMIN_REGISTER_TITLE = """\
Создание администратора\
"""

ADMIN_REGISTER_DESCRIPTION = """
Алгоритм регистрации админ пользователя схож с \
обычным, но дополнительно нужно передать секретный ключ\
"""

ADMIN_LOGIN_TITLE = """\
Вход в аккаунт администратора\
"""

ADMIN_LOGIN_DESCRIPTION = """\
Алгоримт авторизации схож с обычным пользователем\
"""

USER_BAN_TITLE = """\
Заблокировать пользователя\
"""

USER_BAN_DESCRIPTION = """
Нужен админ-доступ. Метод закрывающий \
пользователю доступ к системе (с возможностью восстановления)\
"""

USER_DELETE_TITLE = """\
Удалить аккаунт (профиль) пользователя\
"""

USER_DELETE_DESCRIPTION = """\
Нужен админ-доступ. Метод, полностью удаляющий аккаунт (профиль) пользователя\
"""

USER_RESET_TITLE = """\
Сбросить лимиты пользователя\
"""

USER_RESET_DESCRIPTION = """\
Нужен админ-доступ. Метод, сбрасывающий все лимиты пользователя на загрузку контента и энергию\
"""

SEND_CODE_TITLE = """\
Отправить код на почту
"""

SEND_CODE_DESCRIPTION = """\
Данный метод отправляет код подтверждения, нужный для регистрации \
не через внешних провайдеров, на указанную почту\
"""

GET_TELEGRAM_LINK_TITLE = """\
Получить ссылку на бота
"""

GET_TELEGRAM_LINK_DESCRIPTION = """\
Данный метод генерирует код подтверждения и выдаёт ссылку для перехода в ТГ \
для связи бота с приложением
"""

CHECK_CODE_TITLE = """\
Проверить код\
"""

CHECK_CODE_DESCRIPTION = """\
DEBUG-метод, проверяющий код подтверждения для указанной почты.\
"""

TOPIC_ADD_TITLE = """\
Добавить топик\
"""

TOPIC_ADD_DESCRIPTION = """\
Нужен админ-доступ. Метод для добавления новой категории для слов\
"""

SUBTOPIC_ADD_TITLE = """\
Добавить подтопик\
"""

SUBTOPIC_ADD_DESCRIPTION = """\
Нужен админ-доступ. Метод для добавления новой подкатегории слов. \
Добавление также идёт и в chromadb, для дальнейшей индексации слов\
"""

SUBTOPIC_ADD_ICON_TITLE = """\
Добавить иконку к подтопику\
"""

SUBTOPIC_ADD_ICON_DESCRIPTION = """\
Нужен админ-доступ. Метод для добавления / обновления иконки подкатегории.\
"""

TOPIC_GET_TITLE = """\
Получить топик\
"""

TOPIC_GET_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для получения информации \
о конкретной категории\
"""

SUBTOPIC_GET_TITLE = """\
Получить подтопик\
"""

SUBTOPIC_GET_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для получения информации \
о конкретной подкатегории\
"""

TOPIC_ALL_TITLE = """\
Получить все топики\
"""

TOPIC_ALL_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для получения списка всех категорий\
"""

SUBTOPIC_ALL_TITLE = """\
Получить все подтопики\
"""

SUBTOPIC_ALL_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для получения списка всех подкатегорий\
"""

SUBTOPIC_ALL_TOPIC_TITLE = """\
Получить все подтопики топику\
"""

SUBTOPIC_ALL_TOPIC_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для получения списка всех подкатегорий, \
входящих в определённую категорию\
"""

SUBTOPIC_CHECK_TITLE = """\
Получить подтопик по слову\
"""

SUBTOPIC_CHECK_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для определения подкатегории конкретного слова\
"""

TOPIC_DELETE_TITLE = """\
Удалить топик\
"""

TOPIC_DELETE_DESCRIPTION = """\
Нужен админ-доступ. Метод для удаления категории.\
"""

SUBTOPIC_DELETE_TITLE = """\
Удалить подтопик\
"""

SUBTOPIC_DELETE_DESCRIPTION = """\
Нужен админ-доступ. Метод для удаления подкатегории. Также подкатегория удаляется \
и из коллекции chromadb\
"""

USER_TOPICS_GET_TITLE = """\
Получить топики пользователя\
"""

USER_TOPICS_GET_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для получения всех категорий \
пользователя с подкатегориями отсортированных по прогрессу, употреблению\
"""

USER_TOPICS_GET_SUBTOPIC_WORDS_TITLE = """\
Получить слова из подкатегории пользователя\
"""

USER_TOPICS_GET_SUBTOPIC_WORDS_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для получения слов из подкатегории\
пользователя отсортированных по прогрессу, употреблению\
"""

USER_WORDS_GET_TITLE = """\
Получить слова пользователя\
"""

USER_WORDS_GET_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для получения всех слов \
пользователя, ранжированных по категориями, подкатегориям и \
отсортированных по прогрессу, употреблению\
"""

USER_WORDS_GET_STUDY_TITLE = """\
Получить подборку для изучения\
"""

USER_WORDS_GET_STUDY_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для получения подборки списка слов \
пользователя для системы изучения. Может выбрать слова как из всего топика, \
так и из конкретного подтопика\
"""

USER_WORDS_POST_STUDY_TITLE = """\
Закончить изучение\
"""

USER_WORDS_POST_STUDY_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для регистрации прогресса \
пользователя по словам, предложенным для изучения\
"""

UPLOAD_AUDIO_TITLE = """\
Загрузить аудио\
"""

UPLOAD_AUDIO_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для загрузки аудиозаписи \
в каталог пользователя для дальнейшей его обработки, перевода слов и \
формированию личного словаря пользователя\
"""

UPLOAD_YOUTUBE_TITLE = """\
Загрузить видео с YouTube\
"""

UPLOAD_YOUTUBE_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для загрузки видео с YouTube \
по ссылке в каталог пользователя для дальнейшей его обработки, перевода \
слов и формированию личного словаря пользователя\
"""

UPLOAD_BOT_WORDS_TITLE = """\
Загрузить слова из бота\
"""

UPLOAD_BOT_WORDS_DESCRIPTION = """\
Нужна авторизация (SERVICE токен). Метод для загрузки слов из бота \
для их дальнейшей обработки, перевода слов и формированию личного \
словаря пользователя\
"""


DELETE_USER_WORD_TITLE = """\
Удалить слово из пользовательского словаря\
"""

DELETE_USER_WORD_DESCRIPTION = """\
Нужна авторизация (ACCESS токен). Метод для удаления слова из личного \
словаря пользователя и добавления слова в стоп лист на месяц\
"""

ERROR_CREATE_TITLE = """\
Запустить тестовую ошибку\
"""

ERROR_CREATE_DESCRIPTION = """\
DEBUG-метод для создания отчёта по ошибке и её отправки по вебсокету\
"""

FEEDBACK_TITLE = """\
Создать пользовательский отзыв\
"""

FEEDBACK_DESCRIPTION = """\
Пользователь может оставить свой отзыв о приложении и поставить оценку (от 1 до 5 звезд)\
"""

FEEDBACK_UPDATE_TITLE = """\
Обновить пользовательский отзыв\
"""

FEEDBACK_UPDATE_DESCRIPTION = """\
Пользователь может обновить свой отзыв о приложении, если он существует\
"""

SENTRY_TITLE = """\
Запустить тестовую ошибку в Sentry\
"""

SENTRY_DESCRIPTION = """\
DEBUG-метод для документирования ошибки в Sentry\
"""

SUB_ADD_TITLE = """\
Добавить тариф\
"""

SUB_ADD_DESCRIPTION = """\
Метод для добавления тарифа\
"""

SUB_GET_ALL_TITLE = """\
Получить список тарифов\
"""

SUB_GET_ALL_DESCRIPTION = """\
Метод для получения списка тарифов\
"""

SUB_GET_TITLE = """\
Получить тариф\
"""

SUB_GET_DESCRIPTION = """\
Метод для получения подписки\
"""

SUB_DELETE_TITLE = """\
Удалить тариф\
"""

SUB_DELETE_DESCRIPTION = """\
Метод для удаления тарифа\
"""

SUB_UPDATE_TITLE = """\
Обновить тариф\
"""

SUB_UPDATE_DESCRIPTION = """\
Метод для обновления тарифа\
"""

FORM_PAYMENT_TITLE = """\
Получить ссылку на оплату\
"""

FORM_PAYMENT_DESCRIPTION = """\
Метод для получения ссылки оплаты\
"""

CHECK_PAYMENT_TITLE = """\
Проверить статус платежа\
"""

CHECK_PAYMENT_DESCRIPTION = """\
Метод для проверки статуса платежа\
"""

BILL_GET_TITLE = """\
Получить чек\
"""

BILL_GET_DESCRIPTION = """\
Метод для получения чека по id\
"""

BILL_ALL_TITLE = """\
Получить все чеки\
"""

BILL_ALL_DESCRIPTION = """\
Метод для получения всех чеков\
"""

ACHIEVEMENT_ADD_TITLE = """\
Создать достижение\
"""

ACHIEVEMENT_ADD_DESCRIPTION = """\
Создайте достижения для пользователей\
"""

ACHIEVEMENT_GET_TITLE = """\
Получить достижение\
"""

ACHIEVEMENT_GET_DESCRIPTION = """\
Получить существующее достижение по его id\
"""

ACHIEVEMENT_GET_ALL_TITLE = """\
Получить все достижения\
"""

ACHIEVEMENT_GET_ALL_DESCRIPTION = """\
Получить все существующие достижения\
"""

ACHIEVEMENT_DELETE_TITLE = """\
Удалить достижение\
"""

ACHIEVEMENT_DELETE_DESCRIPTION = """\
Удалить достижение по его id\
"""

ACHIEVEMENT_UPDATE_TITLE = """\
Обновить достижение\
"""

ACHIEVEMENT_UPDATE_DESCRIPTION = """\
Обновить достижение по его id\
"""

ONBOARDING_UPDATE_TITLE = """\
Обновить данные пользователя по онбордингу\
"""

ONBOARDING_UPDATE_DESCRIPTION = """\
Обновить данные о том, что пользователь прошёл онбординг\
"""

TAGS_METADATA = [
    {
        "name": "Users",
        "description": "Операции с пользователями",
    },
    {
        "name": "Email",
        "description": "Операции с почтовым клиентом",
    },
    {
        "name": "User Words",
        "description": "Операции со словами пользователя",
    },
    {
        "name": "Admins",
        "description": "Операции с админ-пользователями",
    },
    {
        "name": "Topic",
        "description": "Операции с категориями / подкатегориями",
    },
    {
        "name": "Errors",
        "description": "Операции с обработкой ошибок, не входящих в АПИ представления",
    },
]
