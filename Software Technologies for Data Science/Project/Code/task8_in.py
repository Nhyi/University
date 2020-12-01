#importing the required modules
import os
import csv
import datetime
import sqlite3
from database_script import database_creation

if os.path.exists('task8_in.db'):
    os.remove('task8_in.db')

#connecting to the database
database_creation('task8_in.db')
db = sqlite3.connect('task8_in.db')
cursor = db.cursor()

#reading through the file and setting each information to a variable
with open('task8_in.csv', 'r', newline = '') as file:

    file = csv.reader(file)

    for row in file:
        time_added = row[0]
        add_undo = row[1]
        location = row[2]
        vehicle_type = row[3]
        occupancy = row[4]
        record_time = datetime.datetime.strptime(time_added,'%Y%m%d%H%M')

        if add_undo == 'add':
            cursor.execute('''INSERT INTO traffic (username, locations, types, occupancy, time_added)\
                 VALUES (?, ?, ?, ?, ?)''', ('task8_user', location, vehicle_type, occupancy, record_time))
        else:
            cursor.execute('''UPDATE traffic SET undo = 1 WHERE recordid = (SELECT MAX(recordid)\
                        FROM traffic WHERE undo = 0 AND locations = ? AND types = ? AND occupancy = ?)''', (location, vehicle_type, occupancy))
        
        db.commit()