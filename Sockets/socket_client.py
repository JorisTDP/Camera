#!python3.9
# echo-client.py

import socket
import serial
import time

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8001  # The port used by the server

arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1)

def write_read(x):
    arduino.write(bytes(x,'utf-8'))
    time.sleep(0.05)
    for i in range(10):
        data = arduino.readline()
        print (data)
    return data

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello, world")
    data = s.recv(1024)
    ndata = data.decode('utf-8')
    print (ndata)
    write_read(ndata)
    


