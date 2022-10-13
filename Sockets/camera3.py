#!python3.9
import pygame.camera
from VideoCapture import Device

pygame.init()
pygame.camera.init()

cam = Device()

window_surface = pygame.display.set_mode((640, 480))

is_running = True
while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

    if cam is not None:
        image = cam.getImage(timestamp=0).resize((320, 240)).save('demo.jpg', quality=80)
        window_surface.blit(image, (0, 0))

    pygame.display.update()