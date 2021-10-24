import datetime
import json
import os
import sys
import requests
from decimal import Decimal, ROUND_HALF_DOWN
from PIL import Image, ImageDraw, ImageFont
from CONSTANTS import *
from config import *

dirpath = os.path.dirname(__file__) #текущее расположение файла

def text_to_png(array): #перевод текста на картинку
    img = Image.new('RGB', (350 , 30 * len(array)), color = (255, 255, 255))
    main_font = ImageFont.truetype("arial.ttf", 15)
    for i in range(len(array)):
        img_temp = Image.new('RGB', (500, 30), color = (255, 255, 255))
        d = ImageDraw.Draw(img_temp)
        d.text((10,10), array[i], fill=(0,0,0), font=main_font)
        img.paste(img_temp, (0, 30 * i))
    return img

def download_weather_current(): #скачать текущую погоду
  response = requests.get(OPEN_WEATHER_CURRENT.format(OPEN_WEATHER_KEY))
  info = response.json()
  filename = "cache\weather_current.json"
  filepath = os.path.join(dirpath, filename)
  with open(filepath, "w") as f:
    json.dump(info, f)

def download_weather_5days(): #скачать прогноз погоды на 5 дней
  response = requests.get(OPEN_WEATHER_5DAYS.format(OPEN_WEATHER_KEY))
  info = response.json()
  filename = "cache\weather_5days.json"
  filepath = os.path.join(dirpath, filename)
  with open(filepath, "w") as f:
    json.dump(info, f)

def get_weather_current():  #получить текущую погоду
  filename = "cache\weather_current.json"
  filepath = os.path.join(dirpath, filename) 
  if os.path.isfile(filepath):
    with open(filepath, "r") as f:
      info = json.load(f)
      if (datetime.datetime.now() - datetime.datetime.fromtimestamp(int(info["dt"])) < datetime.timedelta(0, 0, 0, 0, 30)):   #погода обновлена в последние полчаса
        return (info, False)  #true - нужно обновить погоду, false - не нужно
  download_weather_current()  #обновить погоду
  return (get_weather_current()[0], True)

def get_weather_5days():    #получить прогноз погоды на 5 дней
  filename = "cache\weather_5days.json"
  filepath = os.path.join(dirpath, filename)
  if os.path.isfile(filepath):
    with open(filepath, "r") as f:
      info = json.load(f)
      if datetime.datetime.now() - datetime.datetime.fromtimestamp(int(info["list"][0]["dt"])) < datetime.timedelta(0, 0, 0, 0, 0, 3):  #погода обновлена в последние 3 часа
        return (info["list"], False)    #true - нужно обновить погоду, false - не нужно
  download_weather_5days()  #обновить прогноз погоды
  return (get_weather_5days()[0], True)

def get_clouds(info):   #облачность
    cloud = info["clouds"]["all"]
    cloud_state = "Облачно" if cloud > 0.4 else "Ясное небо" if cloud < 0.1 else "Небольшая облачность"
    return cloud_state

def get_wind_speed(info):   #скорость ветра
  wind_speed = info["wind"]["speed"]
  wind = ""
  if wind_speed < 1:
    wind = "нет"
  elif wind_speed < 4:
    wind = "легкий"
  elif wind_speed < 9:
    wind = "умеренный"
  elif wind_speed < 16:
    wind = "сильный"
  else:
    wind = "буря"
  return (wind, wind_speed)

def get_wind_direction(info):   #направление ветра  
  wind_deg = int(info["wind"]["deg"])
  wind_direction = ""
  if (30 <= wind_deg < 60):
    wind_direction = "северо-восточный"
  elif (wind_deg < 120):
    wind_direction = "восточный"
  elif (wind_deg < 150):
    wind_direction = "юго-восточный"
  elif (wind_deg < 210):
    wind_direction = "южный"
  elif (wind_deg < 240):
    wind_direction = "юго-западный"
  elif (wind_deg < 300):
    wind_direction = "западный"
  elif (wind_deg < 330):
    wind_direction = "северо-западный"
  else:
    wind_direction = "северный"
  return wind_direction

