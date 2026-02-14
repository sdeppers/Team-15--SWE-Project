import pygame
import time
import json
import math
import random
import socket

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000

UDP_IP = "127.0.0.1"  
UDP_PORT = 5005     
bufferSize = 1024

#create socket
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

#bind to ip and port
sock.bind((UDP_IP, UDP_PORT))

#pretty sure this means the code won't stop if it doesn't hear 
#Anything from the socket which is what we want
sock.setblocking(False)

class View():

    def __init__(self):
        SCREEN_SIZE = (WINDOW_WIDTH,WINDOW_HEIGHT)
        self.screen = pygame.display.set_mode(SCREEN_SIZE, 32)

    def load_image(self, image_path):
        image_to_load = pygame.image.load(image_path)
        

    def update(self):

        BLACK_COLOR = (0,0,0)
        WHITE_COLOR = (255,255,255)
        RED_COLOR = (150,0,0)
        GREEN_COLOR = (0,255,0)
        GREY_COLOR = (120,120,120)

        # change background color
        self.screen.fill([0, 100, 150])

        # add text to the screen
        # Default font is size 32
        #font = pygame.font.SysFont(None, 32)
        font = pygame.font.SysFont(None, 72)

        clock_timer = 0
        clock_timer += pygame.time.get_ticks()
        # print(clock_timer)
        # Filepath to splash image starts with '..' because it's located in parent directory
        if (clock_timer < 2500):
            splash_art = pygame.image.load('../assets/gui/logo.jpg')
            new_size = (WINDOW_WIDTH,WINDOW_HEIGHT)
            scaled_splash_art = pygame.transform.scale(splash_art, new_size)
            image_rect = scaled_splash_art.get_rect(center=(WINDOW_WIDTH,WINDOW_HEIGHT))
            self.screen.blit(scaled_splash_art,(0,0))
        else:
            grey_box = pygame.Rect(185,10,500,800)
            pygame.draw.rect(self.screen,GREY_COLOR,grey_box)
            red_box = pygame.Rect(500,600,300,300)
            pygame.draw.rect(self.screen,RED_COLOR,red_box)

            fish_string = "press q to exit"
            fishes_string = "F I S H E S"
            text_surface = font.render(fish_string, True, WHITE_COLOR)
            TEXT_LOCATION = (200, 410)
            self.screen.blit(text_surface, TEXT_LOCATION)
            text_surface = font.render(fish_string, True, BLACK_COLOR)
            TEXT_LOCATION = (198, 408)
            self.screen.blit(text_surface, TEXT_LOCATION)

            text_surface = font.render(fishes_string, True, WHITE_COLOR)
            TEXT_LOCATION = (500, 500)
            self.screen.blit(text_surface, TEXT_LOCATION)
            text_surface = font.render(fishes_string, True, BLACK_COLOR)
            TEXT_LOCATION = (498, 502)
            self.screen.blit(text_surface, TEXT_LOCATION)

        pygame.display.flip()
            
class Controller():
    def __init__(self, view):
        self.view = view
        self.keep_going = True
        self.devices = set() # list of devices to brodcast to with (ip, port)
        self.devices.add((UDP_IP, UDP_PORT))
        pygame.key.set_repeat()
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    self.keep_going = False
        
        try: #we're trying to read what's happening over udp
            bytesAddressPair = sock.recvfrom(bufferSize)
            message = bytesAddressPair[0]
            address = bytesAddressPair[1]
            clientMsg = "Message from Client{}".format(message)
            clientIP = "Client IP Address:{}".format(address)
            self.devices.add(address) #adds devices recieved from if they are new

            print(clientMsg)
            print(clientIP)
        except BlockingIOError: #handles the program waiting for udp

            pass
    def sendData(self, message): #send to a device over udp
        sock.sendto(message.encode(), (UDP_IP, UDP_PORT)) 
        print("Sent", message)
    def broadcast(self, message): #send to all devices in list
        for device in self.devices:
            sock.sendto(message.encode(), device)
        print(f"Broadcast '{message}' to {len(self.devices)} devices")




print("TOP TEXT\n")
pygame.init()
pygame.font.init()
clock = pygame.time.Clock()

v = View()
c = Controller(v)
while c.keep_going:
    c.update()
    v.update()
    
    pygame.time.wait(40)
    #sleep(0.04)
    #c.sendData("Hello through UDP")
    c.broadcast("Hello Broadcast UDP")
print("\n  BOTTOM TEXT2   ")