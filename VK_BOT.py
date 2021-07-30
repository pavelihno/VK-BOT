import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from weather import *
from schedule import *
from CONSTANTS import *

keyboard_menu = VkKeyboard(one_time=True)   #клавиатура меню
keyboard_menu.add_button(MESSAGE_SCHEDULE, color=VkKeyboardColor.NEGATIVE)
keyboard_menu.add_line() 
keyboard_menu.add_button(MESSAGE_WEATHER, color=VkKeyboardColor.POSITIVE)

keyboard_schedule = VkKeyboard(one_time=True)   #клавиатура расписание
keyboard_schedule.add_button(MESSAGE_SCHEDULE_TODAY, color=VkKeyboardColor.POSITIVE)
keyboard_schedule.add_button(MESSAGE_SCHEDULE_TOMORROW, color=VkKeyboardColor.NEGATIVE)
keyboard_schedule.add_line()
keyboard_schedule.add_button(MESSAGE_SCHEDULE_WEEK_СURRENT, color=VkKeyboardColor.PRIMARY)
keyboard_schedule.add_button(MESSAGE_SCHEDULE_WEEK_NEXT, color=VkKeyboardColor.PRIMARY)
keyboard_schedule.add_line()
keyboard_schedule.add_button(MESSAGE_SCHEDULE_WEEK, color=VkKeyboardColor.SECONDARY)
keyboard_schedule.add_button(MESSAGE_SCHEDULE_GROUP, color=VkKeyboardColor.SECONDARY)

keyboard_weather = VkKeyboard(one_time=True)    #клавиатура погода
keyboard_weather.add_button(MESSAGE_WEATHER_NOW, color=VkKeyboardColor.PRIMARY)
keyboard_weather.add_button(MESSAGE_WEATHER_TODAY, color=VkKeyboardColor.POSITIVE)
keyboard_weather.add_button(MESSAGE_WEATHER_TOMORROW, color=VkKeyboardColor.POSITIVE)
keyboard_weather.add_line()
keyboard_weather.add_button(MESSAGE_WEATHER_WEEK, color=VkKeyboardColor.POSITIVE)

