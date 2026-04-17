import pygame

# Slot: horizontal bar (wide, short). Used by View for the player entry screen.
DEFAULT_W = 180
DEFAULT_H = 35
ID_WIDTH = 36
NAME_WIDTH = 50
DIVIDER_COLOR = (70, 74, 82)


class Slot:
    NUM_PER_SIDE = 15
    TOTAL_SLOTS = 30
    DEFAULT_W = 180
    DEFAULT_H = 28

    def __init__(self, slot_index, id_="", player_name="", x=0, y=0, w=None, h=None):
        self.slot_index = slot_index
        self.id = id_ if id_ is not None else ""
        self.player_name = player_name or ""
        self.x = x
        self.y = y
        self.w = w if w is not None else Slot.DEFAULT_W
        self.h = h if h is not None else Slot.DEFAULT_H
        self.device = None
        self.equipment = ""
        self.score = 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    # these are for hit-testing so we know which zone was clicked
    def get_id_rect(self):
        return pygame.Rect(self.x, self.y, ID_WIDTH, self.h)

    def get_name_rect(self):
        return pygame.Rect(self.x + ID_WIDTH, self.y, self.w - ID_WIDTH, self.h)

    def draw(self, surface, font, bg_color=(40, 44, 50), border_color=(80, 84, 92), text_color=(240, 240, 240),
             selected = False, edit_field = None, edit_text = ""):
        
        rect = self.get_rect()
        id_zone_rect = self.get_id_rect()
        name_zone_rect = self.get_name_rect()

        pygame.draw.rect(surface, bg_color, rect)

        highlight_color = (100, 150, 200)
        if selected:
            if edit_field == 'id':
                pygame.draw.rect(surface, highlight_color, id_zone_rect)
            elif edit_field == 'name':
                pygame.draw.rect(surface, highlight_color, name_zone_rect)

        # pygame.draw.rect(surface, bg_color, rect)
        pygame.draw.rect(surface, border_color, rect, 2 if selected else 1)

        # line between id and player_name areas
        div_x = self.x + ID_WIDTH
        pygame.draw.line(surface, DIVIDER_COLOR, (div_x, self.y + 2), (div_x, self.y + self.h - 2), 1)

        # draw id text in the left zone (clip if too long)
        if selected and edit_field == 'id':
            id_str = (edit_text or "")[:6]
        else:
            id_str = (self.id or "")[:6]
        # id_str = (self.id or "")[:6]
        if id_str:
            id_surf = font.render(id_str, True, text_color)
            id_rect = id_surf.get_rect(midleft=(self.x + 2, self.y + self.h // 2))
            if id_rect.right > div_x - 2:
                id_rect.right = div_x - 2
            surface.blit(id_surf, id_rect)

        # draw player_name in the right zone (clip if too long)
        if selected and edit_field == 'name':
            name_str = (edit_text or "")[:10]
        else:
            name_str = (self.player_name or "")[:10]
        # name_str = (self.player_name or "")[:10]
        if name_str:
            name_surf = font.render(name_str, True, text_color)
            name_rect = name_surf.get_rect(midleft=(self.x + ID_WIDTH + 2, self.y + self.h // 2))
            if name_rect.right > self.x + self.w - 2:
                name_rect.right = self.x + self.w - 2
            surface.blit(name_surf, name_rect)
