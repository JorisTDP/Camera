#!python3.9
#import gps_calculations
from gps_calculations import calculate_desired_compass_bearing, calculate_distance_to_target, calculate_next_position


import socket
import serial
import time
import threading
import math

HOST = "127.0.0.1"  # The server's hostname or IP address
RADARPORT = 8001  # The port used by the server
CAMERAPORT = 8002
i = 0

arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1)

class SocketClient:

    def __init__(self):
        self.cam = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cam.connect((HOST, CAMERAPORT))
        self.s.connect((HOST, RADARPORT))
        self.s.sendall(b"Hello, world")
        self.cam.sendall(b"Hello, world")
        self.signal = 1,1,1,1,1,1
        self.offset = 0, 0
        self.angles = [0,0]

    def write_read(self, x):
        arduino.write(bytes(x,'utf-8'))
        time.sleep(0.05)
        for i in range(2):
            data = arduino.readline()
            print (data.decode('utf-8'))
        return data   

    def move_coordinates(self, data: list, offsets: list) -> list:

        location = float(data[4]), float(data[5])
        #location = 51.896819, 4.338292
        elevation = 1

        # calculate next coordinates
        next_position = calculate_next_position(data)

        # calculate desired x angle
        x_angle = calculate_desired_compass_bearing(location,next_position)  #(loc, next)
        #x_angle -= offsets[0] #x_offset
        if(x_angle < 0): x_angle += 360

            # calculate distance to target
        distance = calculate_distance_to_target(location, next_position)

            # calculate desired z angle
        z_angle = math.degrees(math.atan(distance/elevation))
        z_angle = 90 - z_angle ###later weghalen !!!!!!!!!!

            # apply offsets to x and z angles
        print(" x offset ===")
        print(offsets[0])
        x_angle, z_angle = x_angle + int(offsets[0]), z_angle + int(offsets[1])
        angles = [x_angle, z_angle]

        #self.move(angles)

        return angles

        # cam = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # cam.connect((HOST, CAMERAPORT))
        # cam.sendall(b"Hello, world")
        # data = cam.recv(1024)        

    def receiveOffset(self):
        try:
            print("camdata:")
            camdata = self.cam.recv(1024).decode()
            print(camdata)
            noffset = camdata.split(';')
            self.offset = noffset
            print(noffset)
            #print()
            #offset = data 
        except:
            print("=======cam went wrong======")

    #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    def main(self):
        while True:
            x = threading.Thread(target=self.receiveOffset)
            x.start() 
            try:
                print()
                sdata = self.s.recv(1024)
                ndata = sdata.decode('utf-8')
                list = ndata.split(',')
                lat, lon, speed, head, loc_lat, loc_lon = [float(i) for i in list]
                self.signal = lat, lon, speed, head, loc_lat, loc_lon
                print('signal ========== ')
                print(self.signal)
                self.angles = self.move_coordinates(self.signal, self.offset)
            except:
                print("=======radar went wrong======")
            #angles[0] -= i
            # if(i > 90):
            #     i -= 5
            # else:[]
            #     i += 5
            #stri = offset[0] +";" + offset[1] + '\n'
            stri = str(self.angles[0]) + ";" + str(self.angles[1]) + '\n'
            #stri = "90.000;0.000 " + '\n'
            print(stri)
            self.write_read(stri)
    
main = SocketClient()

main.main()


"""write_read(stri)
time.sleep(10)
stri = "180.000;0.000 " + '\n'
write_read(stri)
time.sleep(10)
stri = "270.000;0.000 " + '\n'
write_read(stri)
time.sleep(10)
stri = "0.000;0.000 " + '\n'
write_read(stri)"""

