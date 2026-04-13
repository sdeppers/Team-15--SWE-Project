# -------------------------------------------------------------
# Controller.py
#
# This file contains the Controller class, which manages the
# main program logic for the laser tag player entry system.
#
# Responsibilities of this file:
# - Handle keyboard and mouse input
# - Manage the current screen (splash, player entry, etc.)
# - Update player slot information
# - Communicate with equipment via UDP networking
# - Store player data in the database
#
# The Controller communicates with:
# - View (UI display)
# - Slot objects (player slots)
# - python_pg (database functions)
#
# The program uses pygame for UI and socket for networking.
# -------------------------------------------------------------


import pygame   # Used for graphics, keyboard input, and mouse input
#import time     # Provides time functions (not heavily used here)
#import json     # Used for JSON data formatting (not currently used)
#import math     # Mathematical functions (not currently used)
import random   # Random number generation (used in mp3 selection)
import socket   # Used for UDP networking between devices

from slot import Slot, ID_WIDTH     # Slot represents a player entry slot in the UI
from python_pg import add_player    # Adds a player record to the PostgreSQL database
from python_pg import id_exists     # Checks if a player ID already exists in the database
#from python_pg import delete_database
from view import View               # View handles drawing the UI to the screen

# Amount of time the splash screen stays visible (milliseconds)
SPLASH_DURATION_MS = 2500

# -------------------------------------------------------------
# INPUT_ID and INPUT_NAME store player data for each slot.
#
# There are 32 player slots in the system.
# Each slot stores:
#   - player ID
#   - player codename
#
# These arrays act as temporary storage before writing
# player data to the database.
#
# Default values:
#   "inID"   -> slot does not yet contain a player ID
#   "inName" -> slot does not yet contain a player name
# -------------------------------------------------------------
INPUT_ID = ["inID"] * Slot.TOTAL_SLOTS
INPUT_NAME = ["inName"] * Slot.TOTAL_SLOTS


