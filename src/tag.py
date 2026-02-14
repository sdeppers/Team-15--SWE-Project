import pygame
import time
import json
import math
import random
import socket
import psycopg2
from psycopg2 import sql
from enum import Enum
import uuid

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000

# Application States
class AppState(Enum):
    SPLASH_SCREEN = 1
    NETWORK_SELECT = 2
    PLAYER_ENTRY = 3
    GAME_RUNNING = 4
    EXIT = 5

class DatabaseManager:
    """Manages database connections and player operations"""
    
    def __init__(self):
        self.connection_params = {
            'dbname': 'photon',
            'user': 'student',
        }
        self.conn = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.cursor = self.conn.cursor()
            print("Connected to PostgreSQL database")
            return True
        except Exception as error:
            print(f"Error connecting to database: {error}")
            return False
    
    def add_player(self, codename):
        """Add a player to the database"""
        try:
            if not self.conn:
                print("Database connection not available")
                return None, None
                
            # Generate equipment code
            equipment_code = str(uuid.uuid4())[:8].upper()
            
            self.cursor.execute('''
                INSERT INTO players (codename, equipment_code)
                VALUES (%s, %s)
                RETURNING id;
            ''', (codename, equipment_code))
            
            player_id = self.cursor.fetchone()[0]
            self.conn.commit()
            
            print(f"Player '{codename}' added with equipment code: {equipment_code}")
            return player_id, equipment_code
        except Exception as error:
            print(f"Error adding player: {error}")
            if self.conn:
                self.conn.rollback()
            return None, None
    
    def get_all_players(self):
        """Retrieve all players from database"""
        try:
            self.cursor.execute("SELECT id, codename, equipment_code FROM players;")
            return self.cursor.fetchall()
        except Exception as error:
            print(f"Error retrieving players: {error}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


class UDPBroadcaster:
    """Manages UDP socket broadcasting and game communication"""
    
    def __init__(self, broadcast_address, port=7501):
        self.broadcast_address = broadcast_address
        self.port = port
        self.send_socket = None
        self.receive_socket = None
        self.setup_sockets()
    
    def setup_sockets(self):
        """Setup UDP sockets for sending and receiving"""
        try:
            # Socket for broadcasting equipment codes
            self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            # Socket for receiving traffic generator events (bind to port 7500)
            self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.receive_socket.bind(("0.0.0.0", 7500))
            self.receive_socket.setblocking(False)  # Non-blocking
            
            print(f"UDP sockets initialized - Send: {self.broadcast_address}:{self.port}, Receive: 0.0.0.0:7500")
        except Exception as error:
            print(f"Error setting up UDP sockets: {error}")
    
    def send_startup_signal(self):
        """Send startup signal (202) to traffic generator"""
        try:
            self.send_socket.sendto(b'202', (self.broadcast_address, 7500))
            print("Sent startup signal (202) to traffic generator")
            return True
        except Exception as error:
            print(f"Error sending startup signal: {error}")
            return False
    
    def broadcast_equipment_code(self, player_id, codename, equipment_code):
        """Broadcast equipment code to network (simple format for traffic gen)"""
        try:
            # Send simple string format that traffic generator expects
            message = f"{equipment_code}"
            self.send_socket.sendto(message.encode(), (self.broadcast_address, self.port))
            print(f"Broadcasted equipment code: {equipment_code}")
            return True
        except Exception as error:
            print(f"Error broadcasting: {error}")
            return False
    
    def receive_hit_event(self):
        """Receive hit events from traffic generator (non-blocking)"""
        try:
            data, addr = self.receive_socket.recvfrom(1024)
            message = data.decode('utf-8')
            print(f"Received hit event: {message}")
            return message
        except BlockingIOError:
            return None
        except Exception as error:
            print(f"Error receiving: {error}")
            return None
    
    def send_response(self, response):
        """Send response to traffic generator"""
        try:
            self.send_socket.sendto(response.encode(), (self.broadcast_address, 7500))
            print(f"Sent response: {response}")
            return True
        except Exception as error:
            print(f"Error sending response: {error}")
            return False
    
    def close(self):
        """Close UDP sockets"""
        if self.send_socket:
            self.send_socket.close()
        if self.receive_socket:
            self.receive_socket.close()


class View:
    """Handles all visual rendering"""
    
    def __init__(self):
        SCREEN_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.screen = pygame.display.set_mode(SCREEN_SIZE, 32)
        pygame.display.set_caption("Photon Tag")
        self.start_time = time.time()
    
    def load_image(self, image_path):
        """Load image from file"""
        image_to_load = pygame.image.load(image_path)
        return image_to_load
    
    def draw_splash_screen(self):
        """Draw splash screen"""
        try:
            splash_art = pygame.image.load('assets/gui/logo.jpg')
            scaled_splash_art = pygame.transform.scale(splash_art, (WINDOW_WIDTH, WINDOW_HEIGHT))
            self.screen.blit(scaled_splash_art, (0, 0))
        except:
            # Fallback if image not found
            self.screen.fill([0, 100, 150])
            font = pygame.font.SysFont(None, 72)
            text = font.render("PHOTON TAG", True, (255, 255, 255))
            self.screen.blit(text, (WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 - 50))
        
        pygame.display.flip()
    
    def draw_network_select_screen(self, networks):
        """Draw network selection screen"""
        self.screen.fill([20, 30, 40])
        font_large = pygame.font.SysFont(None, 64)
        font_small = pygame.font.SysFont(None, 32)
        
        title = font_large.render("Select Network", True, (255, 255, 255))
        self.screen.blit(title, (WINDOW_WIDTH // 2 - 150, 50))
        
        y_pos = 200
        for idx, network in enumerate(networks):
            color = (100, 255, 100) if idx == 0 else (200, 200, 200)
            text = font_small.render(f"{idx + 1}: {network}", True, color)
            self.screen.blit(text, (100, y_pos))
            y_pos += 60
        
        instruction = font_small.render("Press 1 or 2 to select", True, (150, 150, 150))
        self.screen.blit(instruction, (150, WINDOW_HEIGHT - 100))
        
        pygame.display.flip()
    
    def draw_player_entry_screen(self, player_count, player_name="", message=""):
        """Draw player entry screen"""
        self.screen.fill([20, 50, 80])
        font_large = pygame.font.SysFont(None, 56)
        font_medium = pygame.font.SysFont(None, 40)
        font_small = pygame.font.SysFont(None, 32)
        
        title = font_large.render(f"Player {player_count + 1} Entry", True, (255, 255, 255))
        self.screen.blit(title, (WINDOW_WIDTH // 2 - 180, 50))
        
        label = font_medium.render("Enter Codename:", True, (200, 200, 200))
        self.screen.blit(label, (100, 250))
        
        # Draw input box
        input_box = pygame.Rect(100, 350, 800, 60)
        pygame.draw.rect(self.screen, (100, 100, 100), input_box, 2)
        
        input_text = font_medium.render(player_name + "_", True, (255, 255, 255))
        self.screen.blit(input_text, (120, 360))
        
        # Draw message
        if message:
            msg_color = (100, 255, 100) if "added" in message.lower() else (255, 100, 100)
            msg_text = font_small.render(message, True, msg_color)
            self.screen.blit(msg_text, (100, 500))
        
        instruction = font_small.render("Press ENTER to confirm, Q to skip to game", True, (150, 150, 150))
        self.screen.blit(instruction, (50, WINDOW_HEIGHT - 100))
        
        pygame.display.flip()
    
    def draw_game_screen(self, players):
        """Draw main game screen"""
        self.screen.fill([0, 100, 150])
        font_large = pygame.font.SysFont(None, 56)
        font_medium = pygame.font.SysFont(None, 32)
        
        title = font_large.render("PHOTON TAG", True, (255, 255, 255))
        self.screen.blit(title, (WINDOW_WIDTH // 2 - 200, 50))
        
        players_text = font_medium.render(f"Players: {len(players)}", True, (100, 255, 100))
        self.screen.blit(players_text, (50, 200))
        
        y_pos = 300
        for player in players:
            player_text = font_medium.render(f"{player[1]}: {player[2]}", True, (200, 200, 255))
            self.screen.blit(player_text, (100, y_pos))
            y_pos += 50
        
        instruction = font_medium.render("Press Q to exit", True, (150, 150, 150))
        self.screen.blit(instruction, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 100))
        
        pygame.display.flip()

class Controller:
    """Handles user input and application flow"""
    
    def __init__(self, view, db_manager, udp_broadcaster):
        self.view = view
        self.db_manager = db_manager
        self.udp_broadcaster = udp_broadcaster
        self.keep_going = True
        self.app_state = AppState.SPLASH_SCREEN
        self.splash_start_time = time.time()
        self.player_codenames = []
        self.player_count = 0
        self.current_input = ""
        self.message = ""
        self.message_time = 0
        self.selected_network = None
        
        pygame.key.set_repeat()
    
    def select_network(self):
        """Let user select network for UDP"""
        networks = {
            1: ("255.255.255.255", "Local Broadcast"),
            2: ("192.168.1.255", "Subnet Broadcast")
        }
        
        while self.keep_going:
            self.view.draw_network_select_screen([networks[1][1], networks[2][1]])
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.keep_going = False
                    self.app_state = AppState.EXIT
                    return
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_1:
                        self.selected_network = networks[1][0]
                        print(f"Selected network: {networks[1][1]}")
                        return
                    elif event.key == pygame.K_2:
                        self.selected_network = networks[2][0]
                        print(f"Selected network: {networks[2][1]}")
                        return
                    elif event.key == pygame.K_q:
                        self.keep_going = False
                        self.app_state = AppState.EXIT
                        return
            
            pygame.time.wait(40)
    
    def player_entry_screen(self):
        """Handle player entry screen"""
        self.player_count = 0
        
        while self.player_count < 2 and self.keep_going:
            # Clear message if timeout
            if time.time() - self.message_time > 3:
                self.message = ""
            
            self.view.draw_player_entry_screen(self.player_count, self.current_input, self.message)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.keep_going = False
                    self.app_state = AppState.EXIT
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        if self.player_count == 0:
                            self.keep_going = False
                            self.app_state = AppState.EXIT
                            return
                        else:
                            # Move to game if we have at least 1 player
                            self.app_state = AppState.GAME_RUNNING
                            return
                    elif event.key == pygame.K_RETURN:
                        if self.current_input.strip():
                            player_id, equipment_code = self.db_manager.add_player(self.current_input)
                            if player_id:
                                self.player_codenames.append((player_id, self.current_input, equipment_code))
                                # Broadcast equipment code
                                self.udp_broadcaster.broadcast_equipment_code(player_id, self.current_input, equipment_code)
                                self.message = f"✓ {self.current_input} added!"
                                self.message_time = time.time()
                                self.player_count += 1
                                self.current_input = ""
                            else:
                                self.message = "Error adding player. Try again."
                                self.message_time = time.time()
                    elif event.key == pygame.K_BACKSPACE:
                        self.current_input = self.current_input[:-1]
                    elif event.unicode.isalnum() or event.unicode == ' ':
                        if len(self.current_input) < 20:
                            self.current_input += event.unicode
            
            pygame.time.wait(40)
    
    def update(self):
        """Main update loop"""
        if self.app_state == AppState.SPLASH_SCREEN:
            self.view.draw_splash_screen()
            
            # Show splash for 2.5 seconds
            if time.time() - self.splash_start_time > 2.5:
                self.app_state = AppState.NETWORK_SELECT
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.keep_going = False
                    self.app_state = AppState.EXIT
        
        elif self.app_state == AppState.NETWORK_SELECT:
            self.select_network()
            if self.keep_going:
                self.app_state = AppState.PLAYER_ENTRY
        
        elif self.app_state == AppState.PLAYER_ENTRY:
            self.player_entry_screen()
        
        elif self.app_state == AppState.GAME_RUNNING:
            players = self.db_manager.get_all_players()
            self.view.draw_game_screen(players)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.keep_going = False
                    self.app_state = AppState.EXIT
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_q:
                        self.keep_going = False
                        self.app_state = AppState.EXIT
        
        elif self.app_state == AppState.EXIT:
            self.keep_going = False

def main():
    """Main application entry point"""
    print("Starting Photon Tag Application\n")
    pygame.init()
    pygame.font.init()
    
    # Initialize managers
    db_manager = DatabaseManager()
    
    # Default broadcast address (will be updated by user selection)
    
    udp_broadcaster = UDPBroadcaster("255.255.255.255", port=7501)
    udp_broadcaster.send_startup_signal()
    # Initialize view and controller
    view = View()
    controller = Controller(view, db_manager, udp_broadcaster)
    
    clock = pygame.time.Clock()
    
    while controller.keep_going:
        controller.update()
        hit_event = udp_broadcaster.receive_hit_event()
        if hit_event:
            print(f'Processing hit: {hit_event}')
            udp_broadcaster.send_response('200')
        clock.tick(25)  # 40ms per frame
    
    # Cleanup
    udp_broadcaster.close()
    db_manager.close()
    pygame.quit()
    
    print("\n  Application Closed   ")

if __name__ == "__main__":
    main()

# import pygame
# import time
# import json
# import math
# import random

# WINDOW_WIDTH = 1000;
# WINDOW_HEIGHT = 1000;

# class View():

#     def __init__(self):
#         SCREEN_SIZE = (WINDOW_WIDTH,WINDOW_HEIGHT)
#         self.screen = pygame.display.set_mode(SCREEN_SIZE, 32)

#     def load_image(self, image_path):
#         image_to_load = pygame.image.load(image_path)
        

#     def update(self):

#         BLACK_COLOR = (0,0,0)
#         WHITE_COLOR = (255,255,255)
#         RED_COLOR = (150,0,0)
#         GREEN_COLOR = (0,255,0)
#         GREY_COLOR = (120,120,120)

#         # change background color
#         self.screen.fill([0, 100, 150])

#         # add text to the screen
#         # Default font is size 32
#         #font = pygame.font.SysFont(None, 32)
#         font = pygame.font.SysFont(None, 72)

#         clock_timer = 0
#         clock_timer += pygame.time.get_ticks()
#         # print(clock_timer)

#         if (clock_timer < 2500):
#             splash_art = pygame.image.load('assets/gui/logo.jpg')
#             new_size = (WINDOW_WIDTH,WINDOW_HEIGHT)
#             scaled_splash_art = pygame.transform.scale(splash_art, new_size)
#             image_rect = scaled_splash_art.get_rect(center=(WINDOW_WIDTH,WINDOW_HEIGHT))
#             self.screen.blit(scaled_splash_art,(0,0))
#         else:
#             grey_box = pygame.Rect(185,10,500,800)
#             pygame.draw.rect(self.screen,GREY_COLOR,grey_box)
#             red_box = pygame.Rect(500,600,300,300)
#             pygame.draw.rect(self.screen,RED_COLOR,red_box)

#             fish_string = "press q to exit"
#             fishes_string = "F I S H E S"
#             text_surface = font.render(fish_string, True, WHITE_COLOR)
#             TEXT_LOCATION = (200, 410)
#             self.screen.blit(text_surface, TEXT_LOCATION)
#             text_surface = font.render(fish_string, True, BLACK_COLOR)
#             TEXT_LOCATION = (198, 408)
#             self.screen.blit(text_surface, TEXT_LOCATION)

#             text_surface = font.render(fishes_string, True, WHITE_COLOR)
#             TEXT_LOCATION = (500, 500)
#             self.screen.blit(text_surface, TEXT_LOCATION)
#             text_surface = font.render(fishes_string, True, BLACK_COLOR)
#             TEXT_LOCATION = (498, 502)
#             self.screen.blit(text_surface, TEXT_LOCATION)

#         pygame.display.flip()
            
# class Controller():
#     def __init__(self, view):
#         self.view = view
#         self.keep_going = True
#         pygame.key.set_repeat()
#     def update(self):
#         for event in pygame.event.get():
#             if event.type == pygame.KEYUP:
#                 if event.key == pygame.K_q:
#                     self.keep_going = False





# print("TOP TEXT\n")
# pygame.init()
# pygame.font.init()
# clock = pygame.time.Clock()

# v = View()
# c = Controller(v)
# while c.keep_going:
#     c.update()
#     v.update()
    
#     pygame.time.wait(40)
#     #sleep(0.04)
# print("\n  BOTTOM TEXT   ")