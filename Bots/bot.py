# импортируем необходимые модули
import time
import logging
import os
import json
import array
from datetime import date
import datetime
# модули для запросов
import requests
import urllib
# модули для бота
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from prettytable import PrettyTable
# модули для таблиц и изображений
import numpy
import pandas
import matplotlib.pyplot as plt
import dataframe_image as dfi

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
TOKEN = "6132474260:AAFB7HnGxSNWvQuqepD8R7Ejl2d1Dc3c1TU"
# Выделяем оперативную память под данные о пользователях
storage = MemoryStorage()
# подключаемся к чат-боту при помощи токена
# Объект бота
bot = Bot(token=TOKEN)
# Диспетчер
dp=Dispatcher(bot=bot,storage=storage)

# Переменные
keyboardTostart=ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
keyboardTostart.add(KeyboardButton(text="Назад"))

keyboard_prof_menu = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
keyboard_prof_menu.add(KeyboardButton(text="Вернуться в главное меню"))
keyboard_prof_menu.add(KeyboardButton(text="Получить другой тип расписания"))

keyboard_stud_menu = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
keyboard_stud_menu.add(KeyboardButton(text="Вернуться в главное меню"))
keyboard_stud_menu.add(KeyboardButton(text="Выбрать другой тип расписания"))
st_group=list()
prof_name=list()
class othersData(StatesGroup):
    userDate = State()
    professorsDate=State()
class studentInfo (StatesGroup):
    s_name = State()
    group = State()

class professorInfo(StatesGroup):
    p_name = State()
    p_group = State()

# GETметоды запросов на сервер 1С
# Получить ВСЕ группы для студента
def getStudentGroups(value):
    BASE_URL = 'http://localhost/Bot/hs/services'

    payload = {'name': str(value)}
    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)    
    response = requests.get(f"{BASE_URL}/students/name",params=params)

    response.encoding = 'utf-8'
    temp=json.loads(response.text)
    arr=list()
    for i in temp:
        arr.append(i['group'])
    return (arr)
# Получить ВСЕ кафедры преподавателя
def getProfessorInfo(value):
    BASE_URL = 'http://localhost/Bot/hs/services'

    payload = {'name': str(value)}
    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)    
    response = requests.get(f"{BASE_URL}/professors/info",params=params)

    response.encoding = 'utf-8'
    temp=json.loads(response.text)
    arr=list()
    for i in temp:
        arr.append(i['department'])
    return (arr)
# Получить расписание на ОДИН день студенту
def getStudentTimetable_DAY(g_value,d1_value):
    BASE_URL = 'http://localhost/Bot/hs/services'

    str_date=str(d1_value).replace("-","")
    payload = {'group': str(g_value), 'date': str(str_date)}
    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)    
    response = requests.get(f"{BASE_URL}/students/timetableDay",params=params)

    response.encoding = 'utf-8'
    try:
        temp=json.loads(response.text)
        time=[["9:30-11:05"],["9:30-11:05","11:20-12:55"], 
          ["9:30-11:05","11:20-12:55","13:10-14:45"],
          ["9:30-11:05","11:20-12:55","13:10-14:45","15:25-17:00"],
          ["9:30-11:05","11:20-12:55","13:10-14:45","15:25-17:00", "17:15-18:50"]]
    
        names_def = ["Корпус", "Аудитория", "Дисциплина", "Преподаватель", "Тип занятия", "Пара"]
        names_rig = ["Пара", "Дисциплина", "Преподаватель",  "Тип занятия", "Аудитория", "Корпус"] 
        df = pandas.DataFrame(temp)
        i=df.shape[0]
        df.columns=names_def
        df=df.reindex(columns=names_rig)
        df=df.sort_values(by="Пара")
        df.drop("Пара",  axis= 1 , inplace= True)
        df.index=time[i-1]
        img_name=str(g_value+"_расписание_на_день_"+str(d1_value) + ".jpg")
        dfi.export(df, img_name)
        return img_name
    except Exception:
        return "На заданную дату нет занятий!"
