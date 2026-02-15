import pygame
import time
import json
import math
import random
import socket

from slot import Slot, ID_WIDTH

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000

SPLASH_DURATION_MS = 2500

# player entry layout: one column on the left, one on the right
SLOT_MARGIN = 50
SLOT_START_Y = 100
SLOT_ROW_GAP = 8
FIELD_LABEL_MARGIN = 6
# space between the team name (RED/GREEN) and the id/player_name labels
TEAM_LABEL_TO_FIELD_MARGIN = 14


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
        SCREEN_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.screen = pygame.display.set_mode(SCREEN_SIZE, 32)
        self.slots = None
        self.slot_font = None

    def load_image(self, image_path):
        image_to_load = pygame.image.load(image_path)

    # build the list of 32 slots once (16 left, 16 right)
    def _make_slots(self):
        if self.slots is not None:
            return
        self.slots = []
        slot_w = Slot.DEFAULT_W
        slot_h = Slot.DEFAULT_H
        left_x = SLOT_MARGIN
        right_x = WINDOW_WIDTH - SLOT_MARGIN - slot_w
        for i in range(Slot.NUM_PER_SIDE):
            slot_y = SLOT_START_Y + i * (slot_h + SLOT_ROW_GAP)
            self.slots.append(Slot(i, "", "", left_x, slot_y, slot_w, slot_h))
        for i in range(Slot.NUM_PER_SIDE):
            slot_y = SLOT_START_Y + i * (slot_h + SLOT_ROW_GAP)
            self.slots.append(Slot(Slot.NUM_PER_SIDE + i, "", "", right_x, slot_y, slot_w, slot_h))

    def update(self, screen_name, selectedSlot = None, editField = None, editText = "", ip_text = UDP_IP, port_text = UDP_PORT):
        BLACK_COLOR = (0, 0, 0)
        WHITE_COLOR = (255, 255, 255)
        RED_COLOR = (150, 0, 0)
        GREEN_COLOR = (0, 255, 0)
        GREY_COLOR = (120, 120, 120)

        clock_timer = pygame.time.get_ticks()

        # show splash for the first few seconds
        if clock_timer < SPLASH_DURATION_MS:
            self.screen.fill(BLACK_COLOR)
            splash_art = pygame.image.load('../assets/gui/logo.jpg')
            new_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
            scaled_splash_art = pygame.transform.scale(splash_art, new_size)
            self.screen.blit(scaled_splash_art, (0, 0))
            pygame.display.flip()
            return

        # player entry screen: teams on opposite sides, id/player_name labels, then slots
        if screen_name == "player_entry":
            self._make_slots()
            if self.slot_font is None:
                self.slot_font = pygame.font.SysFont(None, 22)
            self.screen.fill(BLACK_COLOR)
            left_x = SLOT_MARGIN
            right_x = WINDOW_WIDTH - SLOT_MARGIN - Slot.DEFAULT_W


            red_label = self.slot_font.render("RED TEAM", True, (200, 80, 80))
            
            green_label = self.slot_font.render("GREEN TEAM", True, (80, 200, 80))
            
            ip_display = editText if editField == 'ip' else ip_text
            port_display = editText if editField == 'port' else port_text
            # rendering IP address box
            ip_box_rect = pygame.Rect(50, 30, 200, 30)
            pygame.draw.rect(self.screen, (80, 80, 200), ip_box_rect, 2)
            
            ip_label = self.slot_font.render(f"IP: {ip_display}", True, WHITE_COLOR)
            self.screen.blit(ip_label, (60, 35))

            # rendering UDP Port box
            port_box_rect = pygame.Rect(300, 30, 100, 30)
            pygame.draw.rect(self.screen, (80, 80, 200), port_box_rect, 2)
            port_label = self.slot_font.render(f"Port: {port_display}", True, WHITE_COLOR)
            self.screen.blit(port_label, (310,35))


            team_label_y = SLOT_START_Y - 26
            self.screen.blit(red_label, (left_x, team_label_y))
            self.screen.blit(green_label, (right_x, team_label_y))
            # id and player_name row with a bit of margin below the team names
            field_label_y = team_label_y + TEAM_LABEL_TO_FIELD_MARGIN
            field_font = pygame.font.SysFont(None, 18)
            id_label = field_font.render("id", True, (160, 170, 180))
            name_label = field_font.render("player_name", True, (160, 170, 180))
            slot_w = Slot.DEFAULT_W
            id_x_left = left_x + FIELD_LABEL_MARGIN
            name_x_left = left_x + slot_w - name_label.get_width() - FIELD_LABEL_MARGIN
            self.screen.blit(id_label, (id_x_left, field_label_y))
            self.screen.blit(name_label, (name_x_left, field_label_y))
            id_x_right = right_x + FIELD_LABEL_MARGIN
            name_x_right = right_x + slot_w - name_label.get_width() - FIELD_LABEL_MARGIN
            self.screen.blit(id_label, (id_x_right, field_label_y))
            self.screen.blit(name_label, (name_x_right, field_label_y))

            for one_slot in self.slots:
                is_selected = one_slot.slot_index == selectedSlot

                one_slot.draw(self.screen, self.slot_font, selected = is_selected,
                                edit_field=editField if is_selected else None,
                                edit_text=editText if is_selected else "")

            pygame.display.flip()
            return

        # default main screen (grey box, red box, fishes text)
        self.screen.fill([0, 100, 150])
        font = pygame.font.SysFont(None, 72)
        grey_box = pygame.Rect(185, 10, 500, 800)
        pygame.draw.rect(self.screen, GREY_COLOR, grey_box)
        red_box = pygame.Rect(500, 600, 300, 300)
        pygame.draw.rect(self.screen, RED_COLOR, red_box)
        fish_string = "press q to exit"
        fishes_string = "F I S H E S"
        text_surface = font.render(fish_string, True, WHITE_COLOR)
        self.screen.blit(text_surface, (200, 410))
        text_surface = font.render(fish_string, True, BLACK_COLOR)
        self.screen.blit(text_surface, (198, 408))
        text_surface = font.render(fishes_string, True, WHITE_COLOR)
        self.screen.blit(text_surface, (500, 500))
        text_surface = font.render(fishes_string, True, BLACK_COLOR)
        self.screen.blit(text_surface, (498, 502))
        pygame.display.flip()
            
