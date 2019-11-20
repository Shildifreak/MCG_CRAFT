import sys, os, inspect, subprocess

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


path = os.path.join(PATH, "index.html")
path = os.path.abspath(path)

port = options.port
host = options.host

if sys.platform == "win32":
    url = 'file://"{}"?port={}&host={}'.format(path, port, host)
    browser = '"C:\\Program Files\\Mozilla Firefox\\firefox.exe"'
    command = " ".join([browser, url])
    
else:
    url = "file://{}?port={}&host={}".format(path, port, host)
    browser = "firefox"
    command = [browser, url]

#M# once it's using http:// instead of file:// switch from subprocess to webbrowser module for opening
subprocess.Popen(command)