# Получить расписание на ОДИН день преподавателю
def getProfessorTimeTable_DAY(name_value,date_value):
    BASE_URL = 'http://localhost/Bot/hs/services'
    str_date=str(date_value).replace("-","")
    payload = {'name': str(name_value), 'date': str(str_date)}
    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)    
    response = requests.get(f"{BASE_URL}/professors/timetableDay",params=params)
    response.encoding = 'utf-8'
    try: 
        temp=json.loads(response.text)
        time=[["9:30-11:05"],["9:30-11:05","11:20-12:55"], 
          ["9:30-11:05","11:20-12:55","13:10-14:45"],
          ["9:30-11:05","11:20-12:55","13:10-14:45","15:25-17:00"],
          ["9:30-11:05","11:20-12:55","13:10-14:45","15:25-17:00", "17:15-18:50"]]

        names_def = ["Корпус", "Дисциплина", "Аудитория", "Группа", "Тип занятия", "Пара"]
        names_rig = ["Пара", "Дисциплина", "Группа",  "Тип занятия", "Аудитория", "Корпус"] 
        df = pandas.DataFrame(temp)
        i=df.shape[0]
        df.columns=names_def
        df=df.reindex(columns=names_rig)
        df=df.sort_values(by="Пара")
        df.drop("Пара",  axis= 1 , inplace= True)
        df.index=time[i-1]
        img_name=str(name_value+"_расписание_на_" + str(date_value) + ".jpg")
        dfi.export(df, img_name)
        return img_name
    except Exception:
        return "На заданную дату нет занятий!"
# Получить расписание на НЕДЕЛЮ студенту
def getStudentTimetable_WEEK(name_value,date_value):
    BASE_URL = 'http://localhost/Bot/hs/services'
    str_date=str(date_value).replace("-","")

    payload = {'group': str(name_value), 'date': str(str_date)}
    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)    
    response = requests.get(f"{BASE_URL}/students/timetableWeek",params=params)

    response.encoding = 'utf-8'
    try: 
        temp=json.loads(response.text)

        names_def = ["Время", "Дисциплина", "Преподаватель", "День недели", "Аудитория", "Корпус", "Пара", "Тип занятия", "Четность"]
        names_rig = ["Четность", "День недели", "Пара", "Время", "Дисциплина", "Преподаватель", "Тип занятия", "Аудитория", "Корпус"] 
        names_p = ["День недели", "Время", "Дисциплина", "Преподаватель", "Тип занятия", "Аудитория", "Корпус"]  
        df = pandas.DataFrame(temp)
        df.columns=names_def
        df=df.reindex(columns=names_rig)
        df=df.sort_values(by="Пара")
        df=df.sort_values(by="День недели")
        df.drop("Пара",  axis= 1 , inplace= True)
        df.drop("Четность",  axis= 1 , inplace= True)
        df=pandas.pivot_table(df, index=names_p)
        img_name=str(name_value+"_расписание_на_неделю.jpg")
        dfi.export(df, img_name)
        return img_name
    except Exception:
        return "На заданную дату нет занятий!"
# Получить расписание на НЕДЕЛЮ преподавателу
def getProfessorTimetable_WEEK(name_value,date_value):
    BASE_URL = 'http://localhost/Bot/hs/services'
    str_date=str(date_value).replace("-","")

    payload = {'name': str(name_value), 'date': str(str_date)}
    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)    
    response = requests.get(f"{BASE_URL}/professors/timetableWeek",params=params)

    response.encoding = 'utf-8'
    try: 
        temp=json.loads(response.text)

        names_def = ["Время", "Дисциплина", "День недели", "Группа", "Аудитория", "Корпус", "Пара", "Тип занятия", "Четность"]
        names_rig = ["Четность", "День недели", "Пара", "Время", "Дисциплина", "Группа", "Тип занятия", "Аудитория", "Корпус"] 
        names_p = ["День недели", "Время", "Дисциплина", "Группа", "Тип занятия", "Аудитория", "Корпус"]  
        df = pandas.DataFrame(temp)
        df.columns=names_def
        df=df.reindex(columns=names_rig)
        df=df.sort_values(by="Пара")
        df=df.sort_values(by="День недели")
        df.drop("Пара",  axis= 1 , inplace= True)
        df.drop("Четность",  axis= 1 , inplace= True)
        df=pandas.pivot_table(df, index=names_p)
        img_name=str(name_value+"_расписание_на_неделю.jpg")
        dfi.export(df, img_name)
        return img_name
    except Exception:
        return "На заданную дату нет занятий!"

