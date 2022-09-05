#!python3.9
from modules import communication, message, video_sender, video_receiver, status, radar_communication, movement_controller, modes

import time
import cv2
from threading import Thread, Event

from dotenv import dotenv_values

print(dotenv_values('.env.server'))

# #sender = video_sender.VideoSender("127.0.0.1", 8003, 0)
# comm = communication.Communication("127.0.0.1", 8002, 1)

# #sender_thread = Thread(target=sender.main_loop)

# #sender_thread.start()

# movement = movement_controller.MovementController("COM4", [51.904547, 4.410963], 0, 4)

# mode = modes.Mode0()

# status = status.Status.default_status()
# status.set('current_mode', 0)

# print("Done")

# last_time = time.time()

# while True:
#     try:
#         mes = comm.pop_message()

#         if mes:
#             print(mes)
#             status = mode.handle(mes, status, movement)
#             print(status)
#             mes = message.Message('status', [status])
#             comm.send_message(mes)

#         if((time.time() - last_time) > 5):
#             mes = message.Message('status', [status])
#             comm.send_message(mes)
#             last_time = time.time()
        
#     except KeyboardInterrupt:
#         print("Interrupt")
#         #sender.running = 0
#         break
#     except cv2.error:
#         continue
#     except Exception as err:
#         print(err)

# sender_thread.join()

# -------------------------------------------------------------------------------------------------------------------------------

# com1 = communication.Communication("127.0.0.1", 8002, 1)
# com2 = communication.Communication("127.0.0.1", 8002, 0)
# com3 = communication.Communication("127.0.0.1", 8002, 0)

# for i in range(30):
#     com1.pop_message()

# for i in range(30):
#     mes = message.Message(f"message {i}", [status.Status.default_status(), "lol"])
#     print(f'> {str(mes.name)}')
#     com1.send_message(mes)

#     time.sleep(0.01)

#     mes = com2.pop_message()
#     if mes:print(f'< {str(mes.name)}')

#     mes = com3.pop_message()
#     if mes:print(f'< {str(mes.name)}')

# # com3 reconnects
# del com3
# com3 = communication.Communication("127.0.0.1", 8002, 0)

# print(' -- COM3 RECONNECT -- ')

# for i in range(30):
#     mes = message.Message(f"message {i}", [status.Status.default_status(), "lol"])
#     print(f'> {str(mes.name)}')
#     com1.send_message(mes)

#     time.sleep(0.01)

#     mes = com2.pop_message()
#     if mes:print(f'< {str(mes.name)}')

#     mes = com3.pop_message()
#     if mes:print(f'< {str(mes.name)}')

# print(' -- CLIENT -> SERVER -- ')

# #reset
# del com1, com2, com3
# com1 = communication.Communication("127.0.0.1", 8002, 1)
# com2 = communication.Communication("127.0.0.1", 8002, 0)
# com3 = communication.Communication("127.0.0.1", 8002, 0)

# for i in range(30):
#     mes = message.Message(f"message {i}", [status.Status.default_status(), "lol"])
#     print(f'> {str(mes.name)}')
#     com2.send_message(mes)
#     com3.send_message(mes)

#     time.sleep(0.01)

#     mes = com1.pop_message()
#     if mes:print(f'< {str(mes.name)}')

#     mes = com1.pop_message()
#     if mes:print(f'< {str(mes.name)}')

# # com3 reconnects
# del com3
# com3 = communication.Communication("127.0.0.1", 8002, 0)

# print(' -- COM3 RECONNECT -- ')

# for i in range(30):
#     mes = message.Message(f"message {i}", [status.Status.default_status(), "lol"])
#     print(f'> {str(mes.name)}')
#     com2.send_message(mes)
#     com3.send_message(mes)

#     time.sleep(0.01)

#     mes = com1.pop_message()
#     if mes:print(f'< {str(mes.name)}')

#     mes = com1.pop_message()
#     if mes:print(f'< {str(mes.name)}')

# ------------------------------------------------------------------------------------------------------------------------------------------

# arduino = movement_controller.MovementController("COM7")

# while True:
#     try:
#         mes = input("pos?: ")

#         args = mes.split(';')
#         args = [float(arg) for arg in args]

#         arduino.move(args)
#     except KeyboardInterrupt:
#         break

# -------------------------------------------------------------------------------------------------------------------------------------------

config = dotenv_values('.env.server')

movement = movement_controller.MovementController(config['COM_PORT'], [float(config['CAM_LAT']), float(config['CAM_LON'])], int(config['CAM_X_OFFSET']), float(config['CAM_ELEVATION']))

test_amount = 10
failure_indices = [None] * test_amount

for i in range(test_amount):
    counter = 0
    while(True):
        before = time.time()

        movement.move([60,60])
        counter += 1

        dif = time.time() - before
        print(dif)
        if(dif < 1):  print(f'{counter}: SUCCESS')
        else:
            print(f'{counter}: FAILURE')
            break

        time.sleep(0.005)

    failure_indices[i] = counter
    movement.reset_connection()

print(failure_indices)

    



