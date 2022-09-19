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

    if(input("One way mode?") == "y"):
        while True:
            conn, addr = radar.accept()
            with conn:
                input("Start simulation prep?")
                lat = 50.896819 #51.8968268
                lon = 4.338292 #4.35375342
                dist = 8
                bearing = 1
                #send = str(lat) + ',' + str(lon) + ',' + str(dist) + ',' + str(bearing)
                #conn.sendall(send.encode('ascii'))
                input("Start simulation?")
                for i in range(32):
                    send = str(lat) + ',' + str(lon) + ',' + str(dist) + ',' + str(bearing)

                    try:
                        conn.sendall(send.encode('ascii'))
                    except:
                        break
                    time.sleep(1)

                    next_cords = great_circle_destination(lat, lon, dist, bearing)
                    #lat = next_cords[0]
                    #lon = next_cords[1]

                    print(send)

    radar.setblocking(0)
    sel = selectors.DefaultSelector()
    sel.register(radar, selectors.EVENT_READ, data=None)

    connected_clients = []

    lat = 51.903890
    lon = 4.409957
    dist = 8
    bearing = 55

    counter = 0

    print("Loop mode started")
    while True:
        # Always accepting new connections
        events = sel.select(timeout=0.01)
        for key, mask in events:
            if key.data is None:
                print("NEW CONNECTION")
                conn, addr = radar.accept()  # Should be ready to read
                conn.setblocking(0)
                connected_clients += [conn]

        send = str(lat) + ',' + str(lon) + ',' + str(dist) + ',' + str(bearing)
        
        for client in connected_clients:
                try:
                    print("Sending:", send)
                    client.sendall(send.encode('ascii'))
                except:
                    connected_clients.remove(client)
        
        # Set the next position for the camera to look at
        counter += 1
        next_cords = great_circle_destination(lat, lon, dist, bearing)
        lat = next_cords[0]
        lon = next_cords[1]

        # When counter reaches a certain value reset the counter and reverse the bearing.
        if(counter > 32):
            counter = 0
            if(bearing < 180): bearing += 180
            else: bearing -= 180
        
        time.sleep(1)

