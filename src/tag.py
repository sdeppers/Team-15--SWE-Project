import pygame
import time
import json
import math
import random

WINDOW_WIDTH = 1000;
WINDOW_HEIGHT = 1000;

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

        if (clock_timer < 2500):
            splash_art = pygame.image.load('assets/gui/logo.jpg')
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
        pygame.key.set_repeat()
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    self.keep_going = False





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
print("\n  BOTTOM TEXT2   ")