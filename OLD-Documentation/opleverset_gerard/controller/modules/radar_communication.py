#!python3.9
# Libraries used for socket communication
import socket
import select

class RadarCommunication():
    def __init__(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.ip = ip
        self.port = port

        self.connected = 0
        self.attempt_connection(self.ip, self.port)

    def attempt_connection(self, ip: str, port: int):
        try:
            self.socket.connect((ip, port))
            self.connected = 1
            self.data = b''
        except socket.error:
            self.connected = 0

    def get_message(self):
        if not self.connected: self.attempt_connection(self.ip, self.port)
        if not self.connected: return None

        try:
            ready = select.select([self.socket], [], [], 0.01)
            if ready[0]:
                return self.socket.recv(1024).decode('ascii')
            else:
                return None
        except socket.error:
            self.connected = 0

    def __del__(self):
        self.socket.shutdown()
        self.socket.close()


