#importing the required modules
import csv
import datetime
import sqlite3

#connecting to the database
db = sqlite3.connect('database.db')
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

        if add_undo == 'add':
            cursor.execute('''INSERT INTO traffic (username, locations, types, occupancy, time_added)\
                 VALUES (?, ?, ?, ?, ?)''', ('task8_user', location, vehicle_type, occupancy, time_added))
        else:
            cursor.execute('''UPDATE traffic SET undo = 1 WHERE recordid = (SELECT MAX(recordid)\
                        FROM traffic WHERE undo = 0 AND locations = ? AND types = ? AND occupancy = ?)''', (location, vehicle_type, occupancy))
        
        db.commit()