class Controller():
    def __init__(self, view):
        self.view = view
        self.keep_going = True
        self.current_screen = "splash"
        self.devices = set() # list of devices to brodcast to with (ip, port)
        self.devices.add((UDP_IP, UDP_PORT))
        pygame.key.set_repeat()

        # vars to track selected slot
        self.selectedSlot = None
        self.editField = None # either ID or name
        self.editText = ""

        # vars for editing ip/port
        self.editing_ip = False
        self.editing_port = False
        self.ip_text = UDP_IP
        self.port_text = str(UDP_PORT)

    def update(self):
        # after splash time is up, switch to player entry
        if self.current_screen == "splash" and pygame.time.get_ticks() > SPLASH_DURATION_MS:
            self.current_screen = "player_entry"
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.keep_going = False
                elif self.current_screen == "player_entry":
                    self.handleKeyInput(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.current_screen == "player_entry":
                    self.handleMouseClick(event.pos)
        
        try: #we're trying to read what's happening over udp
            bytesAddressPair = sock.recvfrom(bufferSize)
            message = bytesAddressPair[0]
            address = bytesAddressPair[1]

            self.lastAddress = address # added to track last sender

            clientMsg = "Message from Client{}".format(message)
            clientIP = "Client IP Address:{}".format(address)
            self.devices.add(address) #adds devices recieved from if they are new

            print(clientMsg)
            print(clientIP)
        except BlockingIOError: #handles the program waiting for udp

            pass

    # ---------------------------------
    # Mouse and Keyboard Event Handlers
    # ---------------------------------
    
    def handleMouseClick(self, pos):
        if self.view.slots is None:
            return

        x, y = pos

        # Check for IP box click first
        if 50 <= x <= 250 and 30 <= y <= 60:
            self.editField = 'ip'
            self.editing_ip = True
            self.editing_port = False
            self.editText = self.ip_text
            self.selectedSlot = None
            return

        # Check for Port box click
        if 300 <= x <= 400 and 30 <= y <= 60:
            self.editField = 'port'
            self.editing_port = True
            self.editing_ip = False
            self.editText = self.port_text
            self.selectedSlot = None
            return

        # Now check for slot clicks
        slot_clicked = False
        for slot in self.view.slots:
            slot_rect = slot.get_rect()
            if slot_rect.collidepoint(x, y):
                self.selectedSlot = slot.slot_index
                id_rect = slot.get_id_rect()
                if id_rect.collidepoint(x, y):
                    self.editField = 'id'
                else:
                    self.editField = 'name'
                self.editText = ""
                slot_clicked = True
                break

        # Deselect if click was not on any slot or IP/Port box
        if not slot_clicked:
            self.selectedSlot = None
            self.editField = None
            self.editText = ""
            

    def handleKeyInput(self, event):

        if self.editField == 'ip':
            if event.key == pygame.K_RETURN:
                global UDP_IP, UDP_PORT, sock
                self.ip_text = self.editText
                UDP_IP = self.ip_text
                sock.close()
                sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                sock.bind((UDP_IP, UDP_PORT))
                sock.setblocking(False)
                self.editing_ip = False
                self.editField = None
                self.editText = ""
            elif event.key == pygame.K_BACKSPACE:
                self.editText = self.editText[:-1]
            elif event.unicode and event.unicode.isprintable():
                self.editText += event.unicode
            return
        
        if self.editField == 'port':
            if event.key == pygame.K_RETURN:
                #global UDP_IP, UDP_PORT, sock
                self.port_text = self.editText
                UDP_PORT = int(self.port_text)
                sock.close()
                sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                sock.bind((UDP_IP, UDP_PORT))
                sock.setblocking(False)
                self.editing_port = False
                self.editField = None
                self.editText = ""
            elif event.key == pygame.K_BACKSPACE:
                self.editText = self.editText[:-1]
            elif event.unicode and event.unicode.isdigit():
                self.editText += event.unicode
            return

        # if no slot / editfield been selected:
        if self.selectedSlot is None or self.editField is None:
            if event.key == pygame.K_UP and self.selectedSlot is not None:
                self.selectedSlot = max(0, self.selectedSlot - 1)
            elif event.key == pygame.K_DOWN and self.selectedSlot is not None:
                self.selectedSlot = min(31, self.selectedSlot + 1)
            return
        
        # handling text input
        if event.key == pygame.K_BACKSPACE:
            self.editText = self.editText[:-1]
            self.saveSlotText()
        elif event.key == pygame.K_RETURN:
            # save current text to slot
            self.saveSlotText()
            self.editField = None
            self.editText = ""
        elif event.key == pygame.K_TAB:
            # switch between ID and name field
            self.saveSlotText()
            self.editField = 'name' if self.editField == 'id' else 'id'
            self.editText = ""
        elif event.unicode and event.unicode.isprintable():
            # adding character to editText (w limited length) 
            max_len = 6 if self.editField == 'id' else 10
            if len(self.editText) < max_len:
                self.editText += event.unicode
                self.saveSlotText()

        
        
    def saveSlotText(self):
        if self.selectedSlot is not None and self.selectedSlot < len(self.view.slots):
            slot = self.view.slots[self.selectedSlot]
            if self.editField == 'id':
                slot.id = self.editText
                if self.lastAddress:
                    slot.device = self.lastAddress
                    self.devices.add(self.lastAddress)
                self.broadcast(f"Equipment Code:{slot.id}")

            elif self.editField == 'name':
                slot.player_name = self.editText
                self.broadcast(f"Player Name:{slot.player_name}")


    # UDP Send/Broadcast Methods
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
    # passing edit info to view so it can render selected player slots
    v.update(c.current_screen, c.selectedSlot, c.editField, c.editText, c.ip_text, c.port_text)
    pygame.time.wait(40)
    #sleep(0.04)
    #c.sendData("Hello through UDP")
    c.broadcast("Hello Broadcast UDP")
print("\n  BOTTOM TEXT2   ")