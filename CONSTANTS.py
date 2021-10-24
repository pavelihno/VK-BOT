OPEN_WEATHER_CURRENT = "http://api.openweathermap.org/data/2.5/weather?q=moscow&appid={}&lang=ru&units=metric"
OPEN_WEATHER_5DAYS = "https://api.openweathermap.org/data/2.5/forecast?q=moscow&appid={}&lang=ru&units=metric"
OPEN_WEATHER_ICON = "http://openweathermap.org/img/w/"

GROUP_NAME_PATTERN = r"И[А-Я]БО-\d{2}-\d{2}"
GROUP_NAME_DAY_WEEK_PATTERN = r"\w+ И[А-Я]БО-\d{2}-\d{2}"
COMMA_INCLUDE = r"\d+,.+"
COMMA_EXCLUDE = r"кр.+\d+,.+"
DASH_INCLUDE = r"\d+-\d+"
DASH_EXCLUDE = r"кр.+\d+-\d+"
MESSAGE_GREETING = "Приветствую, "
MESSAGE_GREETING_TEXT = "Предлагаю ознакомиться с моим функционалом:\n1) Расписание занятий\n   ·Напишите номер своей группы, чтобы я его запомнил\n   ·Напишите 'день недели' 'номер группы'\
, чтобы получить расписание на этот день\n   ·Напишите 'день недели', чтобы получить расписание своей группы на этот день\n2) Погода в Москве"
MESSAGE_MENU_TEXT = "Мой функционал: "

MESSAGE_GROUP_SHOW_TEXT = "Показываю расписание группы "
MESSAGE_GROUP_WRITE_TEXT = "Напиши номер своей группы в формате: ИХБО-ХХ-ХХ"
MESSAGE_GROUP_NAME_SAVED_TEXT = "Я запомнил, что ты из группы "
MESSAGE_GROUP_NAME_WRONG_TEXT = "Группа {} не существует"
MESSAGE_WEEK_CURRENT_TEXT = "Идет {} неделя"
MESSAGE_WEEK_CURRENT_SESSION_TEXT = "Идет экзаменационная сессия"
MESSAGE_WEEK_CURRENT_HOLIDAYS_TEXT = "Идут каникулы"

MESSAGE_SCHEDULE = "Расписание занятий "
MESSAGE_SCHEDULE_WEEK = "какая неделя?"
MESSAGE_SCHEDULE_GROUP = "какая группа?"
MESSAGE_SCHEDULE_TODAY = "на сегодня"
MESSAGE_SCHEDULE_TOMORROW = "на завтра"
MESSAGE_SCHEDULE_WEEK_СURRENT = "на эту неделю"
MESSAGE_SCHEDULE_WEEK_NEXT = "на следующую неделю"

MESSAGE_SCHEDULE_SUNDAY = "Воскресенье день для Бога!"
MESSAGE_SCHEDULE_HOLIDAYS = "КАНИКУЛЫ! Отдыхай!"
MESSAGE_SCHEDULE_SESSION = "ЭКЗАМЕНЫ! Не забывай готовиться!"

MESSAGE_WEATHER = "Погода в Москве "
MESSAGE_WEATHER_TODAY = "на сегодня"
MESSAGE_WEATHER_TOMORROW = "на завтра"
MESSAGE_WEATHER_WEEK = "на 5 дней"
MESSAGE_WEATHER_NOW = "сейчас"


MESSAGE_WEATHER_TODAY_TEXT = "Погода на сегодня"
MESSAGE_WEATHER_TOMORROW_TEXT = "Погода на завтра"
MESSAGE_WEATHER_WEEK_TEXT = "Погода на 5 дней"
MESSAGE_WEATHER_NOW_TEXT = "Погода сейчас"

MESSAGE_UNAVALAIBLE_COMMAND = "Команда временно недоступна"
MESSAGE_UNKNOWN_COMMAND = "Неизвестная команда"

DAYS_WEEK = {"понедельник": 0, "вторник": 1, "среда": 2, "четверг": 3, "пятница": 4, "суббота": 5, "воскресенье": 6}
WEEK_DAYS = {0: "понедельник", 1: "вторник", 2: "среда", 3: "четверг", 4: "пятница", 5: "суббота", 6: "воскресенье"} 