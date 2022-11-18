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

        self.clock = pygame.time.Clock()

        self.communication = Communication(CAMERA_IP, CAMERA_PORT)

        # Start pygame and create a screen
        pygame.init()
        pygame.display.set_caption("Sens2Sea ObjectDetectie UI")
        self.screen = pygame.display.set_mode([self.width, self.height])

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FPS, 60)

        self.input_rect = pygame.Rect(0, 0, 440, 34)

        self.base_font = pygame.font.Font(None, 32)
        self.user_text = ''
  
        self.color_active = pygame.Color('lightskyblue3')

        self.color_passive = pygame.Color('chartreuse4')
        self.color = self.color_passive

        self.active = False
        

        self.running = 1

    def update_screen(self, frame):
            # reset screen
            self.screen.fill([0, 0, 0])

            if(type(frame) != type(None)):
                temp_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                temp_frame = np.rot90(temp_frame)
                temp_frame = cv2.flip(temp_frame, 0)
                #temp_frame = temp_frame.swapaxes(0, 1)
                temp_frame = cv2.resize(temp_frame, (720, 1280), interpolation=cv2.INTER_AREA)

                temp_frame = pygame.surfarray.make_surface(temp_frame)

                self.screen.blit(temp_frame, (0,0))

            font = pygame.font.Font('freesansbold.ttf', 30)

            width = self.width
            height = self.height

            # Display available controls
            txt = "Controls: Arrow keys for +1,-1 offset | W,A,S,D keys for +10,-10 offset "
            text = font.render(txt, True, (255,255,255), (0,0,0))
            self.screen.blit(text, (width - font.size(txt)[0],0))

            # Display current offsets in mode 0
            pygame.display.update()
            
            return pygame.event.get()

    def handle_user_event(event, self):
        if event.type == pygame.QUIT:
            del ui
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False

        elif event.type == KEYDOWN:

            if self.active == True:
                if event.key == pygame.K_BACKSPACE:
                    self.user_text = self.user_text[:-1]
                elif event.key == pygame.K_RETURN:
                    self.communication.send_input(self.user_text)
                    self.user_text = ''
                else: 
                    self.user_text += event.unicode    
            else:
                if event.key == K_UP:
                    self.offsetz -= 1
                    #print(self.offsetx)
                if event.key == K_DOWN:
                    self.offsetz += 1
                    #print(self.offsetx)
                if event.key == K_LEFT:
                    self.offsetx += 1
                    #print(self.offsetz)
                if event.key == K_RIGHT:
                    self.offsetx -= 1
                if event.key == K_w:
                    self.offsetz -= 10
                    #print(self.offsetx)
                if event.key == K_s:
                    self.offsetz += 10
                    #print(self.offsetx)
                if event.key == K_a:
                    self.offsetx += 10
                    #print(self.offsetz)
                if event.key == K_d:
                    self.offsetx -= 10
                    #print(self.offsetz)
                    #self.communication.send_offset(offset)

            self.communication.send_offset(self.offsetx, self.offsetz)
            #print(self.user_text)
    
    def input(self): #draws input_rect
        pygame.draw.rect(self.screen, self.color, self.input_rect)
        text_surface = self.base_font.render(self.user_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (self.input_rect.x+5, self.input_rect.y+5))
        self.input_rect.w = max(100, text_surface.get_width()+10)
        pygame.display.flip()
        self.clock.tick(60)

    def main_loop(self):
        while True: #self.running:
            success, frame = self.cap.read()
            if not success:
                break
            if self.active:
                self.color = self.color_active
            else:
                self.color = self.color_passive

            UserInterface.input(self)
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