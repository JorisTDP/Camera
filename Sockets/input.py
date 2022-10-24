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


    def attempt_connection(self, ip: str, port: str):
        try:
            self.socket.connect((ip, port))
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.connected = 1
            self.data = b''
        except socket.error:
            self.connected = 0
    
    def message_amount(self) -> int:
        return len(self.get_messages())

    def re_init(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.bind((self.ip, self.port))
        self.socket.listen()
        self.conn, self.addr = self.socket.accept()


    def send_offset(self, offset):
        #try:
        self.re_init()
        with self.conn:
            print("sending offset: ")
            print(offset)
            print(self.conn)
            #self.socket.sendall(b"Hello World")
            self.conn.sendall(bytes(offset))
            print("sent message")
        #except socket.error:
            #print(socket.error)