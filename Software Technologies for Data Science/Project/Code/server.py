#!/usr/bin/env python

# This is a simple web server for a traffic counting application.
# It's your job to extend it by adding the backend functionality to support
# recording the traffic in a SQL database. You will also need to support
# some predefined users and access/session control. You should only
# need to extend this file. The client side code (html, javascript and css)
# is complete and does not require editing or detailed understanding.

# import the various libraries needed
import http.cookies as Cookie # some cookie handling support
from http.server import BaseHTTPRequestHandler, HTTPServer # the heavy lifting of the web server
import urllib # some url parsing support
import base64 # some encoding support
import sqlite3 # used to create the database
import hashlib #used to help has the passwords and check them in the login tables
from datetime import datetime #using datetime for records

#Task 1: Creating the SQL Database
#creating the database and referencing to it
db = sqlite3.connect('initial_database.db')
cursor = db.cursor()

cursor.execute('''DROP TABLE IF EXISTS logins''')
cursor.execute('''DROP TABLE IF EXISTS loginsession''')
cursor.execute('''DROP TABLE IF EXISTS traffic''')
db.commit()

#creating the table for storing logins and password
cursor.execute('''CREATE TABLE logins (
    usernames TEXT PRIMARY KEY,
    passwords TEXT NOT NULL
    )''')

#creating the tables for monitoring start and end sessions
cursor.execute('''CREATE TABLE loginsession (
    sessionid INTEGER PRIMARY KEY,
    username TEXT,
    start_time DATETIME,
    end_time DATETIME,
    token TEXT
    )''')

#creating the table for storing traffic
cursor.execute('''CREATE TABLE traffic (
    recordid INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    locations TEXT NOT NULL,
    types TEXT NOT NULL,
    occupancy INTEGER NOT NULL,
    recording_times DATETIME NOT NULL
    )''')

#committing to the database
db.commit()

#storing the usernames and passwords in the logins table
usernames = ['test1', 'test2', 'test3', 'test4', 'test5', 'test6', 'test7', 'test8', 'test9', 'test10']
passwords = ['password1', 'password2', 'password3', 'password4', 'password5', 'password6', 'password7', 'password8', 'password9', 'password10']

#hashing function
def hash_pwd(password):
    #hash the password
    hashing_password = hashlib.sha512(password.encode('utf-8'))
    return hashing_password.hexdigest()
 
#checking function
def verify_password(stored_password, provided_password):
    return stored_password == hash_pwd(provided_password)

#hashes the usernames and passwords
hashed_pwds = [hash_pwd(pwd) for pwd in passwords]
user_hash = list(zip(usernames, hashed_pwds))

#populates the table of logins
cursor.executemany("""INSERT INTO logins VALUES (?, ?)""", user_hash)
db.commit()

# This function builds a refill action that allows part of the
# currently loaded page to be replaced.
def build_response_refill(where, what):
    text = "<action>\n"
    text += "<type>refill</type>\n"
    text += "<where>"+where+"</where>\n"
    m = base64.b64encode(bytes(what, 'ascii'))
    text += "<what>"+str(m, 'ascii')+"</what>\n"
    text += "</action>\n"
    return text


# This function builds the page redirection action
# It indicates which page the client should fetch.
# If this action is used, only one instance of it should
# contained in the response and there should be no refill action.
def build_response_redirect(where):
    text = "<action>\n"
    text += "<type>redirect</type>\n"
    text += "<where>"+where+"</where>\n"
    text += "</action>\n"
    return text

## Decide if the combination of user and magic is valid
def handle_validate(iuser, imagic):
    if (iuser == 'test') and (imagic == '1234567890'):
        return True
    else:
        return False

## remove the combination of user and magic from the data base, ending the login
def handle_delete_session(iuser, imagic):
    return

