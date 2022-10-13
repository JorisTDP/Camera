#!python3.9
# Libraries used for socket communication
import socket
import selectors
import select
import pickle
import struct

# Libraries used to send camera input
import cv2

class VideoSender():
    def __init__(self, ip: str, port: str, capture_device: int):
        # Start the videocapture to be able to get frames from the camera.
        self.capture_device = capture_device
        self.camera = cv2.VideoCapture(capture_device)
        print("CAPTURE DEVICE")
        print(capture_device)
        self.camera.set(3, 1280)
        self.camera.set(4, 720)

        # Set up the socket and all required variables.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.bind((ip, port))
        self.socket.listen()

        self.selector = selectors.DefaultSelector()
        self.selector.register(self.socket, selectors.EVENT_READ, data=None)

        self.connected_clients = []

        self.running = 1

    def main_loop(self):
        while self.running:
            self.check_connections_server()

            # If there are no clients there is no use in wasting resources capturing
            # the frame from the camera.
            if len(self.connected_clients) < 1: continue

            # Capture and encode the camera frame
            try:
                ret, frame = self.camera.read()
                result, frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            except cv2.error:
                # Restart videocapture to hopefully avoid future issues.
                self.camera.release()
                self.camera = cv2.VideoCapture(self.capture_device)
                self.camera.set(3, 1280)
                self.camera.set(4, 720)

                continue

            # Turn frame into data using pickle so it can be easily decoded after
            # being sent to the user interface.
            data = pickle.dumps(frame, 0)
            size = len(data)

            # Send frame to each client
            for client in self.connected_clients:
                try:
                    client.sendall(struct.pack("I", size) + data)
                except socket.error:
                    # If the socket raises an error the most likely reason is the
                    # client has disconnected, therefore we remove them from the list
                    # of connected clients.
                    self.connected_clients.remove(client)
        
        self.camera.release()
        self.socket.close()
                

    
    def check_connections_server(self):
        events = self.selector.select(timeout=0.01)
        for key, mask in events:
            if key.data is None:
                conn, addr = self.socket.accept()  # Should be ready to read
                self.connected_clients += [conn]

    def __del__(self):
        self.running = 0

class NotConnectedError(Exception):
    def __init__(self):
        super().__init__("Commmunication client is not connected! Make sure the settings are correct and a server is running!")