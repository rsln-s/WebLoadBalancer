__author__ = 'ruslan'


import logging
import os.path
import socket
import sys
from thread import *

def parse_headers(request):
    """Return a dictionary in the form Header => Value for all headers in
    *request*."""
    headers = {}
    for line in request.split('\n')[1:]:
        # blank line separates headers from content
        if line == '\r':
            break
        header_line = line.partition(':')
        headers[header_line[0].lower()] = header_line[2].strip()
    return headers

class RSWebLoadBalancer:

    def __init__(self, incoming_port=8000):
        self.backend = 8888
        self.currentSessions = []
        self.incomingPort = incoming_port
        self.bufferLength = 8192
        self.debug = True

    def shutDown(self):
        sys.exit(0)

    def redirectRequest(self, connection, data, address):
        if self.debug:
            print("Trying to redirect")
        try:
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            send_socket.connect(('127.0.0.1', self.backend))
            send_socket.send(data)
            if self.debug:
                print("sent data:", data)
            while True:
                reply = send_socket.recv(self.bufferLength)
                if not reply:
                    break
                if len(reply) > 0:
                    connection.send(reply)
                    if self.debug:
                        print("received reply: ", reply)

            send_socket.close()
            connection.close()
        except socket.error, (value, message):
            print("Error while redirecting:", value, message)
            connection.close()
            send_socket.close()
            self.shutDown()

    def run(self):
        print 'WebLoadBalancer is running now'
        if self.debug:
            print("In debug mode")
        try:
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listen_socket.bind(('127.0.0.1', self.incomingPort))
            listen_socket.listen(1)
        except Exception, e:
            print('Unable to initialize Socket')
            self.shutDown()
        while True:
            try:
                connection, address = listen_socket.accept()
                data = connection.recv(self.bufferLength)
                headers = parse_headers(data)
                if len(data) == 0:
                    continue
                if self.debug:
                    print("Received data: ", data)
                if 'cookie' in headers:
                    cookies = {e.split('=')[0]: e.split('=')[1] for e in headers['cookie'].split(';')}
                    print'Found a cookie'
                start_new_thread(self.redirectRequest, (connection, data, address))
            except KeyboardInterrupt:
                print("quitting WebLoadBalancer")
                listen_socket.close()
                self.shutDown()