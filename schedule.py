import sys
import os
import shutil
import glob
import requests
import re
import json
from bs4 import BeautifulSoup
import datetime
import xlrd
from PIL import Image, ImageDraw, ImageFont
import locale
from CONSTANTS import *
from config import *

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
dirpath = os.path.dirname(__file__) #текущее расположение файла

def get_current_week_num(): #номер текущей недели
    url = "https://www.mirea.ru"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    result = soup.find("div", class_="mainpage").find("div").find("div").find("div", class_="bonus_cart-title") #строка с номером недели
    return 16
    if "экзаменационная" in result.get_text():  
        return 0  #экзаменационная неделя
    try:
        week_num = int(re.findall(pattern="[0-9]+", string=result.get_text().split(",")[1])[0]) #поиск числа (номера недели) (работает только во время учебы)
        return week_num
    except IndexError:
        return -1 #каникулы

def group_exists(group_name):    #проверка, существует ли группа
    if get_schedule(group_name) == None:
        return False
    else:
        return True

def download_schedule(course):  #скачивание расписания по номеру курса
    url = "https://www.mirea.ru/schedule/"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    elements = soup.find("div", {"id": "tabs"}).find(text=re.compile("Институт информационных технологий", flags=re.I)).\
    findParent("div").findNextSibling("div").find_all("a")
    pattern = r"unknown"
    if (course == 1):
        pattern = r"/ИИТ\S+1к\S+.xlsx"
    elif (course == 2):
        pattern = r"/ИИТ\S+2к\S+.xlsx"
    elif (course == 3):
        pattern = r"/ИИТ\S+3к\S+.xlsx"
    file_name = re.findall(pattern=pattern, string=str(elements))[0][1:]
    for element in elements:
        if file_name in element["href"]:
            url = element["href"]
    filename = "cache\IIT_{}_{}.xlsx".format(course, datetime.date.today().strftime("%d_%m"))
    filepath = os.path.join(dirpath, filename)
    r = requests.get(url, allow_redirects=True)
    open(filepath, 'wb').write(r.content)

def parse_schedule(course):  #запись расписания в json 
    filename = "IIT_{}_{}".format(course, datetime.date.today().strftime("%d_%m"))
    filename_json = "cache\{}.json".format(filename)
    filename_xlsx = "cache\{}.xlsx".format(filename)
    filepath_json = os.path.join(dirpath, filename_json)
    filepath_xlsx = os.path.join(dirpath, filename_xlsx)
    workbook = xlrd.open_workbook(filepath_xlsx)
    sheet = workbook.sheet_by_index(0)
    groups = {} #структура - группа: расписание: четные, нечетные: дни недели: пары
    for col in range(5, sheet.ncols, 5):
        group_name = sheet.cell(1, col).value
        if re.fullmatch(GROUP_NAME_PATTERN, group_name):
            schedule = []   #расписание группы
            odd = []    #нечетная неделя
            even = []   #четная неделя
            for week_day in range(0, 6):
                day = []    #расписание на день
                for row in range(4 + 12*week_day, 15 + 12*week_day, 2): #четная неделя
                    subject = sheet.cell(row, col).value
                    type = sheet.cell(row, col+1).value
                    teacher = sheet.cell(row, col+2).value
                    room = sheet.cell(row, col+3).value
                    if subject == "":
                        subject = "—"
                    day.append([subject, type, teacher, room])
                even.append(day)
                
                day = []    #расписание на день
                for row in range(3 + 12*week_day, 14 + 12*week_day, 2): #нечетная неделя
                    subject = sheet.cell(row, col).value
                    type = sheet.cell(row, col+1).value
                    teacher = sheet.cell(row, col+2).value
                    room = sheet.cell(row, col+3).value
                    if subject == "":
                        subject = "—"
                    day.append([subject, type, teacher, room])
                odd.append(day)
            
            schedule.append(even)
            schedule.append(odd)
            groups[group_name] = schedule
    with open(filepath_json, "w") as f:
        json.dump(groups, f)
    return(groups)

