#!python3.9
import pygame
import cv2

from .status import Status

class PyGameController():
    """
    Controller class for the PyGame window

    ...

    Methods
    -------
    update_screen(frame, status, ui)
        Updates the screen using the latest frame and the current status together
        with certain attributes from the UI object
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height+30

        # Start pygame and create a screen
        pygame.init()
        pygame.display.set_caption("Sens2Sea ObjectDetectie UI")
        self.screen = pygame.display.set_mode([self.width, self.height])
    
    def update_screen(self, frame, status: Status, ui):
        # reset screen
        self.screen.fill([0, 0, 0])

        if(type(frame) != type(None)):
            temp_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            temp_frame = cv2.flip(temp_frame, 0)
            temp_frame = cv2.flip(temp_frame, 1)
            temp_frame = temp_frame.swapaxes(1, 0)
            temp_frame = pygame.surfarray.make_surface(temp_frame)

            self.screen.blit(temp_frame, (0,0))

        font = pygame.font.Font('freesansbold.ttf', 30)

        width = self.width
        height = self.height

        text = font.render(f"X: {status.get('x_angle')} | Z: {status.get('z_angle')} | D: {status.get('distance')}", True, (255,255,255), (0,0,0))
        text_rect = text.get_rect(center=(width/2 , height-15))
        self.screen.blit(text, text_rect)

        # Display available controls
        txt = "Controls: r = reset camera | tab = switch-control-modes (+ left shift = mode-back)"
        text = font.render(txt, True, (255,255,255), (0,0,0))
        self.screen.blit(text, (width - font.size(txt)[0],0))

        # Display current mode
        txt = f"Mode: {status.get('current_mode')} - {status.get('current_mode')}"
        text = font.render(txt, True, (255,255,255), (0,0,0))
        self.screen.blit(text, (width - font.size(txt)[0], 30))

        # Display current offsets in mode 0
        if status.get('current_mode') == 0:
            txt = f"Offsets: {status.get('x_offset')} - {status.get('z_offset')}"
            text = font.render(txt, True, (255,255,255), (0,0,0))
            self.screen.blit(text, (width - font.size(txt)[0], 60))

            txt = f'Offset increment: {ui.offset_increment}'
            text = font.render(txt, True, (255,255,255), (0,0,0))
            self.screen.blit(text, (width - font.size(txt)[0], 90))

        # Display current move increment in mode 1
        if status.get('current_mode') == 1:
            txt = f'Move size: {ui.move_size}'
            text = font.render(txt, True, (255,255,255), (0,0,0))
            self.screen.blit(text, (width - font.size(txt)[0], 60))

        pygame.display.update()
        
        return pygame.event.get()
