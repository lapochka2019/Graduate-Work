import requests
import urllib
from prettytable import PrettyTable
import json
import array
from datetime import date
from datetime import datetime
import numpy
import pandas
import matplotlib.pyplot as plt
import dataframe_image as dfi
from PIL import Image

def getProfessorTimetable_ALL(name_value, date_val):
    BASE_URL = 'http://localhost/Bot/hs/services'

    payload = {'name': str(name_value), 'date':str(date_val)}
    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)    
    response = requests.get(f"{BASE_URL}/professors/timetableFull",params=params)

    response.encoding = 'utf-8'
    try: 
        temp=json.loads(response.text)

        names_def = ["Время", "Дисциплина", "День недели", "Группа", "Аудитория", "Корпус", "Пара", "Тип занятия", "Четность"]
        names_rig = ["Четность", "День недели", "Пара", "Время", "Дисциплина", "Группа", "Тип занятия", "Аудитория", "Корпус"] 
        names_p = ["Четность","День недели", "Время", "Дисциплина", "Группа", "Тип занятия", "Аудитория", "Корпус"]  
        df = pandas.DataFrame(temp)
        df.columns=names_def
        df=df.reindex(columns=names_rig)
        df=df.sort_values(by="Пара")
        df=df.sort_values(by="День недели")
        df.drop("Пара",  axis= 1 , inplace= True)
        df=pandas.pivot_table(df, index=names_p)
        img_name=str(name_value+"_расписание_на_неделю.jpg")
        dfi.export(df, img_name)
        return img_name
    except Exception:
        return "На заданную дату нет занятий"
 
print (getProfessorTimetable_ALL("Прокуровский А.А.","20230509"))
