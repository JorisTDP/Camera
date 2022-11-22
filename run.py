import os

response = os.system('start cmd /k py C:/Users/joris/Desktop/Stage/Camera/Sockets/radar_simulation.py') #start radar_sim
response = os.system('start cmd /k py C:/Users/joris/Desktop/Stage/Camera/Sockets/camera.py') # start camera.py
response = os.system('py C:/Users/joris/Desktop/Stage/Camera/Sockets/socket_client.py') # start socket client
