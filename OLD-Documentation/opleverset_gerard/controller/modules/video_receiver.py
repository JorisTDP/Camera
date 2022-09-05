#!python3.9
# Libraries used for socket communication
import socket
import selectors
import select
import pickle
import struct

# Libraries used to send camera input
import cv2

class VideoReceiver():
    def __init__(self, ip: str, port: str):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.ip = ip
        self.port = port

        self.data = b""
        self.frame = None

        self.attempt_connection(ip, port)

        self.running = 1

    def attempt_connection(self, ip: str, port: str):
        try:
            self.socket.__init__(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip, port))
            self.connected = 1
        except socket.error:
            self.connected = 0

    def main_loop(self):
        while self.running:
            # While not connected the client should continue to attempt a connection.
            if not self.connected:
                self.attempt_connection(self.ip, self.port)

            ready = select.select([self.socket], [], [], 0.01)
            if ready[0]:
                try:
                    frame = self.parse_new_frame(self.socket)
                    if(type(frame) != type(None)): self.frame = frame

                except socket.error:
                    self.connected = 0

    def parse_new_frame(self, socket: socket.socket):
        data = self.data

        # Wait for the payload with the frame size to be fully sent
        payload_size = struct.calcsize("I")
        while len(data) < payload_size:
            data += socket.recv(4096)

        # Get frame size from the payload and remove it from the current data
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]

        # Wait for the frame to be fully sent
        msg_size = struct.unpack("I", packed_msg_size)[0]
        while len(data) < msg_size:
            data += socket.recv(4096)

        # Put relevant data in frame_data and remove converted message from the data
        frame_data = data[:msg_size]
        self.data = data[msg_size:]

        frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        return cv2.imdecode(frame, cv2.IMREAD_COLOR)
    
    def __del__(self):
        self.running = 0
        self.socket.close()