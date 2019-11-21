import os, inspect, threading, time
import http.server, webbrowser

# PATH to this file
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

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
options, args = parser.parse_args()

port = options.port
host = options.host
http_port = 8080

print("serving page from",PATH)
os.chdir(PATH)
# just serve index.html from current working directory
Handler = http.server.SimpleHTTPRequestHandler
httpd = http.server.HTTPServer(("", http_port), Handler)
http_thread = threading.Thread(target=httpd.serve_forever)

http_thread.start()
url = "http://localhost:%i?port=%s&host=%s" %(http_port,port,host)
webbrowser.open(url) #maybe insert sleep before

time.sleep(10)

httpd.shutdown()
http_thread.join()
