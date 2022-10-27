#!python3.9
import cv2
import pygame
import numpy as np
import time
import socket
from input import Communication


import sys

from pygame.locals import *

CAMERA_IP = "127.0.0.1"
CAMERA_PORT = 8002

class UserInterface():
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.offsetx = 1
        self.offsetz = 1

        self.communication = Communication(CAMERA_IP, CAMERA_PORT)

        # Start pygame and create a screen
        pygame.init()
        pygame.display.set_caption("Sens2Sea ObjectDetectie UI")
        self.screen = pygame.display.set_mode([self.width, self.height])

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        

        self.running = 1

    def update_screen(self, frame):
            # reset screen
            self.screen.fill([0, 0, 0])

            if(type(frame) != type(None)):
                temp_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                temp_frame = np.rot90(temp_frame)
                temp_frame = cv2.flip(temp_frame, 0)
                #temp_frame = temp_frame.swapaxes(0, 1)
                temp_frame = pygame.surfarray.make_surface(temp_frame)

                self.screen.blit(temp_frame, (200,200))

            font = pygame.font.Font('freesansbold.ttf', 30)

            width = self.width
            height = self.height

            # Display available controls
            txt = "Controls: r = reset camera | tab = switch-control-modes (+ left shift = mode-back)"
            text = font.render(txt, True, (255,255,255), (0,0,0))
            self.screen.blit(text, (width - font.size(txt)[0],0))

            # Display current offsets in mode 0
            pygame.display.update()
            
            return pygame.event.get()

    def handle_user_event(event, self):
        if event.type == pygame.QUIT:
            del ui
        elif event.type == KEYDOWN:
        
            if event.key == K_UP:
                self.offsetx += 1
                #print(self.offsetx)
            if event.key == K_DOWN:
                self.offsetx -= 1
                #print(self.offsetx)
            if event.key == K_LEFT:
                self.offsetz -= 1
                #print(self.offsetz)
            if event.key == K_RIGHT:
                self.offsetz += 1
            if event.key == K_w:
                self.offsetx += 10
                #print(self.offsetx)
            if event.key == K_s:
                self.offsetx -= 10
                #print(self.offsetx)
            if event.key == K_a:
                self.offsetz -= 10
                #print(self.offsetz)
            if event.key == K_d:
                self.offsetz += 10
                #print(self.offsetz)
                #self.communication.send_offset(offset)
            self.communication.send_offset(self.offsetx, self.offsetz)

    def main_loop(self):
        while True: #self.running:
            success, frame = self.cap.read()
            if not success:
                break
            pygame_events = UserInterface.update_screen(self, frame)

            for event in pygame_events:
                UserInterface.handle_user_event(event, self)

            #self.communication.send_offset(self.offsetx)


class UIShutdown(Exception):
    def __init__(self):
        super().__init__("The UI will to be shut down according to user input!")

ui = UserInterface(1280, 720)
#try:
ui.main_loop()
#except UIShutdown: 
#    print("error")