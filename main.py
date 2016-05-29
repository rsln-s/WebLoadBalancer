__author__ = 'ruslan'

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from RSWebLoadBalancer import *
from threading import Thread

class MockServerRequestHandler1(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Hello from the first mock server\n")


class MockServerRequestHandler2(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Hello from the second mock server\n")


httpd1 = HTTPServer(('127.0.0.1', 8888), MockServerRequestHandler1)
server_thread1 = Thread(target=httpd1.serve_forever)
server_thread1.daemon = True
server_thread1.start()

httpd2 = HTTPServer(('127.0.0.1', 8889), MockServerRequestHandler2)
server_thread2 = Thread(target=httpd2.serve_forever)
server_thread2.daemon = True
server_thread2.start()

print("Request handlers are up")

b = RSWebLoadBalancer()
b.run()

httpd1.shutdown()
httpd2.shutdown()

