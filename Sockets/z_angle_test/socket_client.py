#!python3.9
#import gps_calculations
from gps_calculations import calculate_desired_compass_bearing, calculate_distance_to_target, calculate_next_position


import socket
import serial
import time
import math

def move_coordinates(data: list) -> list:

    location = 51.896819, 4.338292
    elevation = 10

    # calculate next coordinates
    next_position = calculate_next_position(data)

    # calculate desired x angle
    x_angle = calculate_desired_compass_bearing(location,next_position)  #(loc, next)
    if(x_angle < 0): x_angle += 360

        # calculate distance to target
    distance = calculate_distance_to_target(location, next_position)
    print(distance)

        # calculate desired z angle
    z_angle = math.degrees(math.atan(distance/elevation))
    z_angle = 90 - z_angle 

        # apply offsets to x and z angles
    x_angle, z_angle = x_angle, z_angle
    angles = [x_angle, z_angle]

    #self.move(angles)

    return angles

        

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    lat = 51.896819 #51.8968268
    lon = 4.338410 #4.35375342
    speed = 8
    head = 1        

    signal = lat, lon, speed, head
    angles = move_coordinates(signal)
    print("main:")
    stri = str(angles[0]) + ";" + str(angles[1]) + '\n'
    print(stri)
