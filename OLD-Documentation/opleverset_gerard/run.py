import os

#put static ip of raspberry pi
hostname = "169.254.183.31"

#makes connection with pi
print('Connecting')
#response = os.system('cd Sockets')
response = os.system('start cmd /k py C:/Users/joris/Desktop/Stage/Camera/OLD-Documentation/opleverset_gerard/controller/simulation/radar_simulation.py')
response = os.system('py C:/Users/joris/Desktop/Stage/Camera/OLD-Documentation/opleverset_gerard/controller/controller.py')
response = os.system('start cmd /k py C:/Users/joris/Desktop/Stage/Camera/OLD-Documentation/opleverset_gerard/controller/user_interface.py')
#response = os.system('C:\Users\joris\Desktop\Stage\Camera\OLD-Documentation\opleverset_gerard\controller')
#response = os.system('py C:/Users/joris/Desktop/Stage/Camera/Sockets/socket_client.py')
print('programs started')
