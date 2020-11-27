#importing required modules
import csv
import datetime
import sqlite3

db = sqlite3.connect('database.db')
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
            cursor.execute('''UPDATE loginsession SET end_time = ? WHERE username = ?''', (record_time, username))

        db.commit()
