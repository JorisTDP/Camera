#!python3.9
from .message import Message
from .status import Status
from .movement_controller import MovementController
from .gps_calculations import calculate_desired_compass_bearing, calculate_distance_to_target, calculate_next_position

import time

# Mode abstract
class Mode():
    """
    Mode class used as abstract for derived Modes

    ...

    Methods
    -------
    handle(message, status, hardware)
        Selects and runs corresponding method based on the event message received
    """

    handlers = {}

    def handle(self, message: Message, status: Status, hardware: MovementController) -> Status:
        if self.handlers.get(message.name):
            method = self.handlers.get(message.name)
            
            return method(message, status, hardware)
        else:
            return status

class Mode0(Mode):
    """
    Radar operation mode, responds to radar_input and offset_update events.

    ...

    Methods
    -------
    handle(message, status, hardware)
        Selects and runs corresponding method based on the event message received
    """

    def __init__(self):
        # Set the last received radar input to two seconds ago to automatically return 
        self.last_radar = time.time()-2

        self.handlers = {
            'offset_update': self.offset_update,
            'radar_input': self.radar_input,
        }

    def offset_update(self, message: Message, status: Status, hardware: MovementController) -> Status:
        status.set('x_offset', status.get('x_offset') + message.args[0])
        status.set('z_offset', status.get('z_offset') + message.args[1])

        return status

    def radar_input(self, message: Message, status: Status, hardware: MovementController) -> Status:
        offsets = [status.get('x_offset'), status.get('z_offset')]

        # Let the hardware move to the desired location
        angles = hardware.move_coordinates(message.args, offsets)

        # Add new angles to the status object and return it
        status.set('x_angle', angles[0])
        status.set('z_angle', angles[1])

        return status


class Mode1(Mode):
    """
    Manual operation mode, responds to move events.

    ...

    Methods
    -------
    handle(message, status, hardware)
        Selects and runs corresponding method based on the event message received
    """

    def __init__(self):
        self.handlers = {
            'move': self.move,
        }

    def move(self, message: Message, status: Status, hardware: MovementController) -> Status:
        # Get current status and add the movement from the user to them
        new_angles = [status.get('x_angle') + message.args[0], status.get('z_angle') + message.args[1]]

        hardware.move(new_angles)

        status.set('x_angle', new_angles[0])
        status.set('z_angle', new_angles[1])

        return status


    