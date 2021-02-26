the files register.py and list.py are supposed to be used as cgi scripts by a webserver like eg. apache

make sure the webserver as permission to
- execute register.py
- execute list.py
- read and write database/
- read and write database/server.db

the script reset.py can be used to reset / initialize the database with the correct tables
make sure the webserver does not have permission to execute reset.py if you dont wan't other people to be able to reset your database
