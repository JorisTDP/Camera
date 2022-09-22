#!python3.9
#import gps_calculations
from gps_calculations import calculate_desired_compass_bearing, calculate_distance_to_target, calculate_next_position


import socket
import serial
import time
import math


HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8001  # The port used by the server
i = 0

arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1)

def write_read(x):
    arduino.write(bytes(x,'utf-8'))
    time.sleep(0.05)
    for i in range(2):
        data = arduino.readline()
        print (data.decode('utf-8'))
    return data   

def move_coordinates(data: list, offsets: list) -> list:

    location = 51.896819, 4.338292
    elevation = 20

    # calculate next coordinates
    next_position = calculate_next_position(data)

    # calculate desired x angle
    x_angle = calculate_desired_compass_bearing(location,next_position)  #(loc, next)
    x_angle -= 0 #x_offset
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
        list = ndata.split(',')
        lat, lon, speed, head = [float(i) for i in list]
        signal = lat, lon, speed, head
        offset = 2, 3
        angles = move_coordinates(signal, offset)
        #angles[0] -= i
        # if(i > 90):
        #     i -= 5
        # else:
        #     i += 5
        stri = "359.000;0.000 " + '\n'
        #stri = str(angles[0]) + ";" + str(angles[1]) + '\n'
        print(stri)
        write_read(stri)
    