## A user has supplied a username (parameters['usernameinput'][0])
## and password (parameters['passwordinput'][0]) check if these are
## valid and if so, create a suitable session record in the database
## with a random magic identifier that is returned.
## Return the username, magic identifier and the response action set.
def handle_login_request(iuser, imagic, parameters):
    if handle_validate(iuser, imagic) == True:
        # the user is already logged in, so end the existing session.
        handle_delete_session(iuser, imagic)

    text = "<response>\n"

    #checking for empty inputs for password or usernames
    if 'passwordinput' not in parameters or 'usernameinput' not in parameters:
        text += build_response_refill('message', 'Invalid password')
        user = '!'
        magic = ''
        text += "</response>\n"
        return [user, magic, text]

    #checking non empty inputs against table
    username = parameters['usernameinput'][0]
    given_password = parameters['passwordinput'][0]

    cursor.execute('''SELECT passwords FROM logins WHERE usernames = ?;''', (username,))
    db_password = (cursor.fetchone()[0])

    if verify_password(db_password, given_password):
        cursor.execute('''INSERT INTO loginsession (username, start_time) VALUES (?, ?)''', (username, datetime.now()))
        db.commit()
        text += build_response_redirect('/page.html')
        user = 'test'
        magic = '1234567890'
    else: ## The user is not valid
        text += build_response_refill('message', 'Invalid password')
        user = '!'
        magic = ''
    text += "</response>\n"
    return [user, magic, text]

## The user has requested a vehicle be added to the count
## parameters['locationinput'][0] the location to be recorded
## parameters['occupancyinput'][0] the occupant count to be recorded
## parameters['typeinput'][0] the type to be recorded
## Return the username, magic identifier (these can be empty  strings) and the response action set.
def handle_add_request(iuser, imagic, parameters):
    text = "<response>\n"
    if handle_validate(iuser, imagic) != True:
        #Invalid sessions redirect to login
        text += build_response_redirect('/index.html')
    else: ## a valid session so process the addition of the entry.
        text += build_response_refill('message', 'Entry added.')
        text += build_response_refill('total', '0')
    text += "</response>\n"
    user = ''
    magic = ''
    return [user, magic, text]

## The user has requested a vehicle be removed from the count
## This is intended to allow counters to correct errors.
## parameters['locationinput'][0] the location to be recorded
## parameters['occupancyinput'][0] the occupant count to be recorded
## parameters['typeinput'][0] the type to be recorded
## Return the username, magic identifier (these can be empty  strings) and the response action set.
def handle_undo_request(iuser, imagic, parameters):
    text = "<response>\n"
    if handle_validate(iuser, imagic) != True:
        #Invalid sessions redirect to login
        text += build_response_redirect('/index.html')
    else: ## a valid session so process the recording of the entry.
        text += build_response_refill('message', 'Entry Un-done.')
        text += build_response_refill('total', '0')
    text += "</response>\n"
    user = ''
    magic = ''
    return [user, magic, text]

# This code handles the selection of the back button on the record form (page.html)
# You will only need to modify this code if you make changes elsewhere that break its behaviour
def handle_back_request(iuser, imagic, parameters):
    text = "<response>\n"
    if handle_validate(iuser, imagic) != True:
        text += build_response_redirect('/index.html')
    else:
        text += build_response_redirect('/summary.html')
    text += "</response>\n"
    user = ''
    magic = ''
    return [user, magic, text]

## This code handles the selection of the logout button on the summary page (summary.html)
## You will need to ensure the end of the session is recorded in the database
## And that the session magic is revoked.
def handle_logout_request(iuser, imagic, parameters):

    cursor.execute('''UPDATE loginsession SET end_time = ? WHERE username = ?''', (datetime.now(), 'test1'))
    db.commit()
    text = "<response>\n"
    text += build_response_redirect('/index.html')
    user = '!'
    magic = ''
    text += "</response>\n"
    return [user, magic, text]

## This code handles a request for update to the session summary values.
## You will need to extract this information from the database.
def handle_summary_request(iuser, imagic, parameters):
    text = "<response>\n"
    if handle_validate(iuser, imagic) != True:
        text += build_response_redirect('/index.html')
    else:
        text += build_response_refill('sum_car', '0')
        text += build_response_refill('sum_taxi', '0')
        text += build_response_refill('sum_bus', '0')
        text += build_response_refill('sum_motorbike', '0')
        text += build_response_refill('sum_bicycle', '0')
        text += build_response_refill('sum_van', '0')
        text += build_response_refill('sum_truck', '0')
        text += build_response_refill('sum_other', '0')
        text += build_response_refill('total', '0')
        text += "</response>\n"
        user = ''
        magic = ''
    return [user, magic, text]