def getStudentsTimetable_ALL(name_value, date_val):
    BASE_URL = 'http://localhost/Bot/hs/services'
    str_date=str(date_val).replace("-","")
    payload = {'group': str(name_value), 'date':str(str_date)}
    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)    
    response = requests.get(f"{BASE_URL}/students/timetableFull",params=params)

    response.encoding = 'utf-8'
    try: 
        temp=json.loads(response.text)

        names_def = ["Время", "Дисциплина", "Преподаватель", "День недели", "Аудитория", "Корпус", "Пара", "Тип занятия", "Четность"]
        names_rig = ["Четность", "День недели", "Пара", "Время", "Дисциплина", "Преподаватель", "Тип занятия", "Аудитория", "Корпус"] 
        names_p = ["Четность","День недели", "Время", "Дисциплина", "Преподаватель", "Тип занятия", "Аудитория", "Корпус"]  
        df = pandas.DataFrame(temp)
        df.columns=names_def
        df=df.reindex(columns=names_rig)
        df=df.sort_values(by="Пара")
        df=df.sort_values(by="День недели")
        df.drop("Пара",  axis= 1 , inplace= True)
        df=pandas.pivot_table(df, index=names_p)
        img_name=str(name_value+"_расписание_на_две_недели.jpg")
        dfi.export(df, img_name)
        return img_name
    except Exception:
        return "На заданную дату нет занятий!"

def getProfessorTimetable_ALL(name_value, date_val):
    BASE_URL = 'http://localhost/Bot/hs/services'
    str_date=str(date_val).replace("-","")
    payload = {'name': str(name_value), 'date':str(str_date)}
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
        return "На заданную дату нет занятий!"


# 0. Главная. Перечень всех возможностей и команд бота (стоит ли дублировать на английском?)
@dp.message_handler(commands=['help'])
async def help_hendler(message: types.Message):
    await message.answer("Для работы с чат-ботом доступны следующие команды:" \
                        "\n 1. Начало работы - /start" \
                        "\n 2. Перейти к авторизации как студент - Студент или /student" \
                        "\n 3. Перейти к авторизации как преподаватель - Преподаватель или /professor" \
                        "\n 4. Получить все команды - /help")

# 1. Студент или Преподаватлеь?