def get_schedule(group_name):   #чтение расписания из json и поиск группы
    group, year = group_name.split("-")[1::]
    year_current = datetime.datetime.now().year % 100
    course = year_current - int(year) + 1 - 1 if datetime.datetime.now().month < 9 else 0     #номер курса
    if course not in [1, 2, 3]:
        return None
    filename = "IIT_{}_".format(course)
    today = datetime.date.today().strftime("%d_%m")
    folder_name = "cache"
    folder_path = os.path.join(dirpath, folder_name)
    with os.scandir(folder_path) as files:
        for file in files:
            if filename in file.name and file.name[-4:] == "xlsx":
                filepath_json = "{}\{}json".format(folder_path, file.name[:-4])
                filepath_xlsx = "{}\{}".format(folder_path, file.name)
                if file.name[6:11] == datetime.date.today().strftime("%d_%m"):
                    with open(filepath_json, "r") as f:
                        groups = json.load(f)
                        try:
                            return groups[group_name]
                        except KeyError:
                            return None #группа не существует
                else:
                    try:
                        os.remove(filepath_json)
                        os.remove(filepath_xlsx)
                    except FileNotFoundError:
                        print("Файлы не не найдены, сейчас они будут скачаны")
        download_schedule(course)
        parse_schedule(course)
        return get_schedule(group_name)

def get_schedule_day(group_name, week_num, week_day_num):   #обработка расписания на день
    day_schedule = []
    day = get_schedule(group_name)[week_num % 2][week_day_num]
    number = 1
    for lesson in day:
        subject = lesson[0].split("\n")
        type = lesson[1].split("\n")
        teacher = lesson[2].split("\n")
        room = lesson[3].split("\n")
        subject_out, type_out, teacher_out, room_out = [], [], [], []    #подготовленные для вывода массивы
        for i in range (len(subject)):
            substr_subject_num = subject[i].split(" н. ")[0]
            substr_subject = subject[i].split(" н. ")[len(subject[i].split(" н. ")) - 1]
            def empty_lesson():     #нет пары   
                try:
                    type[i], teacher[i], room[i] = "—", "—", "—"
                except IndexError:
                    print("Ошибка в таблице с расписанием")
            if substr_subject_num[0].isdigit() and re.fullmatch(pattern=DASH_INCLUDE, string=substr_subject_num):    #номера недель, на которых есть занятия через тире
                week_num_from = int(substr_subject_num.split("-")[0])
                week_num_to = int(substr_subject_num.split("-")[1])
                if (week_num_from > week_num or week_num_to < week_num):
                    substr_subject = "—"
                    empty_lesson() 
            elif substr_subject_num[0].isdigit() and re.fullmatch(pattern=COMMA_INCLUDE, string=substr_subject_num):   #номера недель, на которых есть занятия через запятую
                week_num_include = substr_subject_num.split(",")
                for j in range(len(week_num_include)):
                    week_num_include[j] = int(week_num_include[j])
                if not week_num in week_num_include:
                    substr_subject = "—"
                    empty_lesson()
            elif substr_subject_num[0].isdigit():   #номер недели, на которой есть занятия
                week_num_include = int(substr_subject_num.split(" ")[0])
                if week_num != week_num_include:
                    substr_subject = "—"
                    empty_lesson()
            elif substr_subject_num[0:2] == "кр" and re.fullmatch(pattern=DASH_EXCLUDE, string=substr_subject_num):    #номера недель, на которых нет занятий через тире
                week_num_from = int(substr_subject_num.split(" ")[1].split("-")[0])
                week_num_to = int(substr_subject_num.split(" ")[1].split("-")[1])
                if (week_num_from <= week_num and week_num_to >= week_num):
                    substr_subject = "—"
                    empty_lesson()
            elif substr_subject_num[0:2] == "кр" and re.fullmatch(pattern=COMMA_EXCLUDE, string=substr_subject_num):   #номера недель, на которых нет занятий через запятую
                week_num_exclude = substr_subject_num.split(" ")[1].split(",")
                for j in range(len(week_num_exclude)):
                    week_num_exclude[j] = int(week_num_exclude[j])
                if week_num in week_num_exclude:
                    substr_subject = "—"
                    empty_lesson()
            elif substr_subject_num[0:2] == "кр":   #номер недели, на которой нет занятий
                try:
                    week_num_exclude = int(substr_subject_num.split(" ")[1])
                except IndexError:
                    week_num_exclude = int(substr_subject_num.split(".")[1])
                if week_num == week_num_exclude:
                    substr_subject = "—"
                    empty_lesson()
            subject_out.append(substr_subject)
            try:
                type_out.append(type[i])
                teacher_out.append(teacher[i])
                room_out.append(room[i])
            except IndexError:
                print("Ошибка в таблице с расписанием")
        day_schedule.append([number, subject_out, type_out, teacher_out, room_out])
        number += 1
    return day_schedule

