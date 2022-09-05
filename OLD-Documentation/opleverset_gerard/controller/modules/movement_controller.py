#!python3.9
from .gps_calculations import calculate_desired_compass_bearing, calculate_distance_to_target, calculate_next_position

import math

# Serial used for communication with the Arduino
import serial

class MovementController():
    """
    Message class for communication and event management

    ...

    Methods
    -------
    move(angles)
        Tells the microcontroller over Serial to move to new angles

    move_coordinates(data, offsets)
        Calculates angles based on target data and offsets then moves
    """

    def __init__(self, com_port: str, location: 'list[int]', x_offset: int, elevation: int):

        self.location = tuple(location)
        self.x_offset = x_offset
        self.elevation = elevation

        self.com_port = com_port

        self.attempt_connection()

    def attempt_connection(self):
        try:
            self.ser = serial.Serial(self.com_port, 115200, timeout=10, rtscts=True)
        except serial.SerialException:
            print("Serial connection failed!")
            self.ser = None

    def reset_connection(self):
        self.ser.close()

        self.attempt_connection()

    def connected(self):
        if self.ser:
            return 1
        else:
            return 0

    def move(self, angles: list):
        if not self.ser: self.attempt_connection()
        if not self.ser: return

        print("Sending: ", str(angles[0]) + ';' + str(angles[1]))
        self.ser.write((str(angles[0]) + ';' + str(angles[1]) + '\n').encode())
        print("Sent angles over serial")

    def move_coordinates(self, data: list, offsets: list) -> list:
        target = tuple(float(val) for val in data)

        # calculate next coordinates
        next_position = calculate_next_position(target)

        # calculate desired x angle
        x_angle = calculate_desired_compass_bearing(self.location, next_position)
        x_angle -= self.x_offset
        if(x_angle < 0): x_angle += 360

        # calculate distance to target
        distance = calculate_distance_to_target(self.location, next_position)

        # calculate desired z angle
        z_angle = math.degrees(math.atan(distance/self.elevation))

        # apply offsets to x and z angles
        x_angle, z_angle = x_angle + offsets[0], z_angle + offsets[1]
        angles = [x_angle, z_angle]

        self.move(angles)

        return angles

    def __del__(self):
        self.ser.close()