class Controller():
    def __init__(self, view):
        self.ADDING_NEW_PLAYER = False
        self.NEEDS_EQUIPMENT_ID = False
        self.view = view
        self.keep_going = True
        self.current_screen = "splash"  # Possible values: splash, player_entry, action_display
        #self.devices = set() # list of devices to broadcast to with (ip, port)
        #self.devices.add((UDP_IP, UDP_PORT)) # Device tracking was originally planned but not used in the final version
        pygame.key.set_repeat()

        # vars to track selected slot
        self.selectedSlot = None
        self.editField = None # either ID or name
        self.editText = ""
        self.lastAddress = None #to prevent attempting to access while no attribute
        # After the .mp3 is selected, this becomes true
        self.mp3_has_been_selected = False
        # String for the filepath to the mp3 will be stored here
        self.mp3_filepath = ""
        # Hacky way of preventing the mp3 from continually restarting
        self.mp3_playing = False

        #for broadcasting to equipment
        self.game_started = False
        self.game_ended = False

        # -------------------------------------------------------------
        # UDP Networking Configuration
        #
        #UDP is used to send and receive messages between the
        # player entry system and the laser tag equipment.
        #
        # Send_UDP_IP  -> IP address messages are sent to
        # Receive_UDP_PORT -> Port used to listen for incoming messages
        # Target_port -> Port used when sending UDP messages to equipment
        # bufferSize -> Maximum size of received message
        # -------------------------------------------------------------
        self.Send_UDP_IP = "127.0.0.1"  
        self.Receive_UDP_PORT = 7501
        self.Target_port = 7500
        self.bufferSize = 1024

        self.recv_sock =socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.recv_sock.bind(("0.0.0.0", self.Receive_UDP_PORT))
        self.recv_sock.setblocking(False)

        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # vars for editing ip/port
        self.editing_ip = False
        self.editing_port = False
        self.ip_text = self.Send_UDP_IP
        self.port_text = str(self.Target_port)
    
    #Helper function for UDP Handlers
    def find_player_by_equipment(self, equipment_id):
        for slot in self.view.slots:
            if str(slot.equipment) == str(equipment_id):
                return slot
        return None

    def is_red(self, slot):
        return slot.slot_index < 16

    def is_green(self, slot):
        return slot.slot_index >= 16

    def is_opposing_team(self, p1, p2):
        return (self.is_red(p1) and self.is_green(p2)) or \
            (self.is_green(p1) and self.is_red(p2))

    # -------------------------------------------------------------
    # update()
    #
    # This function runs once per frame.
    #
    # Responsibilities:
    # - Check if splash screen should transition
    # - Handle keyboard events
    # - Handle mouse clicks
    # - Listen for UDP messages from equipment
    # -------------------------------------------------------------
    def update(self):
        # Sets mp3_filepath to one of the 8 available tracks
        if not self.mp3_has_been_selected:
            rand_int = random.randint(1, 8)
            self.mp3_filepath = "../assets/photon_tracks/Track0" + str(rand_int) + ".mp3"
            print(self.mp3_filepath) # Testing only
            pygame.mixer.init()
            self.mp3_has_been_selected = True
        # after splash time is up, switch to player entry
        if self.current_screen == "splash" and pygame.time.get_ticks() > SPLASH_DURATION_MS:
            self.current_screen = "player_entry"
        # When action display is active, start the mp3 file and play through the end
        if self.current_screen == "action_display":
            if self.view.GAME_RUNNING and not self.game_started: #broadcast code to start game
                self.broadcast("202")
                self.game_started = True

            if self.view.game_time_left <= 0 and not self.game_ended: # end the game when game ended
                for _ in range(3):
                    self.broadcast("221")
                self.game_ended = True

            if not self.mp3_playing:
                print("Playing " + self.mp3_filepath) # For testing only
                pygame.mixer.music.load(self.mp3_filepath)
                pygame.mixer.music.play()
                self.mp3_playing = True
                # Disperse to exit instruction begins at start=380.0 in the mp3
                # *IF THE TRACK NEEDS TO BE STOPPED AND RESTARTED AT 30 SECONDS, USE THE FOLLOWING:
                # pygame.mixer.music.stop()
                # pygame.mixer.music.play(start=30.0)
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.keep_going = False
                elif self.current_screen == "player_entry":
                    self.handleKeyInput(event)
            elif event.type == pygame.MOUSEBUTTONDOWN: #?? This probably shouldn't always be checked
                if self.current_screen == "player_entry":
                    self.handleMouseClick(event.pos)
        
        
        try: #we're trying to read what's happening over udp
            bytesAddressPair = self.recv_sock.recvfrom(self.bufferSize)
            # Decodes the 'bytes' type into a python string
            message = bytesAddressPair[0].decode('utf-8')
            address = bytesAddressPair[1].decode('utf-8')

            self.lastAddress = address # added to track last sender

            clientMsg = "Message from Client{}".format(message)
            clientIP = "Client IP Address:{}".format(address)
            #self.devices.add(address) #adds devices recieved from if they are new

            if ":" in message: #Handles normal hits
                shooter_id, hit_id = message.split(":")
                shooter_id = int(shooter_id)
                hit_id = int(hit_id)

                shooter = self.find_player_by_equipment(shooter_id)
                target = self.find_player_by_equipment(hit_id)

                if target == "53": #red base
                    if self.is_green(shooter):
                        shooter.score += 100
                        shooter.has_base = True
                        # Both 'pop' methods pop the first string in their array if there is not
                        # at least one empty string. Then, it appends an additional empty string
                        # To store the 10th message in (allows for "scrolling text")
                        self.view.pop_first_green()
                        # Stores base hit message
                        first_empty = self.view.event_strings_green.index('')
                        action_string = shooter.player_name + " hit the red base!"
                        self.event_strings_green[first_empty] = action_string
                elif target == "43": #green base
                    if self.is_red(shooter):
                        shooter.score += 100
                        shooter.has_base = True
                        self.view.pop_first_red()
                        # Stores base hit message
                        first_empty = self.view.event_strings_red.index('')
                        action_string = shooter.player_name + " hit the green base!"
                        self.event_strings_red[first_empty] = action_string
                elif shooter and target:
                    if self.is_opposing_team(shooter, target):
                        shooter.score += 10
                    else:
                        shooter.score -= 10
                        target.score -= 10
                        self.broadcast(str(shooter_id)) #disable shooter like hit on friendly fire?
                    if self.is_green(shooter):
                        self.view.pop_first_green()
                        # Stores (green) player hit target
                        first_empty = self.view.event_strings_green.index('')
                        action_string = shooter.player_name + " hit "+ target.player_name
                        self.event_strings_green[first_empty] = action_string
                    if self.is_red(shooter):
                        self.view.pop_first_red()
                        # Stores (red) player hit target
                        first_empty = self.view.event_strings_red.index('')
                        action_string = shooter.player_name + " hit "+ target.player_name
                        self.event_strings_red[first_empty] = action_string
                    
                    # broadcast hit player
                    self.broadcast(str(hit_id))

            print(clientMsg)
            print(clientIP)
        except BlockingIOError: #handles the program waiting for udp

            pass

    # -------------------------------------------------------------
    # handleMouseClick()
    #
    # Determines what UI element the user clicked on:
    # - IP address input box
    # - Port input box
    # - Player slot ID field
    # - Player slot name field
    # -------------------------------------------------------------
    
    def handleMouseClick(self, pos):
        if self.view.slots is None:
            return

        # Added to ensure text entries are saved if user clicks into another box while still editing current box
        # REMOVED FEATURE. Potential to cause lots of problems with
        # id_exists function. -Spence
        # if self.selectedSlot is not None and self.editField in ['id', 'name']:
        #     self.saveSlotText()

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
            
    # -------------------------------------------------------------
    # handleKeyInput()
    #
    # Processes all keyboard input including:
    # - Editing player IDs
    # - Editing player names
    # - Entering equipment IDs
    # - Switching fields using TAB
    # - Starting the action display screen
    # -------------------------------------------------------------

    #F12 -> Clears all player slots
    #F5  -> Switches to action display screen    
    #TAB -> Switch between ID and name fields
    #ENTER -> Save entered text
    #BACKSPACE -> Delete last character
    def handleKeyInput(self, event):
        # If F12 is pressed at ANY time, all records in DB are deleted,
        # and slot.id and slot.player_name is set to ""
        # SATISFIES REQUIREMENT *f12...*
        if event.key == pygame.K_F12:
            #delete_database()
            for slot in self.view.slots:
                slot.id = ""
                slot.player_name = ""
        if event.key == pygame.K_F5:
            #for udp broadcast
            self.game_started = False
            self.game_ended = False

            self.current_screen = "action_display"
        if self.editField == 'ip':
            if event.key == pygame.K_RETURN:
                self.ip_text = self.editText
                self.Send_UDP_IP = self.ip_text
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
                self.Target_port = int(self.port_text)
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
                self.selectedSlot = min(Slot.TOTAL_SLOTS, self.selectedSlot + 1)
            return
        
        # handling text input
        if event.key == pygame.K_BACKSPACE:
            self.editText = self.editText[:-1]
            # self.saveSlotText() | <- REMOVED to fix message sent after every char update
        elif event.key == pygame.K_RETURN:
            # save current text to slot
            self.saveSlotText()
            self.editText = ""
            self.editField = None
            # SATISFIES REQUIREMENT *prompt for the equipment...
            # See editField == 'equip' block for more details
            if self.NEEDS_EQUIPMENT_ID:
                self.editField = 'equip'
                self.NEEDS_EQUIPMENT_ID = False
            # ADD_NEW... is true when there is no record for a given player ID
            # Only enters block AFTER an equipment ID is assigned to the player ID.
            # SATISFIES REQUIREMENT *allow for the entry for...
            elif self.ADDING_NEW_PLAYER:
                self.editField = 'name'
                self.ADDING_NEW_PLAYER = False
            
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
                # self.saveSlotText() | <- REMOVED to fix message sent after every char update

    # -------------------------------------------------------------
    # saveSlotText()
    #
    # Saves the text currently being edited into the selected slot.
    #
    # Depending on the field being edited, this function may:
    # - Store the player ID
    # - Store the player name
    # - Store equipment ID
    # - Check the database for existing player records
    # - Add new players to the database
    # -------------------------------------------------------------    
    def saveSlotText(self):
        if self.selectedSlot is not None and self.selectedSlot < len(self.view.slots):
            slot = self.view.slots[self.selectedSlot]
            if self.editField == 'id':
                slot.id = self.editText
                if self.lastAddress:
                    slot.device = self.lastAddress
                    #self.devices.add(self.lastAddress)
                #self.broadcast(f"Equipment Code:{slot.id}")
                INPUT_ID[slot.slot_index] = slot.id
                # If a player record for a given player ID exists,
                # populate that slots' codename from the database
                # ELSE, set ADDING_NEW_PLAYER to true
                existing_name = id_exists(slot.id)
                print("\nPlease input equipment ID, and press ENTER.")
                if existing_name != '':
                    INPUT_NAME[slot.slot_index] = existing_name
                    slot.player_name = existing_name
                else:
                    print("Then, input new player codename, and press ENTER.")
                    self.ADDING_NEW_PLAYER = True
                # Equipment id is ALWAYS selected immediately after user
                # stores a player ID.
                # Equipment ID will be selected prior to the codename slot.
                # See final 'K_RETURN' block for more details.
                self.NEEDS_EQUIPMENT_ID = True

            elif self.editField == 'name':
                slot.player_name = self.editText
                #self.broadcast(f"Player Name:{slot.player_name}")
                INPUT_NAME[slot.slot_index] = slot.player_name
            # Only stores equipment ID if editText can be cast to an integer
            # Otherwise, NEEDS_EQUIPMENT_ID is set back to True, and program
            # remains in 'equip' state.
            elif self.editField == 'equip':
                if self.editText.isdigit():
                    slot.equipment = self.editText
                    #self.broadcast(f"Equipment ID : {slot.equipment}")
                    self.broadcast(str(slot.equipment))
                else:
                    print("\nERROR. Equipment ID must be an integer.\nTry again.")
                    self.NEEDS_EQUIPMENT_ID = True
            # Add player into to database if both slots are populated.
            # Error checking for preventing duplicate entries can be found in the
            # add_player function, and the id_exist function that is called prior
            if INPUT_ID[slot.slot_index] != "inID":
                if INPUT_NAME[slot.slot_index] != "inName":
                    add_player(INPUT_ID[slot.slot_index],INPUT_NAME[slot.slot_index])



    # UDP Send/Broadcast Methods
    #def sendData(self, message): #send to a device over udp
    #    self.send_sock.sendto(message.encode(), (UDP_IP, UDP_PORT)) 
    #    print("Sent", message)
    def broadcast(self, message): #send to all devices in list
        self.send_sock.sendto(message.encode(), (self.Send_UDP_IP, self.Target_port))
        print(f"\nBroadcast '{message}' to {self.Send_UDP_IP}:{self.Target_port}")