#!python3.9
from gps_calculations import calculate_desired_compass_bearing, calculate_distance_to_target, calculate_next_position

import socket
import serial
import time
import threading
import math

HOST = "127.0.0.1" 
RADARPORT = 8001 
CAMERAPORT = 8002 

arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1)

class SocketClient:

    def __init__(self): #init of sockets and variables
        self.cam = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cam.connect((HOST, CAMERAPORT))
        self.s.connect((HOST, RADARPORT))
        self.s.sendall(b"Hello, world")
        self.cam.sendall(b"Hello, world")
        self.signal = 1,1,1,1,1,1
        self.offset = 0, 0
        self.angles = [0,0]
        self.correctInput = False
        self.input = 1

    def write_read(self, x): # send angles (x) to arduino
        arduino.write(bytes(x,'utf-8'))
        time.sleep(0.05)
        for i in range(2):
            data = arduino.readline() #read if arduino has responded correctly
            print (data.decode('utf-8'))
        return data   

    def move_coordinates(self, data: list, offsets: list) -> list:

        location = float(data[4]), float(data[5])
        elevation = 1

        # calculate next coordinates
        next_position = calculate_next_position(data)

        # calculate desired x angle
        x_angle = calculate_desired_compass_bearing(location,next_position)  #(loc, next)
        if(x_angle < 0): x_angle += 360

        # calculate distance to target
        distance = calculate_distance_to_target(location, next_position)

        # calculate desired z angle
        z_angle = math.degrees(math.atan(distance/elevation))
        z_angle = 90 - z_angle ###later weghalen !!!!!!!!!!

        # apply offsets to x and z angles
        x_angle, z_angle = x_angle + int(offsets[0]), z_angle + int(offsets[1])
        angles = [x_angle, z_angle]

        return angles    

    def receiveOffset(self): # function that recieves the offset from the user interface
        try:
            print("camdata:")
            camdata = self.cam.recv(1024).decode()
            print(camdata)
            if(camdata[0] == "+"):
                print("user input accepted")
                inp = camdata[1:]
                print(inp)
                try:
                    check = float(inp)
                    self.input = inp
                    self.correctInput = True
                except:
                    print("wrong input")
                    self.correctInput = False

            else:
                noffset = camdata.split(';')
                self.offset = noffset
                print(noffset)
        except:
            print("=======cam went wrong======")
            time.sleep(1)

    def main(self): # main loop
        while True:
            x = threading.Thread(target=self.receiveOffset) 
            x.start() # start a thread so cam data and radar data can be recieved simultaneously. 
            try:
                print()
                sdata = self.s.recv(1024) #recieve radar data
                ndata = sdata.decode('utf-8')
                list = ndata.split(',')
                lat, lon, speed, head, loc_lat, loc_lon = [float(i) for i in list]
                self.signal = lat, lon, speed, head, loc_lat, loc_lon #stores radar data in signal
                self.angles = self.move_coordinates(self.signal, self.offset) #use signal and offset to calculate the desired angle.
            except:
                print("=======radar went wrong======")
                time.sleep(1)
     
            #stri = offset[0] +";" + offset[1] + '\n'
            if(self.correctInput == False):
                stri = str(self.angles[0]) + ":" + str(self.angles[1]) + ";" + "n" '\n' #put the x and z angle into a string so it can be sent over serial.
            else:
                stri = str(self.angles[0]) + ":" + str(self.angles[1]) + ";" + self.input + '\n'
            #stri = "90.000;0.000 " + '\n'
            print(stri)
            self.write_read(stri) # send over serial to arduino
    

main = SocketClient()
main.main()
