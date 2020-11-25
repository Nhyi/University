#importing the required modules
import csv
import datetime
import sqlite3

db = sqlite3.connect('database.db')
cursor = db.cursor()

vehicle_list = ['car', 'taxi', 'bus', 'bicycle', 'motorbike', 'van', 'truck', 'other']
writing_to_csv = []
valid_input = False

while valid_input == False:

    try:
        start_date = datetime.datetime.strptime(input('Type a start date YEAR-MONTH-DAY-HOUR-MINUTE in the format YYYYMMDDHHMM: '), '%Y%m%d%H%M')
        end_date = datetime.datetime.strptime(input('Type a end date YEAR-MONTH-DAY-HOUR-MINUTE in the format YYYYMMDDHHMM: '), '%Y%m%d%H%M')
        valid_input == True
    
    except:
        print('Incorrect time format given, please provide a valid date format.')

