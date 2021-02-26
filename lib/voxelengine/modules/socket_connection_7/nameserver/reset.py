import sys
if not (len(sys.argv) > 1 and sys.argv[1] == "--reset"):
	print("please call with reset.py --reset")
	sys.exit(1)

import os
import inspect
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
dbpath = os.path.join(PATH, "database", "server.db")

with open(dbpath, "w"):
	pass

import sqlite3
conn = sqlite3.connect(dbpath)
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE server
				 (uid integer, key text, value text, time real, PRIMARY KEY (uid))''')

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()

print("success")
