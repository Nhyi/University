#importing the required modules
import csv
import sqlite3
from math import ceil
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

db = sqlite3.connect('initial_database.db')
cursor = db.cursor()

correct_entry = False

while correct_entry == False:

    try:
        time = datetime.strptime(input('Type a start date YEAR-MONTH-DAY in the format YYYYMMDD: '), '%Y%m%d')
        correct_entry = True
    
    except:
        print('Incorrect time format given, please provide a valid date format.')

day = time
week = day - timedelta(days = 7)
month = day - relativedelta(months=1)

day = day.strftime('%Y-%m-%d')
week = week.strftime('%Y-%m-%d')
month = month.strftime('%Y-%m-%d')

cursor.execute('''SELECT username, (SUM(julianday(end_time) - julianday(start_time))) FROM loginsession WHERE end_time IS NOT NULL AND date(start_time) = ? GROUP BY username''', (day,))
day_records = cursor.fetchall()
name_list = []
day_list = []

cursor.execute('''SELECT username, (SUM(julianday(end_time) - julianday(start_time))) FROM loginsession WHERE end_time IS NOT NULL AND date(start_time) BETWEEN ? AND ? GROUP BY username''', (week, day))
week_records = cursor.fetchall()
week_list = []

cursor.execute('''SELECT username, (SUM(julianday(end_time) - julianday(start_time))) FROM loginsession WHERE end_time IS NOT NULL AND date(start_time) BETWEEN ? AND ? GROUP BY username''', (month, day))
month_records = cursor.fetchall()
month_list = []

for record in day_records:
    name_list.append(record[0])
    day_list.append(ceil((record[1] * 24) * 10) / 10)

for record in week_records:
    week_list.append(ceil((record[1] * 24) * 10) / 10)

for record in month_records:
    month_list.append(ceil((record[1] * 24) * 10) / 10)

complete_list = list(zip(name_list, day_list, week_list, month_list))

with open ('task9_out.csv', 'w', newline = '') as f:
    for record in complete_list:
        write = csv.writer(f)
        write.writerow(record)