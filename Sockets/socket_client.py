#!python3.9
#import gps_calculations
from gps_calculations import calculate_desired_compass_bearing, calculate_distance_to_target, calculate_next_position


import socket
import serial
import time
import math


HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8001  # The port used by the server

#arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1)

def write_read(x):
    arduino.write(bytes(x,'utf-8'))
    time.sleep(0.05)
    for i in range(2):
        data = arduino.readline()
        print (data)
    return data 

def move_coordinates(data: list, offsets: list) -> list:

    location = (52.3993, 4.39294)
    elevation = 1

    # calculate next coordinates
    next_position = calculate_next_position(data)

    # calculate desired x angle
    x_angle = calculate_desired_compass_bearing(location, next_position)
    x_angle -= 3 #x_offset
    if(x_angle < 0): x_angle += 360

        # calculate distance to target
    distance = calculate_distance_to_target(location, next_position)

        # calculate desired z angle
    z_angle = math.degrees(math.atan(distance/elevation))

        # apply offsets to x and z angles
    x_angle, z_angle = x_angle + offsets[0], z_angle + offsets[1]
    angles = [x_angle, z_angle]

    #self.move(angles)

    return angles


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello, world")
    while True:
        data = s.recv(1024)
        ndata = data.decode('utf-8')
        #datan = __str__(ndata)
        list = ndata.split(',')
        lat, lon, speed, head = [float(i) for i in list]
        signal = lat, lon, speed, head
        offset = 2, 3
        print(move_coordinates(signal, offset))
        #write_read(ndata)
    


