import sqlite3
import hashlib

def database_creation(name):

    db = sqlite3.connect(name)
    cursor = db.cursor()

    #creating the table for storing logins and password
    cursor.execute('''CREATE TABLE IF NOT EXISTS logins (
        usernames TEXT PRIMARY KEY,
        passwords TEXT
        )''')

    #creating the tables for monitoring start and end sessions
    cursor.execute('''CREATE TABLE IF NOT EXISTS loginsession (
        sessionid INTEGER PRIMARY KEY,
        username TEXT,
        start_time DATETIME,
        end_time DATETIME,
        token TEXT
        )''')

    #creating the table for storing traffic
    cursor.execute('''CREATE TABLE IF NOT EXISTS traffic (
        recordid INTEGER PRIMARY KEY,
        username TEXT,
        locations TEXT,
        types TEXT,
        occupancy INTEGER,
        time_added DATETIME,
        token TEXT,
        undo INTEGER DEFAULT 0
        )''')

    usernames = ['test1', 'test2', 'test3', 'test4', 'test5', 'test6', 'test7', 'test8', 'test9', 'test10']
    passwords = ['password1', 'password2', 'password3', 'password4', 'password5', 'password6', 'password7', 'password8', 'password9', 'password10']

    def hash_pwd(password):
        #hash the password
        hashing_password = hashlib.sha512(password.encode('utf-8'))
        return hashing_password.hexdigest()

    #hashes the usernames and passwords
    hashed_pwds = [hash_pwd(pwd) for pwd in passwords]
    user_hash = list(zip(usernames, hashed_pwds))
    #populates the table of logins
    try:
        cursor.executemany("""INSERT INTO logins VALUES (?, ?)""", user_hash)
    except:
        pass
    db.commit()