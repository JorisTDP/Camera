#!python3.9
import socket
import selectors
import select
import math
import time

class Communication():

    def __init__(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.ip = ip
        self.port = port
        self.data = b""
        self.messages = []

        self.socket.bind((ip, port))
        self.socket.listen()
        self.conn, self.addr = self.socket.accept()
        print(self.conn)
        print(f"Connected by {self.addr}")

    def re_init(self): # re-establish connection
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip, self.port))
        self.socket.listen()
        self.conn, self.addr = self.socket.accept()

    def send_input(self, input):
        #print(input)
        try:
            val = "+" + str(input)
            #print(val)
        except:
            print("err")

        encdata = val.encode("ascii") # encode string
        try:
            self.conn.sendall(encdata) # send offset to socket_client
        except:
            self.re_init() # if a error occurs, attempt to reconnect so socket
        print("sent message")

        

    def send_offset(self, offsetx, offsetz):
        print("sending offset: ")
        data = str(offsetx) + ";" + str(offsetz) # store x and z offset in string
        encdata = data.encode("ascii") # encode string

        try:
            self.conn.sendall(encdata) # send offset to socket_client
        except:
            self.re_init() # if a error occurs, attempt to reconnect so socket
        print("sent message")