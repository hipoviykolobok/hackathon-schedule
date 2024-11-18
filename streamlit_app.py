import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Расписание занятий", page_icon="📅", layout="wide")
st.html('<head><script src="https://telegram.org/js/telegram-web-app.js"></script></head>')

# CSS стили с адаптацией к темному и светлому режиму
st.markdown("""
    <style>
    h1 {
        color: inherit;
        text-align: center;
    }
    .stSelectbox, .stDateInput, .stButton {
        border-radius: 10px;
        padding: 5px;
    }
    @media (prefers-color-scheme: light) {
        .stSelectbox, .stDateInput, .stButton {
            background-color: rgba(240, 240, 240, 0.9);
            border: 1px solid rgba(200, 200, 200, 0.8);
        }
    }
    @media (prefers-color-scheme: dark) {
        .stSelectbox, .stDateInput, .stButton {
            background-color: rgba(50, 50, 50, 0.9);
            border: 1px solid rgba(100, 100, 100, 0.9);
        }
    }
    .stDataFrame table {
        border: 1px solid rgba(200, 200, 200, 0.5);
    }
    .stDataFrame table th {
        background-color: rgba(230, 230, 230, 0.8);
        color: inherit;
    }
    .stDataFrame table td {
        background-color: rgba(250, 250, 250, 0.8);
        color: inherit;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📅 Расписание занятий")
st.markdown('Добро пожаловать в приложение для просмотра расписания занятий! Используйте фильтры слева, чтобы выбрать нужные параметры  и нажмите кнопку "Показать расписание". Мы надеемся, что это приложение сделает ваш учебный процесс удобнее!')

# Функции для работы с данными
def get_data(query, params):
    try:
        # Использование контекстного менеджера для работы с базой данных
        with sqlite3.connect('schedule.db') as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
        return pd.DataFrame(rows, columns=columns)
    except sqlite3.Error as e:
        st.error(f"Ошибка базы данных: {e}")
        return pd.DataFrame()

def get_choices(query):
    try:
        # Использование контекстного менеджера для работы с базой данных
        with sqlite3.connect('schedule.db') as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
        return [row[0] for row in rows]
    except sqlite3.Error as e:
        st.error(f"Ошибка базы данных: {e}")
        return []

def get_days_of_week():
    try:
        with sqlite3.connect('schedule.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM days_of_week ORDER BY id")
            rows = cursor.fetchall()
        return [row[0] for row in rows] if rows else []
    except sqlite3.Error as e:
        st.error(f"Ошибка при получении данных из таблицы days_of_week: {e}")
        return []
        
def get_week_parity(date):
    start_date = datetime(2024, 9, 2)
    delta = date - start_date
    week_number = delta.days // 7
    return 'Нечетная неделя' if week_number % 2 == 0 else 'Четная неделя'

def get_day_of_week(date):
    days_of_week = get_days_of_week()
    return days_of_week[date.weekday()]

# Загружаем доступные значения
groups = get_choices("SELECT name FROM groups")
teachers = get_choices("SELECT name FROM teachers")
disciplines = get_choices("SELECT name FROM disciplines")
audiences = get_choices("SELECT DISTINCT room FROM schedule")  # Используем таблицу schedule для аудиторий
types_of_classes = ['Лекция', 'Практика','Лабораторная']

# Селектбоксы для выбора параметров
st.sidebar.header("Фильтры")
selected_date = st.sidebar.date_input("Дата (необязательно)", value=None)
selected_group = st.sidebar.selectbox("Группа", [""] + groups)
selected_teacher = st.sidebar.selectbox("Преподаватель", [""] + teachers)
selected_discipline = st.sidebar.selectbox("Дисциплина", [""] + disciplines)
selected_audience = st.sidebar.selectbox("Аудитория", [""] + audiences)
selected_type = st.sidebar.selectbox("Тип занятия", [""] + types_of_classes)

# Определяем день недели, если выбрана дата
day_of_week = None
week_parity = None
if selected_date:
    selected_date = datetime.strptime(str(selected_date), '%Y-%m-%d')
    day_of_week = get_day_of_week(selected_date)
    week_parity = get_week_parity(selected_date)
    st.write(f"Выбранная дата: {selected_date.date()}, {day_of_week}, {week_parity}.")

if st.sidebar.button("Показать расписание"):
    query = """
        SELECT 
            disciplines.name AS "Дисциплина",
            teachers.name AS "Преподаватель",
            schedule.time AS "Время",
            days_of_week.name AS "День недели",
            schedule.room AS "Аудитория",
            groups.name AS "Группа",
            schedule.lesson_type AS "Тип занятия",
            schedule.week AS "Тип недели"
        FROM schedule
        JOIN disciplines ON schedule.discipline_id = disciplines.id
        JOIN teachers ON schedule.teacher_id = teachers.id
        JOIN days_of_week ON schedule.day_id = days_of_week.id
        JOIN groups ON schedule.group_id = groups.id
        WHERE 1=1
    """
    params = []
    if selected_group:
        query += " AND groups.name = ?"
        params.append(selected_group)
    if selected_teacher:
        query += " AND teachers.name = ?"
        params.append(selected_teacher)
    if selected_discipline:
        query += " AND disciplines.name = ?"
        params.append(selected_discipline)
    if selected_audience:
        query += " AND schedule.room = ?"
        params.append(selected_audience)
    if day_of_week:
        query += " AND days_of_week.name = ?"
        params.append(day_of_week)
    if selected_type:
        query += " AND schedule.lesson_type = ?"
        params.append(selected_type)
    if week_parity == "Четная неделя":
        query += " AND (schedule.week = ? OR schedule.week = ?)"
        params.extend(["Четная неделя", "Каждая неделя"])
    elif week_parity == "Нечетная неделя":
        query += " AND (schedule.week = ? OR schedule.week = ?)"
        params.extend(["Нечетная неделя", "Каждая неделя"])

    
    schedule = get_data(query, params)
    if schedule.empty:
        st.warning("По вашим фильтрам расписание не найдено.")
    else:
        st.dataframe(schedule)
