import sqlite3
import json

# Путь к JSON файлу с данными
json_file_path = 'schedule.json'

# Загружаем данные из JSON-файла
with open(json_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Создаем подключение к базе данных
conn = sqlite3.connect('65rrr656schedule.db')
cursor = conn.cursor()

# Создаем таблицы для дней недели, групп, дисциплин, преподавателей и расписания
cursor.execute('''
CREATE TABLE IF NOT EXISTS days_of_week (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS disciplines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_id INTEGER NOT NULL,
    time TEXT NOT NULL,
    group_id INTEGER NOT NULL,
    discipline_id INTEGER NOT NULL,
    teacher_id INTEGER,
    room TEXT NOT NULL,
    lesson_type TEXT NOT NULL,
    week TEXT NOT NULL,
    FOREIGN KEY (day_id) REFERENCES days_of_week (id),
    FOREIGN KEY (group_id) REFERENCES groups (id),
    FOREIGN KEY (discipline_id) REFERENCES disciplines (id),
    FOREIGN KEY (teacher_id) REFERENCES teachers (id)
)
''')

# Вставляем дни недели в таблицу
days_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
day_ids = {}
for day in days_of_week:
    cursor.execute('INSERT OR IGNORE INTO days_of_week (name) VALUES (?)', (day,))
    day_ids[day] = cursor.lastrowid

# Вставляем группы в таблицу
groups = {}
for item in data:
    group_name = item['group']
    if group_name not in groups:
        cursor.execute('INSERT OR IGNORE INTO groups (name) VALUES (?)', (group_name,))
        groups[group_name] = cursor.lastrowid

# Вставляем дисциплины в таблицу
disciplines = {}
for item in data:
    discipline_name = item['course']['name']
    if discipline_name not in disciplines:
        cursor.execute('INSERT OR IGNORE INTO disciplines (name) VALUES (?)', (discipline_name,))
        disciplines[discipline_name] = cursor.lastrowid

# Вставляем преподавателей в таблицу
teachers = {}
for item in data:
    teacher_name = item['course']['teacher']
    if teacher_name not in teachers:
        cursor.execute('INSERT OR IGNORE INTO teachers (name) VALUES (?)', (teacher_name,))
        teachers[teacher_name] = cursor.lastrowid

# Вставляем данные в таблицу расписания
for item in data:
    group_name = item['group']
    day_of_week = item['day']
    time = item['time']
    discipline_name = item['course']['name']
    teacher_name = item['course']['teacher']
    room = item['course']['room']
    lesson_type = item['course']['type']
    week = item['course']['week']

    # Получаем id дня недели, группы, дисциплины и преподавателя
    day_id = day_ids[day_of_week]
    group_id = groups[group_name]
    discipline_id = disciplines[discipline_name]
    teacher_id = teachers[teacher_name]
    

    # Вставляем данные в таблицу расписания
    cursor.execute('''
    INSERT INTO schedule (day_id, time, group_id, discipline_id, teacher_id, room, lesson_type, week)
    VALUES (?, ?, ?, ?, ?, ?, ?,?)
    ''', (day_id, time, group_id, discipline_id, teacher_id, room, lesson_type, week))

# Сохраняем изменения и закрываем подключение
conn.commit()
conn.close()

print("Database has been populated with schedule data.")
