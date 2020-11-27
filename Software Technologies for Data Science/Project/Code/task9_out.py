#importing the required modules
import csv
import datetime
import sqlite3

db = sqlite3.connect('database.db')
cursor = db.cursor()

correct_entry = False

while correct_entry == False:

    try:
        time = datetime.datetime.strptime(input('Type a start date YEAR-MONTH-DAY-HOUR-MINUTE in the format YYYYMMDDHHMM: '), '%Y%m%d%H%M')
        correct_entry = True
    
    except:
        print('Incorrect time format given, please provide a valid date format.')

cursor.execute('''SELECT username, (SUM(end - start)) GROUP BY username WHERE 