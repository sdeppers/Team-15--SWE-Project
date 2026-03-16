import pygame
import time
import json
import math
import random
import socket

from slot import Slot, ID_WIDTH

WINDOW_WIDTH = 750
WINDOW_HEIGHT = 750

SPLASH_DURATION_MS = 2500

# player entry layout: one column on the left, one on the right
SLOT_MARGIN = 50
SLOT_START_Y = 100
SLOT_ROW_GAP = 8
FIELD_LABEL_MARGIN = 6
# space between the team name (RED/GREEN) and the id/player_name labels
TEAM_LABEL_TO_FIELD_MARGIN = 14

class View():

    def __init__(self):
        SCREEN_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.screen = pygame.display.set_mode(SCREEN_SIZE, 32)
        self.slots = None
        self.slot_font = None
        self.clock_start = False
        self.countdown_index = 30
        self.start_time = 0

    def load_image(self, image_path):
        image_to_load = pygame.image.load(image_path)

    # build the list of 32 slots once (16 left, 16 right)
    # Slot indices [0-15] are on the left, [16-31] on the right
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
    # REnders one frame of the UI based on the current screen and any relevant info about selected slot or text being edited
    def update(self, screen_name, selectedSlot = None, editField = None, editText = "", ip_text = "", port_text = ""):
        BLACK_COLOR = (0, 0, 0)
        WHITE_COLOR = (255, 255, 255)
        RED_COLOR = (255, 0, 0)
        GREEN_COLOR = (0, 255, 0)
        GREY_COLOR = (120, 120, 120)
        BLUE_COLOR=(150, 150, 255)

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
            
            # When editFIeld matches a box ('ip', 'port', or 'equip'), show editText instea of stored text
            ip_display = editText if editField == 'ip' else ip_text
            port_display = editText if editField == 'port' else port_text
            equipment_display = editText if editField == 'equip' else ""
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

            # rendering EQUIPMENT ID box
            equip_box_rect = pygame.Rect(300, 100, 200, 30)
            pygame.draw.rect(self.screen, (80, 80, 200), equip_box_rect, 2)
            # Equipment ID text is RED while it's taking user input
            if editField == 'equip':
                equip_label = self.slot_font.render(f"Equipment ID: {equipment_display}", True, RED_COLOR)
            else:
                equip_label = self.slot_font.render(f"Equipment ID: {equipment_display}", True, WHITE_COLOR)
            self.screen.blit(equip_label, (310,105))


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
        elif screen_name == "action_display":
            # Store time of entering action display
            if not self.clock_start:
                self.start_time = clock_timer
                self.clock_start = True
            # Draw boxes
            self.screen.fill([0, 0, 0])
            font = pygame.font.SysFont(None, 42)
            border = pygame.Rect(10, 10, 730, 730)
            pygame.draw.rect(self.screen, BLUE_COLOR, border)
            top_half = pygame.Rect(20, 20, 710, 710)
            pygame.draw.rect(self.screen, BLACK_COLOR, top_half)
            bottom_half = pygame.Rect(20, 325, 710, 405)
            pygame.draw.rect(self.screen, GREY_COLOR, bottom_half)
            # Draw labels
            scores_string = "Current Scores"
            action_string = "Current Game Action"
            text_surface = font.render(action_string, True, BLUE_COLOR)
            self.screen.blit(text_surface, (400, 348))
            text_surface = font.render(action_string, True, BLACK_COLOR)
            self.screen.blit(text_surface, (398, 350))
            text_surface = font.render(scores_string, True, WHITE_COLOR)
            self.screen.blit(text_surface, (260, 25))
            text_surface = font.render(scores_string, True, BLUE_COLOR)
            self.screen.blit(text_surface, (258, 27))
            # Team labels
            text_surface = font.render("RED TEAM", True, RED_COLOR)
            self.screen.blit(text_surface, (30, 30))
            text_surface = font.render("GREEN TEAM", True, GREEN_COLOR)
            self.screen.blit(text_surface, (530, 30))
            # Y position of first codename in each list
            y_pos = 80
            font = pygame.font.SysFont(None, 30)
            # Print each codename and score for every
            # Player on red team.
            for red in self.slots:
                if red.slot_index < Slot.NUM_PER_SIDE:
                    if red.player_name != "":
                        text_surface = font.render(red.player_name, True, RED_COLOR)
                        self.screen.blit(text_surface, (30, y_pos))
                        text_surface = font.render(str(red.score), True, RED_COLOR)
                        self.screen.blit(text_surface, (150, y_pos))
                        y_pos += 30
            # Reset y-pos to print green team.
            y_pos = 80
            # Print green team
            for green in self.slots:
                if green.slot_index >= Slot.NUM_PER_SIDE:
                    if green.player_name != "":
                        text_surface = font.render(green.player_name, True, GREEN_COLOR)
                        self.screen.blit(text_surface, (530, y_pos))
                        text_surface = font.render(str(green.score), True, GREEN_COLOR)
                        self.screen.blit(text_surface, (650, y_pos))
                        y_pos += 30
            # Decrement countdown_index once every second
            if self.start_time < (clock_timer - 1000):
                if self.countdown_index > 0:
                    self.countdown_index -= 1
                    self.start_time = clock_timer
            # Print countdown image
            countdown = "../assets/gui/countdown_images/"
            countdown += str(self.countdown_index) + ".tif"
            splash_art = pygame.image.load(countdown)
            new_size = (200, 200)
            scaled_splash_art = pygame.transform.scale(splash_art, new_size)
            self.screen.blit(scaled_splash_art, (500, 500))

            pygame.display.flip()