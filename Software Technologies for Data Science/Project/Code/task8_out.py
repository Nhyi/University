#importing the required modules
import csv
import datetime
import sqlite3

#connect to the database
db = sqlite3.connect('database.db')
cursor = db.cursor()

#have lists which we are going to write to
vehicle_list = ['car', 'taxi', 'bus', 'bicycle', 'motorbike', 'van', 'truck', 'other']
writing_to_csv = []
INPUT = False

#constantly checking for correct datetime inputs
while INPUT == False:

    try:
        start_date = datetime.datetime.strptime(input('Type a start date YEAR-MONTH-DAY-HOUR-MINUTE in the format YYYYMMDDHHMM: '), '%Y%m%d%H%M')
        end_date = datetime.datetime.strptime(input('Type a end date YEAR-MONTH-DAY-HOUR-MINUTE in the format YYYYMMDDHHMM: '), '%Y%m%d%H%M')

        if end_date < start_date:
            print('End date must be after the start date.')
        else:
            INPUT = True
    
    except:
        print('Incorrect time format given, please provide a valid date format.')

#select records in the table
records = cursor.execute('''
                        SELECT locations, types, occupancy, \n
                        COUNT (occupancy) FROM traffic \n
                        WHERE undo = 0 GROUP BY types, occupancy
                        ''')

#recording which different type of vehicle appears and how often
for vehicle in vehicle_list:
    records = list(cursor.execute('''SELECT locations, types, \n
        SUM(occupancy = 1) as cnt_1, \n
        SUM(occupancy = 2) as cnt_2, \n
        SUM(occupancy = 3) as cnt_3, \n
        SUM(occupancy = 4) as cnt_4 \n
FROM traffic \n
WHERE undo = 0 AND \n
        types = ? AND \n
        time_added BETWEEN ? AND ? \n
GROUP BY types;''', (vehicle, start_date, end_date)))

    if records:
        writing_to_csv.append(records[0])

#write the output to a csv file
with open ('task8_out.csv', 'w', newline = '') as f:
    for record in writing_to_csv:
        write = csv.writer(f)
        write.writerow(record)