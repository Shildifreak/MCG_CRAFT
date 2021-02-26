#!/usr/bin/python3

import time
import json
import os, inspect
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
TTL = 60

#import cgitb
#cgitb.enable()
#print("Content-Type:text/html")
#print()

import cgi
form = cgi.FieldStorage()

if "key" in form:
	key = form["key"].value
else:
	key = "voxelgame"

import sqlite3
dbpath = os.path.join(PATH, "database", "server.db")
conn = sqlite3.connect(dbpath)
c = conn.cursor()

c.execute('''
SELECT * FROM server
WHERE time > ? AND key = ?
''',(time.time()-TTL, key))
output = json.dumps(tuple((uid,value) for uid, key, value, timestamp in c.fetchall()))
conn.close()

print("Content-Type: text/json")
print("Access-Control-Allow-Origin: *")
print()
print(output)

