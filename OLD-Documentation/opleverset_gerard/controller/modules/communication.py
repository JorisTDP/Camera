#!python3.9
# Libraries used for socket communication
import socket
import selectors
import select
import pickle
import struct

from .message import Message
from queue import Queue

class Communication():
    """
    Communication class that handles socket connections between scripts.

    ...

    Attributes
    ----------
    socket : socket
        The socket connection used in client mode

    ip : str
        IP the socket is connected to or is listening on

    port : str
        Port the socket is connected to or is listening on

    server_mode : bool
        Determines wether the communication functions in server or client mode

    data : bytes
        Stores the bytes being send by the server in client mode

    messages : Queue
        A queue containing unhandled messages that have been received

    selector : DefaultSelector
        Server mode only! Used to keep track of incoming connections.
        
    connected_clients : dict
        Server mode only! A dictionary containing all of the currently connected
        clients and their respective bytes for data storage

    Methods
    -------
    pop_message()
        Checks for new messages and returns the last message of the queue or None
    
    send_message(message)
        Sends a message object to all connected clients or the server depending
        on wether server mode is enabled
    """

    def __init__(self, ip: str, port: int, server_mode: bool):
        """
        Parameters
        ----------
        ip : str
            IP the socket is connected to or is listening on

        port : str
            Port the socket is connected to or is listening on

        server_mode : bool
            Wether the socket should operate in server or client mode
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_mode = server_mode

        self.ip = ip
        self.port = port

        self.data = b""
        self.messages = []

        if(server_mode):
            self.socket.bind((ip, port))
            self.socket.listen()

            self.selector = selectors.DefaultSelector()
            self.selector.register(self.socket, selectors.EVENT_READ, data=None)

            self.connected_clients = {}
        else:
            self.attempt_connection(ip, port)

    def attempt_connection(self, ip: str, port: str):
        try:
            self.socket.connect((ip, port))
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.connected = 1
            self.data = b''
        except socket.error:
            self.connected = 0
    
    def __del__(self):
        self.send_message(Message("shutdown", []))
    
        self.socket.close()

    # Getting messages
    def pop_message(self) -> Message:
        self.get_messages()

        if len(self.messages) > 0:
            return self.messages.pop(0)
        else:
            return None
    
    def message_amount(self) -> int:
        return len(self.get_messages())

    def get_messages(self):
        # Check for new incoming messages before sending back the queue.
        if(self.server_mode):
            self.get_messages_server()
        else:
            self.get_messages_client()

        return list(self.messages).copy()

    def get_messages_server(self):
        self.check_connections_server()

        for client in list(self.connected_clients.keys()):
            # Probe the connection to ensure it is still up.

            ready = select.select([client], [], [], 0.01)
            if ready[0]:
                try:
                    message = self.parse_new_message(client, self.connected_clients[client])

                    if message:
                        if not message.name == 'shutdown': 
                            self.messages.append(message)
                        else:
                            del self.connected_clients[client]
                except socket.error as err:
                    del self.connected_clients[client]
                    print("server error in get_messages_server:\n", err)

    def get_messages_client(self):
        if not self.connected: self.attempt_connection(self.ip, self.port)
        if not self.connected: return

        ready = select.select([self.socket], [], [], 0.01)
        if ready[0]:
            try:
                message = self.parse_new_message(self.socket, self.data)
                print(message)
                if message and not message.name == 'probe': self.messages.append(message)

            except socket.error as err:
                self.connected = 0
                print("client error in get_messages_client:\n", err)

    def parse_new_message(self, socket: socket.socket, data: bytes) -> Message:
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

        message = Message.from_bytes(data[:msg_size])
        if self.server_mode: self.connected_clients[socket] = data[msg_size:]
        else: self.data = data[msg_size:]
        
        return message
        
                
    # Sending messages:
    
    def send_message(self, message: Message):
        # Encode the message into bytes that can be sent.
        message = message.encode()

        if(self.server_mode):
            return self.send_message_server(message)
        else:
            return self.send_message_client(message)

    def send_message_server(self, message: bytes):
        self.check_connections_server()

        for client in list(self.connected_clients.keys()):
            # Get message size
            size = len(message)

            try:
                # Send message with struct telling the listening end how long
                # the sent message is.
                client.sendall(struct.pack("I", size) + message)
            except socket.error:
                del self.connected_clients[client]

    def send_message_client(self, message: bytes):
        if not self.connected: self.attempt_connection(self.ip, self.port)
        if not self.connected: raise(NotConnectedError())

        size = len(message)

        try:
            # Send message with struct telling the listening end how long
            # the sent message is.
            self.socket.sendall(struct.pack("I", size) + message)
        except socket.error:
            self.connected = 0


    # Utility methods

    def check_connections_server(self):
        events = self.selector.select(timeout=0.01)
        for key, mask in events:
            if key.data is None:
                conn, addr = self.socket.accept()  # Should be ready to read
                conn.setblocking(0)
                self.connected_clients = {**self.connected_clients, conn: b""}

    def probe_connection(self, client):
        message = Message('probe', []).encode()
        size = len(message)
        try:
            # Send message with struct telling the listening end how long
            # the sent message is.
            client.sendall(struct.pack("I", size) + message)
            return 1
        except socket.error:
            if self.server_mode:
                del self.connected_clients[client]
            else:
                self.connected = 0
            return 0


class NotConnectedError(Exception):
    def __init__(self):
        super().__init__("Commmunication client is not connected! Make sure the settings are correct and a server is running!")