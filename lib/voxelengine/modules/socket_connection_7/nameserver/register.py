#!/usr/bin/python3

import time
import socket
import json
import os
import inspect
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

#import cgitb
#cgitb.enable()

import cgi
print("Content-Type: text/html")
print()

import cgi
form = cgi.FieldStorage()

if "uid" not in form:
	print("missing parameter 'uid'")
	exit(0)
if "key" not in form:
	print("missing parameter 'key'")
	exit(0)
if "value" not in form:
	print("missing parameter 'value'")
	exit(0)

ip = os.environ["REMOTE_ADDR"] #this variable should be set by caller of cgi script

uid   = form["uid"].value
key   = form["key"].value
value = form["value"].value

# validate data to be mcgcraft serverinfo
serverinfo = json.loads(value)
if not str(serverinfo["http_port"]).isdigit():
	print("port is not a natural number (%s)" % port)
	exit(0)
if ip != socket.gethostbyname(serverinfo["host"]):
	print("hostname does not resolve to request origin (%s)" % ip)
	exit(0)


import sqlite3
dbpath = os.path.join(PATH, "database", "server.db")
conn = sqlite3.connect(dbpath)
c = conn.cursor()

if False:
	# drop entries older than one minute
	c.execute('''DELETE FROM server
	             WHERE time < ?''', (time.time()-60,))

# Insert a row of data
c.execute("REPLACE INTO server VALUES (?,?,?,?)", (uid,key,value,time.time()))

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()

print("success")
