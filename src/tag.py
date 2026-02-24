import pygame
import time
import json
import math
import random
import socket

from view import View
from controller import Controller

pygame.init()
pygame.font.init()
clock = pygame.time.Clock()

v = View()
c = Controller(v)
c.broadcast("Photon Started")

while c.keep_going:
    c.update()
    # passing edit info to view so it can render selected player slots
    v.update(c.current_screen, c.selectedSlot, c.editField, c.editText, c.ip_text, c.port_text)
    pygame.time.wait(40)
    #sleep(0.04)
    #c.sendData("Hello through UDP")
    #c.broadcast("Hello Broadcast UDP")
    #print("\n  BOTTOM TEXT2   ")