@dp.message_handler(state="*", regexp="Вернуться в главное меню")
@dp.message_handler(state="*", regexp="Назад")
@dp.message_handler(commands=['start'])
async def start_hendler(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard_start = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    student_btn_1 = KeyboardButton(text="Студент")
    professor_btn_1 = KeyboardButton(text="Преподаватель")
    keyboard_start.add(student_btn_1).add(professor_btn_1)
    await message.answer("Добрый день! Вас привествует чат-бот МТУСИ! Чтобы получить доступ"\
                         "к расписанию скажите, кем Вы являетесь? Выберите соттветсвующую"\
                            "кнопку.", reply_markup=keyboard_start)

#*******************************************************************#
# 1.1 Студент
@dp.message_handler(regexp="Студент")
@dp.message_handler(commands=['student'])
async def if_student(message: types.Message):
    await message.answer("Введите свои Имя Фамилию Отчество через пробел с большой буквы.\n"\
                         "Например: Иванов Иван Иванович", reply_markup=keyboardTostart)
    await studentInfo.s_name.set()

# 2.1.1 Ищем студента по ФИО
  
# 2.1.2 Если находим несколько, то уточняем группу
@dp.message_handler(state=studentInfo.s_name)
async def foundStudentGroups(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(s_name=answer)
    temp = getStudentGroups(answer)
    temp.append('Моей группы нет в списке') 
    keyboard_group = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    if len(temp)==1:
        await message.answer("Проверьте правильность введеных Вами данных. Или обратитесь в деканат")
    else:
        for i in range(len(temp)):
            keyboard_group.add(KeyboardButton(text=str(temp[i])))
        await message.answer('Выберите группу:',reply_markup=keyboard_group)
        await studentInfo.group.set()
# 2.1.3 Если не находим, то отправляем на первый шаг "Уточните правильность введеных данных" и отправляем в деканат для проверки
@dp.message_handler(regexp="Моей группы нет в списке")
async def ifNoGroups(message: types.Message):
    await message.answer("Проверьте правильность введеных Вами данных. Или обратитесь в деканат.",reply_markup=keyboardTostart)
    
#*******************************************************************#
# 1.2 Преподаватель
@dp.message_handler(regexp= "Преподаватель")
@dp.message_handler(commands=['professor'])
async def if_professor(message: types.Message):
    await message.answer("Введите свои имя фамилию и отчество в формате: Фамилия И.О.", reply_markup=keyboardTostart)
    await professorInfo.p_name.set()

# 2.2.1 Ищем преподавателя по ФИО

# 2.2.2 Если находим, то уточняем кафедру (чтобы было)
@dp.message_handler(state=professorInfo.p_name)
async def professorsInfo(message: types.Message, state: FSMContext):
    answer = message.text
    temp = getProfessorInfo(answer)
    temp.append('Кафедры нет в списке')
    keyboard_professor = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    if len(temp)==1:
        await message.answer("Проверьте правильность введеных Вами данных. Или обратитесь в деканат")
    else:
        for i in range(len(temp)):
            keyboard_professor.add(KeyboardButton(text=str(temp[i])))
        await message.answer("Выберите свою кафедру:",reply_markup=keyboard_professor)
        await state.update_data(p_name=answer)
        prof_name.append(answer)
        await professorInfo.p_group.set()

# 2.2.3 Если не находим, то просим обратиться в деканат
@dp.message_handler(text="Кафедры нет в списке")
async def ifNoProfessor(message: types.Message):
    await message.answer("Проверьте правильность введеных Вами данных. Или обратитесь в деканат.", reply_markup=keyboardTostart)

#*******************************************************************#
# 3 Получение данных (расписание)
# 3.1 Студент: предостаавляем варианты действий
@dp.message_handler(text="Выбрать другой тип расписания")
@dp.message_handler(state=studentInfo.group)
async def studentTimeTable(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(group=answer)
    students_date=await state.get_data()
    await state.finish()
    keyboard_s_TT = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    keyboard_s_TT.add(KeyboardButton(text="На сегодня"))
    keyboard_s_TT.add(KeyboardButton(text="На завтра"))
    keyboard_s_TT.add(KeyboardButton(text="На заданную дату"))
    keyboard_s_TT.add(KeyboardButton(text="На текущую неделю"))
    keyboard_s_TT.add(KeyboardButton(text="На следующую неделю"))
    keyboard_s_TT.add(KeyboardButton(text="Получить расписание на две недели"))
    st_group.append(answer)
    await message.answer("Какое расписание Вы хотите получить?",reply_markup=keyboard_s_TT)

# 3.1.1 Запрос "Получить расписание на сегодня"
@dp.message_handler(text="На сегодня")
async def studentTimeTable_ToDay(message: types.Message):
    # получаем текущую дату
    toDay = date.today()
    if (st_group[0]!=""):
        groupStr = st_group[0]
        #st_group.clear()
        img_name = getStudentTimetable_DAY(groupStr, toDay)
        if (img_name=="На заданную дату нет занятий!"):
            await message.answer(img_name, reply_markup=keyboard_stud_menu)
        else: 
            img=open(img_name,'rb')
            text = "Расписание для группы " + str(groupStr) + " на " + toDay.strftime("%d-%m-%Y")
            await message.answer_photo(img, caption=text)
            await message.answer("Хотите получить другой тип расписания?", reply_markup=keyboard_stud_menu)
    else: await message.answer("Вернитесь в главное меню для заполнения данных!",reply_markup=keyboardTostart)
    #os.remove(img)
# 3.1.2 Запрос "На завтра"
@dp.message_handler(text="На завтра")
async def studentTimeTable_ToMorrow(message: types.Message):
    # получаем текущую дату
    toDay = date.today()
    tomorrow = toDay + datetime.timedelta(days=1)
    
    if (st_group[0]!=""):
        groupStr = st_group[0]
        img_name = getStudentTimetable_DAY(groupStr, tomorrow)
        if (img_name=="На заданную дату нет занятий!"):
            await message.answer(img_name, reply_markup=keyboard_stud_menu)
        else: 
            img=open(img_name,'rb')
            text = "Расписание для группы " + str(groupStr) + " на " + tomorrow.strftime("%d-%m-%Y")
            await message.answer_photo(img, caption=text)
            await message.answer("Хотите получить другой тип расписания?", reply_markup=keyboard_stud_menu)
    else: await message.answer("Вернитесь в главное меню для заполнения данных!",reply_markup=keyboardTostart)
# 3.1.3 Запрос "На заданную дату"
@dp.message_handler(text="На заданную дату")
async def studentTimeTable_otherDay_get(message: types.Message):
    # получаем текущую дату
    await message.answer("Введите нужную дату в офрмате: дд.мм.гггг")
    await othersData.userDate.set()    

@dp.message_handler(state=othersData.userDate)
async def studentTimeTable_otherDay_return(message: types.Message,state: FSMContext):
    day = message.text
    try: 
        toDate = datetime.datetime.strptime(day, '%d.%m.%Y').date() 
        #temp=await state.get_data()
        groupStr = st_group[0]
        if (st_group[0]!=""):
            groupStr = st_group[0]
            img_name = getStudentTimetable_DAY(groupStr, toDate)
            if (img_name=="На заданную дату нет занятий!"):
                await message.answer(img_name, reply_markup=keyboard_stud_menu)
            else: 
                img=open(img_name,'rb')
                text = "Расписание для группы " + str(groupStr) + " на " + toDate.strftime("%d-%m-%Y")
                await state.update_data(userDate=day)
                await state.finish()
                await message.answer_photo(img, caption=text)
                await message.answer("Хотите получить другой тип расписания?", reply_markup=keyboard_stud_menu)
        else: await message.answer("Вернитесь в главное меню для заполнения данных!",reply_markup=keyboardTostart)    
    except Exception:
        await message.answer("Дата введена некорректно. Попробуйте еще раз")
# 3.1.4 Запрос "На текущую неделю"
@dp.message_handler(text="На текущую неделю")
async def studentTimeTable_ThisWeek(message: types.Message):
    # получаем текущую дату
    toDay = date.today()
    groupStr = st_group[0]
    if (st_group[0]!=""):
        groupStr = st_group[0]
        img_name = getStudentTimetable_WEEK(groupStr, toDay)
        if (img_name=="На заданную дату нет занятий!"):
            await message.answer(img_name, reply_markup=keyboard_stud_menu)
        else: 
            img=open(img_name,'rb')
            text = "Расписание для группы " + str(groupStr) + " на текущую неделю"
            await message.answer_photo(img, caption=text)
            await message.answer("Хотите получить другой тип расписания?", reply_markup=keyboard_stud_menu)
    else: await message.answer("Вернитесь в главное меню для заполнения данных!",reply_markup=keyboardTostart)

# 3.1.5 Запрос "На следующую неделю"
@dp.message_handler(text="На следующую неделю")
async def studentTimeTable_ThisWeek(message: types.Message):
    # получаем текущую дату
    toDay = date.today()
    toDay= toDay + datetime.timedelta(days=7)
    groupStr = st_group[0]
    if (st_group[0]!=""):
        groupStr = st_group[0]
        img_name = getStudentTimetable_WEEK(groupStr, toDay)
        if (img_name=="На заданную дату нет занятий!"):
            await message.answer(img_name, reply_markup=keyboard_stud_menu)
        else: 
            img=open(img_name,'rb')
            text = "Расписание для группы " + str(groupStr) + " на следующую неделю"
            await message.answer_photo(img, caption=text)
            await message.answer("Хотите получить другой тип расписания?", reply_markup=keyboard_stud_menu)
    else: await message.answer("Вернитесь в главное меню для заполнения данных!",reply_markup=keyboardTostart)

# 3.1.6 Запрос "Получить расписание на две недели"
@dp.message_handler(text="Получить расписание на две недели")
async def studentTimeTable_ThisWeek(message: types.Message):
    # получаем текущую дату
    toDay = date.today()
    groupStr = st_group[0]
    if (st_group[0]!=""):
        groupStr = st_group[0]
        img_name = getStudentsTimetable_ALL(groupStr, toDay)
        if (img_name=="На заданную дату нет занятий!"):
            await message.answer(img_name, reply_markup=keyboard_stud_menu)
        else: 
            img=open(img_name,'rb')
            text = "Расписание для группы " + str(groupStr) + " на ближайшие две недели"
            await message.answer_photo(img, caption=text)
            await message.answer("Хотите получить другой тип расписания?", reply_markup=keyboard_stud_menu)
    else: await message.answer("Вернитесь в главное меню для заполнения данных!",reply_markup=keyboardTostart)

#*******************************************************************#
# 3.2 Преподаватель
@dp.message_handler(text="Получить другой тип расписания")
@dp.message_handler(state=professorInfo.p_group)
async def professorTimeTable(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(p_group=answer)
    prof_name.append(answer)
    await state.finish()
    keyboard_s_TT = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    keyboard_s_TT.add(KeyboardButton(text="Расписание на сегодня"))
    keyboard_s_TT.add(KeyboardButton(text="Расписание на завтра"))
    keyboard_s_TT.add(KeyboardButton(text="Расписание на заданную дату"))
    keyboard_s_TT.add(KeyboardButton(text="Расписание на текущую неделю"))
    keyboard_s_TT.add(KeyboardButton(text="Расписание на следующую неделю"))
    keyboard_s_TT.add(KeyboardButton(text="Расписание на две недели"))
    #st_group.append(answer)
    await message.answer("Какое расписание Вы хотите получить?",reply_markup=keyboard_s_TT)
# 3.2.1 Запрос "Получить расписание на сегодня"
@dp.message_handler(text="Расписание на сегодня")
async def professorTimeTable_ToDay(message: types.Message):
    # получаем текущую дату
    toDay = date.today()
    name=prof_name[0]
    if (prof_name[0]!=""):
        name=prof_name[0]
        #st_group.clear()
        img_name = getProfessorTimeTable_DAY(name, toDay)
        if (img_name=="На заданную дату нет занятий!"):
            await message.answer(img_name, reply_markup=keyboard_prof_menu)
        else: 
            img=open(img_name,'rb')
            text = "Расписание для преподавателя кафедры '" + str(prof_name[1]) + "' " + str(name) + " на " + toDay.strftime("%d-%m-%Y")
            await message.answer_photo(img, caption=text)
            await message.answer("Выберете дальнейшие действия:", reply_markup=keyboard_prof_menu)
    else: await message.answer("Вернитесь в главное меню для заполнения данных!",reply_markup=keyboardTostart)
    #os.remove(img)
# 3.2.2 Запрос "На завтра"
@dp.message_handler(text="Расписание на завтра")
async def professorTimeTable_ToMorrow(message: types.Message):
    # получаем текущую дату
    toDay = date.today()
    tomorrow = toDay + datetime.timedelta(days=1)
    
    if (prof_name[0]!=""):
        name=prof_name[0]
        img_name = getProfessorTimeTable_DAY(name, tomorrow)
        if (img_name=="На заданную дату нет занятий!"):
            await message.answer(img_name, reply_markup=keyboard_prof_menu)
        else: 
            img=open(img_name,'rb')
            text = "Расписание для преподавателя кафедры '" + str(prof_name[1]) + "' " + str(name) + " на " + tomorrow.strftime("%d-%m-%Y")
            await message.answer_photo(img, caption=text)
            await message.answer("Выберете дальнейшие действия:", reply_markup=keyboard_prof_menu)
    else: await message.answer("Вернитесь в главное меню для заполнения данных!",reply_markup=keyboardTostart)
# 3.2.4 Запрос "На текущую неделю"
@dp.message_handler(text="Расписание на текущую неделю")
async def professorTimeTable_ToDay(message: types.Message):
    # получаем текущую дату
    toDay = date.today()
    
    if (prof_name[0]!=""):
        name=prof_name[0]
        #st_group.clear()
        img_name = getProfessorTimetable_WEEK(name, toDay)
        if (img_name=="На заданную дату нет занятий!"):
            await message.answer(img_name, reply_markup=keyboard_prof_menu)
        else: 
            img=open(img_name,'rb')
            text = "Расписание для преподавателя кафедры '" + str(prof_name[1]) + "' " + str(name) + " на текущую неделю"
            
            await message.answer_photo(img, caption=text)
            await message.answer("Выберете дальнейшие действия:", reply_markup=keyboard_prof_menu)
            
    else: await message.answer("Вернитесь в главное меню для заполнения данных!",reply_markup=keyboardTostart)
# 3.2.5 Запрос "На следующую неделю"
@dp.message_handler(text="Расписание на следующую неделю")
async def professorTimeTable_ToDay(message: types.Message):
    # получаем текущую дату
    toDay = date.today()
    toDay = toDay + datetime.timedelta(days=7)
    
    if (prof_name[0]!=""):
        name=prof_name[0]
        #st_group.clear()
        img_name = getProfessorTimetable_WEEK(name, toDay)
        if (img_name=="На заданную дату нет занятий!"):
            await message.answer(img_name, reply_markup=keyboard_prof_menu)
        else: 
            img=open(img_name,'rb')
            text = "Расписание для преподавателя кафедры '" + str(prof_name[1]) + "' " + str(name) + " на следующую неделю"
            await message.answer_photo(img, caption=text)
            await message.answer("Выберете дальнейшие действия:", reply_markup=keyboard_prof_menu) 
# 3.2.6 Запрос "Получить расписание на две недели" 
@dp.message_handler(text="Расписание на две недели")
async def professorTimeTable_ToDay(message: types.Message):
    toDay = date.today()
    
    if (prof_name[0]!=""):
        name=prof_name[0]
        img_name = getProfessorTimetable_ALL(name, toDay)
        if (img_name=="На заданную дату нет занятий!"):
            await message.answer(img_name, reply_markup=keyboard_prof_menu)
        else: 
            img=open(img_name,'rb')
            text = "Расписание для преподавателя кафедры '" + str(prof_name[1]) + "' " + str(name) + " на ближайшие две недели"
            await message.answer_photo(img, caption=text)
            await message.answer("Хотите получить другой тип расписания?", reply_markup=keyboard_prof_menu)
    else: await message.answer("Вернитесь в главное меню для заполнения данных!",reply_markup=keyboardTostart)
# 3.2.3 Запрос "На заданную дату"
@dp.message_handler(text="Расписание на заданную дату")
async def sprofessorTimeTable_otherDay_get(message: types.Message,state: FSMContext):
    # получаем текущую дату
    await message.answer("Введите нужную дату в офрмате: дд.мм.гггг")
    await othersData.professorsDate.set()    
@dp.message_handler(state=othersData.professorsDate)
async def professorTimeTable_otherDay_return(message: types.Message,state: FSMContext):
    day = message.text
    try: 
        toDate = datetime.datetime.strptime(day, "%d.%m.%Y").date() 
        #temp=await state.get_data()
        
        if (prof_name[0]!=""):
            name=prof_name[0]
            img_name = getProfessorTimeTable_DAY(name, toDate)
            if (img_name=="На заданную дату нет занятий!"):
                await message.answer(img_name, reply_markup=keyboard_prof_menu)
            else: 
                img=open(img_name,'rb')
                text = "Расписание для преподавателя кафедры '" + str(prof_name[1]) + "' " + str(name) + " на " + toDate.strftime("%d-%m-%Y")
                await state.update_data(professorsDate=day)
                await state.finish()
                await message.answer_photo(img, caption=text)
                await message.answer("Выберете дальнейшие действия:", reply_markup=keyboard_prof_menu)
        else: 
            
            await message.answer("Вернитесь в главное меню для заполнения данных!",reply_markup=keyboardTostart)    
    except Exception:
        await message.answer("Дата введена некорректно. Попробуйте еще раз")


# 0.1 Обработчик общих ошибок (для текста, не являющегося командами)
# Данный блок написан в самом конце, чтобы "обрабатывать" не обработанные команды
@dp.message_handler()
async def empty(message: types.Message):
    await message.answer("Данная команда отсутсвует. Пожалуйста, выберете команду из предложенного списка или введите корректные данные.")
    #await message.delete() //данная команда удаляет сообщение пользователя, которые не обрабатывается


if __name__=='__main__':
    executor.start_polling(dp, skip_updates=True)# пропускаем сообщения, которые были получены во время выключения бота