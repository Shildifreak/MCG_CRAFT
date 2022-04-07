import sys, os, inspect, threading, time
import random
import http.server, webbrowser

PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(PATH,".."))

import client_utils
args = client_utils.parser.parse_args()
if not args.server_location:
    serverinfo = client_utils.get_serverinfo(args)
    args.server_location = "%s:%i" % (serverinfo["host"],
                                      serverinfo["http_port"])

url = "http://%s/webclient/latest" % args.server_location
url += "?server=%s&name=%s&password=%s" %(args.server_location,args.name,args.password)
url += "?rid=%i" %random.getrandbits(32) #avoid problems with browser caching
webbrowser.open(url)
