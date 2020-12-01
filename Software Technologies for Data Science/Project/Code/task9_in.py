#importing required modules
import os
import csv
import datetime
import sqlite3
from database_script import database_creation

if os.path.exists('task9_in.db'):
    os.remove('task9_in.db')

database_creation('task9_in.db')
db = sqlite3.connect('task9_in.db')
cursor = db.cursor()

with open('task9_in.csv', 'r', newline = '') as file:

    file = csv.reader(file)
    
    for row in file:
        username = row[0]
        csv_datetime = row[1]
        login_logout = row[2]
        record_time = datetime.datetime.strptime(csv_datetime,'%Y%m%d%H%M')

        if login_logout == 'login':
            cursor.execute('''INSERT INTO loginsession (username, start_time) VALUES (?, ?)''', (username, record_time))

        elif login_logout == 'logout':
            cursor.execute('''UPDATE loginsession SET end_time = ? WHERE username = ? AND end_time IS NULL''', (record_time, username))

        db.commit()