def create_schedule_day(group_name, week_num, week_day_num):    #создание расписания на день
    schedule = get_schedule_day(group_name, week_num, week_day_num)
    array = []
    for lesson in schedule:
        start_index = 0
        while lesson[1][start_index] == "—" and start_index < len(lesson[1]) - 1:
            start_index += 1
        if (lesson[1][start_index] == "—"):
            string = "{}) {}".format(lesson[0], "—")
            array.append(string)
        else:
            string = "{}) {}".format(lesson[0], lesson[1][start_index])
            try:
                string += ", {}".format(lesson[2][start_index])
            except IndexError:    
                string += ", {}".format(lesson[2][0])
            try:
                string += ", {}".format(lesson[3][start_index])
            except IndexError:    
                string += ", {}".format(lesson[3][0])
            try:
                string += ", {}".format(lesson[4][start_index])
            except IndexError:    
                string += ", {}".format(lesson[4][0])
            array.append(string)

        for i in range(1+start_index, len(lesson[1])):
            if (lesson[1][i] == "—"):
                continue
            string = "   {}".format(lesson[1][i])
            try:
                string += ", {}".format(lesson[2][i])
            except IndexError:    
                string += ", {}".format(lesson[2][0])
            try:
                string += ", {}".format(lesson[3][i])
            except IndexError:    
                string += ", {}".format(lesson[3][0])
            try:
                string += ", {}".format(lesson[4][i])
            except IndexError:    
                string += ", {}".format(lesson[4][0])
            array.append(string)
    return array

def create_schedule_day_heading(group_name, week_num, week_day_num, type):  #создание расписания на день с заголовком
    array = []
    string = "Расписание на "
    today = datetime.datetime.today()
    tomorrow = today + datetime.timedelta(days=1)
    if type == "сегодня":
        string += today.strftime("%d.%m")
    elif type == "завтра":
        string += tomorrow.strftime("%d.%m")
    else:
        if type == "среда":
            string += "среду"
        elif type == "пятница":
            string += "пятницу"
        elif type == "суббота":
            string += "субботу"
        else:
            string += type
    if (week_num % 2 == 0):
        string += " ({} неделя)".format(week_num)
    else:
        string += " ({} неделя)".format(week_num)
    array.append(string)
    array += create_schedule_day(group_name, week_num, week_day_num)
    return array
    
def create_schedule_week_heading(group_name, week_num): #создание расписания на неделю с заголовком
    array = []
    for i in range(6):
        array += create_schedule_day_heading(group_name, week_num, i, WEEK_DAYS[i])
        array.append("")
    return array

def array_to_string(array): #преобразование списка в строку
    string = ""
    for i in array:
        string += i + "\n"
    return string

"""
1) Проверить, возможно ли скачать расписание
2) Проверить, возможно ли скачать расписание экзаменов
3) Проверить, может ли данная неделя быть зачетной: функцию, которая запускает парсинг расписания зачетной недели
4) Разобраться с относительной адрессацией на файлы 
"""

print("TEST")