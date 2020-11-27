#importing required modules
import csv
import datetime
import sqlite3

db = sqlite3.connect('database.db')
cursor = db.cursor()

with open('task8_out.csv', 'w', newline = '') as file:

    file = csv.reader(file)
    
    for row in file:
        username = row[0]
        csv_datetime = row[1]
        login_logout = row[2]

        if login_logout == 'logout':
            cursor.execute('''UPDATE loginsession SET end = ? WHERE user = ?)''', (csv_datetime, username))
        else:
            cursor.execute('''INSERT INTO loginsession VALUES ?, ?, 0, 0''', (username, csv_datetime))

        db.commit()
