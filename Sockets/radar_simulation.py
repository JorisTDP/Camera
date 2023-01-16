#!python3.9
# Math library used in geographic calculations
import math

import socket
import selectors
import asyncio

import serial

import time


RADAR_IP = "127.0.0.1"
RADAR_PORT = 8001

running = True


def great_circle_destination(lat, lon, d, bearing):
    R = 6371000
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    bearing = math.radians(bearing)

    lat2 = math.asin( math.sin(lat1)*math.cos(d/R) + math.cos(lat1)*math.sin(d/R)*math.cos(bearing) )
    lon2 = lon1 + math.atan2(math.sin(bearing)*math.sin(d/R)*math.cos(lat1), math.cos(d/R)-math.sin(lat1)*math.sin(lat2))

    return (math.degrees(lat2), math.degrees(lon2))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as radar:
    radar.bind((RADAR_IP, RADAR_PORT))
    radar.listen()
    print(radar)
    conn, addr = radar.accept()
    with conn:                    
        print(conn)                
        print(f"Connected by {addr}")
        if(input("One way mode?") == "y"):
            while True:
                    lat = 51.89683639
                    lon = 4.345754496
                    dist = 8
                    bearing = 1
                    loc_lat = 51.896819
                    loc_lon = 4.338410
                    #send = str(lat) + ',' + str(lon) + ',' + str(dist) + ',' + str(bearing)
                    #conn.sendall(send.encode('ascii'))
                    input("Start simulation?")
                    for i in range(64):
                        send = str(lat) + ',' + str(lon) + ',' + str(dist) + ',' + str(bearing) + ',' + str(loc_lat) + ',' + str(loc_lon)

                        try:
                            conn.sendall(send.encode('ascii'))
                        except:
                            break
                        time.sleep(1)

                        next_cords = great_circle_destination(lat, lon, dist, bearing)
                        lat = next_cords[0]
                        lon = next_cords[1]

                        print(send)

        while True:
            lat = 51.903890
            lon = 4.409957
            dist = 8
            bearing = 55
            loc_lat = 51.896819
            loc_lon = 4.338292

            for i in range(64):
                send = str(lat) + ',' + str(lon) + ',' + str(dist) + ',' + str(bearing) + ',' + str(loc_lat) + ',' + str(loc_lon)
                print(send)
                try:
                    conn.sendall(send.encode('ascii'))
                except:
                    break
                time.sleep(1)