# HTTPRequestHandler class
class myHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    # GET This function responds to GET requests to the web server.
    def do_GET(self):

        # The set_cookies function adds/updates two cookies returned with a webpage.
        # These identify the user who is logged in. The first parameter identifies the user
        # and the second should be used to verify the login session.
        def set_cookies(x, user, magic):
            ucookie = Cookie.SimpleCookie()
            ucookie['u_cookie'] = user
            x.send_header("Set-Cookie", ucookie.output(header='', sep=''))
            mcookie = Cookie.SimpleCookie()
            mcookie['m_cookie'] = magic
            x.send_header("Set-Cookie", mcookie.output(header='', sep=''))

        # The get_cookies function returns the values of the user and magic cookies if they exist
        # it returns empty strings if they do not.
        def get_cookies(source):
            rcookies = Cookie.SimpleCookie(source.headers.get('Cookie'))
            user = ''
            magic = ''
            for keyc, valuec in rcookies.items():
                if keyc == 'u_cookie':
                    user = valuec.value
                if keyc == 'm_cookie':
                    magic = valuec.value
            return [user, magic]

        # Fetch the cookies that arrived with the GET request
        # The identify the user session.
        user_magic = get_cookies(self)

        print(user_magic)

        # Parse the GET request to identify the file requested and the GET parameters
        parsed_path = urllib.parse.urlparse(self.path)

        # Decided what to do based on the file requested.

        # Return a CSS (Cascading Style Sheet) file.
        # These tell the web client how the page should appear.
        if self.path.startswith('/css'):
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('.'+self.path, 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # Return a Javascript file.
        # These tell contain code that the web client can execute.
        if self.path.startswith('/js'):
            self.send_response(200)
            self.send_header('Content-type', 'text/js')
            self.end_headers()
            with open('.'+self.path, 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # A special case of '/' means return the index.html (homepage)
        # of a website
        elif parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('./index.html', 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # Return html pages.
        elif parsed_path.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('.'+parsed_path.path, 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # The special file 'action' is not a real file, it indicates an action
        # we wish the server to execute.
        elif parsed_path.path == '/action':
            self.send_response(200) #respond that this is a valid page request
            # extract the parameters from the GET request.
            # These are passed to the handlers.
            parameters = urllib.parse.parse_qs(parsed_path.query)

            if 'command' in parameters:
                # check if one of the parameters was 'command'
                # If it is, identify which command and call the appropriate handler function.
                if parameters['command'][0] == 'login':
                    [user, magic, text] = handle_login_request(user_magic[0], user_magic[1], parameters)
                    #The result to a login attempt will be to set
                    #the cookies to identify the session.
                    set_cookies(self, user, magic)
                elif parameters['command'][0] == 'add':
                    [user, magic, text] = handle_add_request(user_magic[0], user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'undo':
                    [user, magic, text] = handle_undo_request(user_magic[0], user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'back':
                    [user, magic, text] = handle_back_request(user_magic[0], user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'summary':
                    [user, magic, text] = handle_summary_request(user_magic[0], user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'logout':
                    [user, magic, text] = handle_logout_request(user_magic[0], user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                else:
                    # The command was not recognised, report that to the user.
                    text = "<response>\n"
                    text += build_response_refill('message', 'Internal Error: Command not recognised.')
                    text += "</response>\n"

            else:
                # There was no command present, report that to the user.
                text = "<response>\n"
                text += build_response_refill('message', 'Internal Error: Command not found.')
                text += "</response>\n"
            self.send_header('Content-type', 'application/xml')
            self.end_headers()
            self.wfile.write(bytes(text, 'utf-8'))
        else:
            # A file that does n't fit one of the patterns above was requested.
            self.send_response(404)
            self.end_headers()
        return

# This is the entry point function to this code.
def run():
    print('starting server...')
    ## You can add any extra start up code here
    # Server settings
    # Choose port 8081 over port 80, which is normally used for a http server
    server_address = ('127.0.0.1', 8081)
    httpd = HTTPServer(server_address, myHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever() # This function will not return till the server is aborted.

run()



