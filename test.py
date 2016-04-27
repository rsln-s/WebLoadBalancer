from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import requests
import pexpect
from threading import Thread

RSP_BINARY = '/Users/ruslan/dev/networks_task/WebLoadBalancer/main'

class MockServerRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Hello from the mock server\n")


httpd = HTTPServer(('127.0.0.1', 8888), MockServerRequestHandler)
server_thread = Thread(target=httpd.serve_forever)
server_thread.daemon = True
server_thread.start()
print("Request handler is up")

server = pexpect.spawn(RSP_BINARY, ["8000", "127.0.0.1", "8888"])
server.expect("Started.  Listening on port 8000.")

response = requests.get("http://127.0.0.1:8000")
print(response.text, response.status_code)

server.kill(9)
httpd.shutdown()
