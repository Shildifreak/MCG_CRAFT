import os, inspect, threading, time
import http.server, webbrowser

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-H",
              "--host", dest="host",
              help="only consider servers on this HOST", metavar="HOST",
              action="store")
parser.add_option("-P",
              "--port", dest="port",
              help="only consider servers on this PORT", metavar="PORT", type="int",
              action="store")
parser.add_option(
              "--http_port", dest="http_port",
              help="server hosts http fileserver at this port", metavar="HTTP_PORT", type="int", default=80,
              action="store")
parser.add_option(
              "--parole", dest="parole",
              help="find servers with this parole", metavar="PAROLE", default="",
              action="store")
parser.add_option("-N",
              "--name", dest="name",
              help="use this name for playing on the server", metavar="NAME",
              action="store")
parser.add_option(
              "--password", dest="password",
              help="set a password to prevent others from connecting with your name", metavar="PASSWORD",
              action="store")
options, args = parser.parse_args()

port = options.port
host = options.host
url = "http://mcgcraft.de/webclient/latest?port=%s&host=%s&parole=%s&name=%s&password=%s" %(port,host,options.parole,options.name,options.password)
webbrowser.open(url) #maybe insert sleep before
