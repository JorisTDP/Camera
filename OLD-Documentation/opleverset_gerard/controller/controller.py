#!python3.9
from modules.modes import Mode, Mode0, Mode1
from modules.movement_controller import MovementController
from modules.status import Status
from modules.message import Message
from modules.communication import Communication
from modules.video_sender import VideoSender
from modules.radar_communication import RadarCommunication

from threading import Thread, Event
import time
import sys

from dotenv import dotenv_values


class Controller():
    def __init__(self):
        config = dotenv_values('.env.server')

        # Start the communication responsible for all communication with the
        # clients
        self.comm = Communication("127.0.0.1", int(config['COMMUNICATION_PORT']), 1)

        # Start video sender
        self.sender = VideoSender("127.0.0.1", int(config['VIDEO_PORT']), int(config['CAM_DEVICE']))
        sender_thread = Thread(target=self.sender.main_loop)
        sender_thread.start()

        # Start the radar receiver
        self.radar = RadarCommunication(config['RADAR_IP'], int(config['RADAR_PORT']))

        # Start the movement controller with the correct port, location,
        # x_offset and elevation
        self.movement = MovementController(config['COM_PORT'], [float(config['CAM_LAT']), float(config['CAM_LON'])], int(config['CAM_X_OFFSET']), float(config['CAM_ELEVATION']))

        # Currently supported modes of the system.
        self.modes = [Mode0(), Mode1()]

        # Current status, the last time a status was sent to the users and the 
        # time between each status being send to all users.
        self.status = Status.default_status()
        self.last_status = time.time()
        self.status_interval = 5

        # The global handlers are handlers used for system operation, they should
        # never operate any hardware.
        self.global_handlers = {
            "mode_selection": self.mode_selection
        }

        self.running = 1

    def handle(self, message: Message, status: Status) -> Status:
        if self.global_handlers.get(message.name):
            method = self.global_handlers.get(message.name)
            
            return method(message, status)
        else:
            return status


    def main_loop(self):
        while self.running:
            # Temporary debugging line so the radar doesn't need to be connected at all times.
            # TODO: Remove this for a real production purpose, the radar should be connected at all times.
            if self.status.get('current_mode') == 0:
                # See if the radar has new coordinates and if so convert it to a message
                radar_message = self.radar.get_message()

            # If there is a message continue to handle the event
            if radar_message: 
                self.handle_event(Message('radar_input', radar_message.split(',')))

            # Get last message from the client(s)
            client_message = self.comm.pop_message()

            # If there was a message continue to handle the event
            if client_message: 
                self.handle_event(client_message)

    def handle_event(self, message: Message):
        # Attempt to handle the event with a global handler from the controller
        self.status = self.handle(message, self.status)

        # Attempt to handle the event with a mode specific handler
        self.status = self.modes[self.status.get('current_mode')].handle(message, self.status, self.movement)

        # Send new status to all connected clients
        self.send_status()

    def send_status(self):
        mes = Message('status', [self.status])
        self.comm.send_message(mes)
        self.last_status = time.time()

    def mode_selection(self, message: Message, status: Status) -> Status:
        status.set("current_mode", message.args[0])

        return status

control = Controller()
try:
    control.main_loop()
except KeyboardInterrupt:
    print("KeyboardInterrupt")
    control.running = 0
    control.sender.running = 0
except SystemExit as err:
    print("SystemExit")
    control.running = 0
    control.sender.running = 0
    raise err