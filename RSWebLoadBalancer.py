__author__ = 'ruslan'


import logging
import requests
import os.path
import random
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

    def __init__(self, debug=True, incoming_port=8000):
        self.backend = [8888, 8889]
        self.currentSessions = []
        self.incomingPort = incoming_port
        self.bufferLength = 4092
        self.debug = debug

        #check that all of the backend is up
        for port in self.backend:
            try:
                requests.get("http://127.0.0.1:" + str(port))
            except requests.exceptions.RequestException as e:
                if self.debug:
                    print e
                print("Server at port ", port, " is down")

    def shutDown(self):
        sys.exit(0)

    def redirectRequest(self, connection, data, session_port):
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #check that session port in cookie exists
        if int(session_port) == -1:
            backend_port_to_connect = self.backend[0]
            load = 21
            #find the one with the least load
            for port in self.backend:
                try:
                    reply = requests.get("http://127.0.0.1:" + str(port))
                    if load > int(reply.headers["Load"]):
                        load = int(reply.headers["Load"])
                        backend_port_to_connect = port
                        if self.debug:
                            print("Updated load: ", load, " New backend: ", backend_port_to_connect)
                except requests.exceptions.RequestException as e:
                    if self.debug:
                        print e
                    print("Server at port ", port, " is down")

        elif int(session_port) not in self.backend:
            print(session_port, " not found in the list of backend servers: ", self.backend)
            send_socket.close()
            connection.send('Server you are looking for does not exist')
            connection.close()
            return
        else:
            backend_port_to_connect = int(session_port)

        if self.debug:
            print("Trying to redirect")

        #check if backend server is alive
        try:
            requests.get("http://127.0.0.1:" + str(backend_port_to_connect))
        except requests.exceptions.RequestException as e:
            if self.debug:
                print e
            print("Server at port ", backend_port_to_connect, " is down")
            send_socket.close()
            connection.send('Server you are looking for is down')
            connection.close()
            return

        try:
            send_socket.connect(('127.0.0.1', backend_port_to_connect))
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
                session_port = -1
                if len(data) == 0:
                    continue
                if self.debug:
                    print("Received data: ", data)
                if 'cookie' in headers:
                    cookies = {e.split('=')[0]: e.split('=')[1] for e in headers['cookie'].split(';')}
                    if self.debug:
                        print'Found a cookie'
                    if 'SessionID' in cookies:
                        if self.debug:
                            print ("Found SessionID = ", cookies['SessionID'])
                        session_port = cookies['SessionID']
                start_new_thread(self.redirectRequest, (connection, data, session_port))
            except KeyboardInterrupt:
                print("quitting WebLoadBalancer")
                listen_socket.close()
                self.shutDown()