def get_temp(info): #температура
  return Decimal(info["main"]["temp"]).quantize(Decimal("1.0"))

def get_temp_max_min(info): #макс/мин температура
    return Decimal(info["main"]["temp_max"]).quantize(Decimal("1.0")), Decimal(info["main"]["temp_min"])\
    .quantize(Decimal("1.0"))

def get_humidity(info): #влажность воздуха
    return int(info["main"]["humidity"])

def get_pressure(info): #давление
    return int(info["main"]["pressure"] * 100 / 133)

def get_weather_icon_url(info): #ссылки на иконку погоды
    return OPEN_WEATHER_ICON + info["weather"][0]["icon"]+".png"

def create_weather_current_png(): #перевод информации о текущей погоде из текста на картинку
  if (get_weather_current()[1]):
    info = get_weather_current()[0]
    img = Image.new('RGB', (350 , 30 * 7), color = (255, 255, 255))
    img_temp = text_to_png(["Погода в Москве"])
    img.paste(img_temp, (0, 0))
    img_icon = Image.open(requests.get(get_weather_icon_url(info), stream=True).raw)
    img.paste(img_icon, (75, 30))
    text_array = []
    temp_max, temp_min = get_temp_max_min(info)
    text_array.append(f"{get_clouds(info)}, температура: {temp_min} - {temp_max}°C")
    text_array.append(f"Давление: {get_pressure(info)} рт.ст., влажность: {get_humidity(info)}%")
    wind, wind_speed = get_wind_speed(info)
    text_array.append(f"Ветер: {wind}, {wind_speed} м/с, {get_wind_direction(info)}")
    img.paste(text_to_png(text_array), (0, 90))
    img_name = "cache\weather_current.png"
    img_path = os.path.join(dirpath, img_name) 
    img.save(img_path)

def create_weather_5days_png(): #перевод информации о погоде за 5 дней из текста на картинку
  if (get_weather_5days()[1] or True):  #убрать true
    temp_array = 10 * [0]   #список температур для перевода в png
    icon_array = []   #список иконок для перевода в png 
    info = get_weather_5days()[0]

    if datetime.datetime.fromtimestamp(info[len(info)-1]['dt']).time() <= datetime.time(hour=12):  #время до 12, значит прогноз начинается с текущего дня
      dt_1day = datetime.datetime.fromtimestamp(info[0]['dt'])  #дата первого дня в (dt)
    else:
      dt_1day = datetime.datetime.fromtimestamp(info[0]['dt']) + datetime.timedelta(days=1) #дата первого дня в (dt)
    dt_5day = dt_1day + datetime.timedelta(days=5, hours=-12) #дата пятого дня в (dt)

    counter = 0 #счетчик кол-ва заходов в условие
    for i in range(len(info)):
      dt_iday = datetime.datetime.fromtimestamp(info[i]['dt'])
      
      if (dt_iday >= dt_1day and dt_iday.time() == dt_1day.time()): # 12:00
        
        print(dt_iday)
        print(get_temp(info[i]))

        counter += 1
      if (dt_iday <= dt_5day and dt_iday.time() == dt_5day.time()): # 00:00
        print(dt_iday)
        print(get_temp(info[i]))

        counter += 1
    
    dt_1day_str = dt_1day.strftime("%d.%m")  #дата первого дня (dd.mm)
    dt_5day_str = dt_5day.strftime("%d.%m")  #дата пятого дня (dd.mm)
    img = Image.new('RGB', (350, 30 * 7), color = (255, 255, 255))
    img_temp = text_to_png([f"Погода в Москве с {dt_1day_str} по {dt_5day_str}"])
    img.paste(img_temp, (0, 0))


    img_name = "cache\weather_5days.png"
    img_path = os.path.join(dirpath, img_name)
    img.save(img_path)



create_weather_5days_png()
create_weather_current_png()