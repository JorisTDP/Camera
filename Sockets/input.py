#!python3.9
import socket
import selectors
import select

class Communication():

    def __init__(self, ip: str, port: int):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.ip = ip
        self.port = port

        self.data = b""
        self.messages = []


        self.socket.bind((ip, port))
        self.socket.listen()


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


    def send_offset(self, offset):
        try:
            self.socket.sendall(offset)
        except socket.error:
            print(socket.error)