def main():
    #вход ВК
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    upload = VkUpload(vk_session)
    group_dict = {}     #словарь пользователь-группа
    show_weather = {}   #словарь пользователь-погода
    show_schedule = {}  #словарь пользователь-расписание
    #чтение сообщений
    for event in longpoll.listen(): 
        if event.type == VkEventType.MESSAGE_NEW and event.text and event.to_me:
            text = event.text.lower()
            user = event.user_id
            current_week = get_current_week_num()
            if user in group_dict:
                group = group_dict[user]
            if not user in show_weather:
                show_weather[user] = False
            if not user in show_schedule:
                show_schedule[user] = False
            if text in ["начать", "привет", "бот"]: #приветствие
                message = MESSAGE_GREETING + str(vk.users.get(user_id = user)[0]['first_name']) + "!"
                vk.messages.send(user_id=user, message=message, random_id=0)
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=MESSAGE_GREETING_TEXT)
            elif (text in ["расписание занятий", "расписание"] or text in DAYS_WEEK) and not user in group_dict :   #вывод ввода группы
                show_schedule[user] = True
                vk.messages.send(user_id=user, random_id=0, message=MESSAGE_GROUP_WRITE_TEXT)
            elif text in ["расписание занятий", "расписание"]:      #выбор периода расписания
                show_schedule[user] = True
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_schedule.get_keyboard(), message=MESSAGE_GROUP_SHOW_TEXT+group)
            elif re.fullmatch(GROUP_NAME_PATTERN, text.upper()):    #ввод группы
                if not group_exists(text.upper()):
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=MESSAGE_GROUP_NAME_WRONG_TEXT.format(text.upper()))
                    continue
                show_schedule[user] = True
                group = text.upper()
                group_dict[user] = group
                vk.messages.send(user_id=user, random_id=0, message=MESSAGE_GROUP_NAME_SAVED_TEXT+group)
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_schedule.get_keyboard(), message=MESSAGE_GROUP_SHOW_TEXT+group)
            elif text in ["на сегодня"] and show_schedule[user]:    #расписание сегодня
                show_schedule[user] = False
                day_week_num = datetime.datetime.now().weekday()
                day_week = WEEK_DAYS[day_week_num]
                if (current_week == 0):
                    message = MESSAGE_SCHEDULE_SESSION
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                    continue
                if (current_week == -1):
                    message = MESSAGE_SCHEDULE_HOLIDAYS
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                    continue
                if (day_week_num == 6):
                    message = MESSAGE_SCHEDULE_SUNDAY
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                    continue
                schedule_day = create_schedule_day_heading(group, current_week, day_week_num, day_week)
                message = array_to_string(schedule_day)
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
            elif text in ["на завтра"] and show_schedule[user]:     #расписание завтра
                show_schedule[user] = False
                tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
                day_week_num = tomorrow.weekday()
                day_week = WEEK_DAYS[day_week_num]
                if (current_week == 0):
                    message = MESSAGE_SCHEDULE_SESSION
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                    continue
                if (current_week == -1):
                    message = MESSAGE_SCHEDULE_HOLIDAYS
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                    continue
                if (day_week_num == 6):
                    message = MESSAGE_SCHEDULE_SUNDAY
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                    continue
                schedule_day = create_schedule_day_heading(group, current_week, day_week_num, day_week)
                message = array_to_string(schedule_day)
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
            elif text in ["на эту неделю"] and show_schedule[user]: #расписание неделя
                show_schedule[user] = False
                schedule_week = create_schedule_week_heading(group, current_week)
                if (current_week == 0):
                    message = MESSAGE_SCHEDULE_SESSION
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                    continue
                if (current_week == -1):
                    message = MESSAGE_SCHEDULE_HOLIDAYS
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                    continue
                message = array_to_string(schedule_week)
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
            elif text in ["на следующую неделю"] and show_schedule[user]:   #расписание след неделя
                show_schedule[user] = False
                schedule_week = create_schedule_week_heading(group, current_week+1)
                if (current_week == 0):
                    message = MESSAGE_SCHEDULE_SESSION
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                    continue
                if (current_week == -1):
                    message = MESSAGE_SCHEDULE_HOLIDAYS
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                    continue
                message = array_to_string(schedule_week)
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
            elif text in DAYS_WEEK: #расписание на день недели (без указания группы)
                day_week_num = DAYS_WEEK[text]
                if (day_week_num == 6):
                    message = MESSAGE_SCHEDULE_SUNDAY
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                    continue
                if (current_week == 0):
                    message = MESSAGE_SCHEDULE_SESSION
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                    continue
                if (current_week == -1):
                    message = MESSAGE_SCHEDULE_HOLIDAYS
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                    continue
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_schedule.get_keyboard(), message=MESSAGE_GROUP_SHOW_TEXT+group)
                schedule_day = create_schedule_day_heading(group, current_week-1, day_week_num, text)  #предыдущая неделя
                message = array_to_string(schedule_day)
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                schedule_day = create_schedule_day_heading(group, current_week, day_week_num, text)    #текущая неделя
                message = array_to_string(schedule_day)
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
            elif re.fullmatch(GROUP_NAME_DAY_WEEK_PATTERN, text.upper()):   #расписание на день недели (с указанием группы)
                group_temp = text.upper().split(" ")[1]
                day_week = text.split(" ")[0]
                day_week_num = day_week_num = DAYS_WEEK[day_week]
                if (day_week_num == 6):
                    message = MESSAGE_SCHEDULE_SUNDAY
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                    continue
                if not group_exists(group_temp):
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=MESSAGE_GROUP_NAME_WRONG_TEXT.format(group_temp))
                    continue
                if (current_week == 0):
                    message = MESSAGE_SCHEDULE_SESSION
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                    continue
                if (current_week == -1):
                    message = MESSAGE_SCHEDULE_HOLIDAYS
                    vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                    continue
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_schedule.get_keyboard(), message=MESSAGE_GROUP_SHOW_TEXT+group_temp)
                schedule_day = create_schedule_day_heading(group_temp, current_week-1, day_week_num, text.split(" ")[0])  #предыдущая неделя
                message = array_to_string(schedule_day)
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
                schedule_day = create_schedule_day_heading(group_temp, current_week, day_week_num, text.split(" ")[0])    #текущая неделя
                message = array_to_string(schedule_day)
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
            elif text in ["какая неделя?"] and show_schedule[user]: #какая неделя
                show_schedule[user] = False
                if current_week == 0:
                    message = MESSAGE_WEEK_CURRENT_SESSION_TEXT
                elif current_week == -1:
                    message = MESSAGE_WEEK_CURRENT_HOLIDAYS_TEXT
                else:
                    message = MESSAGE_WEEK_CURRENT_TEXT.format(current_week)
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=message)
            elif text in ["какая группа?"] and show_schedule[user]: #какая группа
                show_schedule[user] = False
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=MESSAGE_GROUP_SHOW_TEXT+group)
            elif text in ["погода", "погода в москве"] and not show_weather[user]:   #вывод выбора периода погоды
                show_weather[user] = True
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_weather.get_keyboard(), message=MESSAGE_WEATHER)
            elif text in ["сейчас"] and show_weather: #погода сейчас
                show_weather[user] = False 
                create_weather_current_png()
                photo_name = "cache\weather_current.png"
                photo_path = os.path.join(dirpath, photo_name)
                photo = upload.photo_messages(photo_path)
                attachment = f"photo{photo[0]['owner_id']}_{photo[0]['id']}"
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), attachment=attachment)
            elif text in ["на сегодня"] and show_weather: #погода сегодня
                show_weather[user] = False
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=MESSAGE_UNAVALAIBLE_COMMAND)
            elif text in ["на завтра"] and show_weather:  #погода завтра
                show_weather[user] = False
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=MESSAGE_UNAVALAIBLE_COMMAND)
            elif text in ["на 5 дней"] and show_weather:  #погода 5 дней
                show_weather[user] = False
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=MESSAGE_UNAVALAIBLE_COMMAND)
            else:   #неизвестная команда
                vk.messages.send(user_id=user, random_id=0, keyboard=keyboard_menu.get_keyboard(), message=MESSAGE_UNKNOWN_COMMAND)


if __name__ == "__main__":
    main()


