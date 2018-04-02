import SimpleHTTPServer
import BaseHTTPServer
import webbrowser

PORT = 8000

class MyHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def do_HEAD(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

	def do_GET(self):
		"""Respond to a GET request."""
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write("<html><head><title>Title goes here.</title></head>")
		self.wfile.write("<body><p>This is a test.</p>")
		
		self.wfile.write("<p>You accessed path: %s</p>" % self.path)
		self.wfile.write("</body></html>")
Handler = MyHTTPRequestHandler

httpd = SimpleHTTPServer.BaseHTTPServer.HTTPServer(("", PORT), Handler)

webbrowser.open("localhost:%i" %PORT)

print "serving at port", PORT
while True:
	httpd.handle_request()


# import code, rlcompleter -> maybe get that to work?
