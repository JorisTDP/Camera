#!python3.9

from modules import pygame_controller, status, communication, video_receiver
from modules.message import Message

import sys

from pygame.locals import *
import pygame

from threading import Thread, Event

from dotenv import dotenv_values

class UserInterface():
    def __init__(self):
        config = dotenv_values('.env.client')

        self.camera_communication = communication.Communication(config['SERVER_IP'], int(config['COMMUNICATION_PORT']), 0)

        self.receiver = video_receiver.VideoReceiver(config['SERVER_IP'], int(config['VIDEO_PORT']))
        receiver_thread = Thread(target=self.receiver.main_loop)
        receiver_thread.start()

        self.pygame_controller = pygame_controller.PyGameController(1280, 720)

        self.status = status.Status.default_status()

        # Variables used in control operations
        self.offset_increment = 1
        self.move_size = 1

        # Define a field to give an outside script the ability to stop the
        # endless main loop.
        self.running = 1

    def main_loop(self):
        while self.running:
            # Check for new messages and handle them
            message = self.camera_communication.pop_message()
            
            # Update status if the message was a status update
            if(message and message.name == 'status'):
                print("Received status")
                self.status = message.args[0]

            # Update screen and process events from pygame
            pygame_events = self.pygame_controller.update_screen(self.receiver.frame, self.status, self)

            for event in pygame_events:
                self.handle_user_event(event)

    def __del__(self):
        del self.camera_communication
        self.running = 0
        self.receiver.running = 0
    
    def handle_user_event(self, event):
        if event.type == pygame.QUIT:
            raise UIShutdown()
        elif event.type == KEYDOWN:
            current_mode = self.status.get('current_mode')

            if event.key == K_ESCAPE or event.key == K_q:
                raise UIShutdown()
            elif event.key == K_TAB:
                # If left shift is pressed go back one mode
                if pygame.key.get_pressed()[K_LSHIFT]:
                    current_mode -= 1
                    if(current_mode < 0): current_mode = 0
                    self.camera_communication.send_message(Message('mode_selection',[current_mode]))
                    return

                # Otherwise continue through the available modes
                current_mode += 1
                if(current_mode > len(self.status.get('modes'))-1): current_mode = len(self.status.get('modes'))-1

                self.camera_communication.send_message(Message('mode_selection',[current_mode]))
            elif current_mode == 0:
                offsets = [0, 0]

                if event.key == K_UP:
                    offsets[1] = self.offset_increment
                elif event.key == K_DOWN:
                    offsets[1] = -self.offset_increment
                elif event.key == K_LEFT:
                    offsets[0] = -self.offset_increment
                elif event.key == K_RIGHT:
                    offsets[0] = self.offset_increment
                elif event.key == K_PAGEUP:
                    self.offset_increment *= 2
                elif event.key == K_PAGEDOWN:
                    self.offset_increment *= 0.5

                print(offsets)
                
                # Only send update message if the offsets actually changed
                if(offsets != [0, 0]):
                    self.camera_communication.send_message(Message('offset_update', offsets))
            elif current_mode == 1:
                print("sending move???")
                if event.key == K_UP:
                    self.camera_communication.send_message(Message('move', [0, self.move_size]))
                elif event.key == K_DOWN:
                    self.camera_communication.send_message(Message('move', [0, -self.move_size]))
                elif event.key == K_LEFT:
                    self.camera_communication.send_message(Message('move', [-self.move_size, 0]))
                elif event.key == K_RIGHT:
                    self.camera_communication.send_message(Message('move', [self.move_size, 0]))
                elif event.key == K_PAGEUP:
                    self.move_size *= 2
                elif event.key == K_PAGEDOWN:
                    self.move_size *= 0.5

class UIShutdown(Exception):
    def __init__(self):
        super().__init__("The UI will to be shut down according to user input!")


ui = UserInterface()
try:
    ui.main_loop()
except UIShutdown:
    del ui
except KeyboardInterrupt:
    del ui
