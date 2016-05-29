__author__ = 'ruslan'

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from RSWebLoadBalancer import *
from threading import Thread

class MockServerRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print("Mock server received smth")
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Hello from the mock server\n")


httpd = HTTPServer(('127.0.0.1', 8888), MockServerRequestHandler)
server_thread = Thread(target=httpd.serve_forever)
server_thread.daemon = True
server_thread.start()
print("Request handler is up")

b = RSWebLoadBalancer()
b.run()

httpd.shutdown()
