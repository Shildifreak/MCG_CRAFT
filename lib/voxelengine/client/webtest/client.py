import sys, os, inspect, threading, time
import random
import webbrowser
import urllib.parse

PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(PATH,".."))

import client_utils
args = client_utils.parser.parse_args()
if not args.server_location:
    serverinfo = client_utils.get_serverinfo(args)
    args.server_location = "%s:%i" % (serverinfo["host"],
                                      serverinfo["http_port"])

url = "http://%s/webclient/latest" % args.server_location
query = {
    "server":args.server_location,
    "name": args.name,
    "password":args.password,
    "rid":random.getrandbits(32), #avoid problems with browser caching
}
query_string = urllib.parse.urlencode(query)

webbrowser.open(url+"?"+query_string)
