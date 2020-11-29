#importing the required modules
import csv
import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


db = sqlite3.connect('database.db')
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

cursor.execute('''SELECT * FROM loginsession WHERE end_time IS NOT NULL AND date(start_time) = ?''', (day,))
records = cursor.fetchall()

for record in records:
    print(record)

# with open ('task9_out.csv', 'w', newline = '') as f:
#     for record in writing_to_csv:
#         write = csv.writer(f)
#         write.writerow(record)