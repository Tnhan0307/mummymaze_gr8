import pygame, os

from api.io.Lightning.manager.TextDesigner import PyramidFont
from api.io.Lightning.utils.ConfigFile import UI_PATH

class WorldMapPanel:
    def __init__(self, x=8, y=320):
        # 1. Load Assets
        self.bg_map = pygame.image.load(os.path.join(UI_PATH, 'map.png')).convert_alpha()
        self.label_pyramid = pygame.image.load(os.path.join(UI_PATH, 'pyramidtext.gif')).convert_alpha()
        self.icon_head = pygame.image.load(os.path.join(UI_PATH, 'maphead.png')).convert_alpha()
        self.icon_x = pygame.image.load(os.path.join(UI_PATH, 'mapx.png')).convert_alpha()
        self.number_font = PyramidFont()

        # Set Rect based on loaded map image
        self.rect = self.bg_map.get_rect()
        self.rect.topleft = (x, y)

        # 2. Define Pyramid Node Positions

        # --- ADJUSTMENT SETTINGS ---
        # 1. Spacing Settings (Significantly tightened to stop drifting right)
        col_w = 20  # Reduced from 23 -> 20 (This pulls the nodes closer together)
        row_h = 15  # Kept vertical spacing the same
        bottom_y = 93

        # 2. Global Horizontal Shift
        # Since we shrank the spacing, we need to shift the center LEFT to keep Node 1
        # in the same place you liked.
        manual_x_offset = -2

        center_x = (self.rect.width // 2) + manual_x_offset
        self.nodes = []

        # --- Row 1 (Bottom): Levels 1-5 ---
        y = bottom_y
        self.nodes.extend([
            (center_x - col_w * 2, y),  # Lvl 1
            (center_x - col_w, y),  # Lvl 2
            (center_x, y),  # Lvl 3
            (center_x + col_w, y),  # Lvl 4
            (center_x + col_w * 2, y)  # Lvl 5
        ])

        # --- Row 2: Levels 6-9 ---
        y -= row_h
        self.nodes.extend([
            (center_x - col_w * 1.5, y),  # Lvl 6
            (center_x - col_w * 0.5, y),  # Lvl 7
            (center_x + col_w * 0.5, y),  # Lvl 8
            (center_x + col_w * 1.5, y)  # Lvl 9
        ])

        # --- Row 3: Levels 10-12 ---
        y -= row_h
        self.nodes.extend([
            (center_x - col_w, y),  # Lvl 10
            (center_x, y),  # Lvl 11
            (center_x + col_w, y)  # Lvl 12
        ])

        # --- Row 4: Levels 13-14 ---
        y -= row_h
        self.nodes.extend([
            (center_x - col_w * 0.5, y),  # Lvl 13
            (center_x + col_w * 0.5, y)  # Lvl 14
        ])

        # --- Row 5 (Top): Level 15 ---
        y -= row_h
        self.nodes.append((center_x, y))  # Lvl 15

    def draw(self, screen, current_level_idx):
        """
        current_level_idx: 1-based index (1 to 15)
        """
        # 1. Draw Background Map
        screen.blit(self.bg_map, self.rect.topleft)

        # 2. Draw "Pyramid" Label
        screen.blit(self.label_pyramid, (self.rect.x + 10, self.rect.y + 10))

        # 3. Draw "1" (Pyramid Number)
        pyramid_num_surf = self.number_font.render("1")
        screen.blit(pyramid_num_surf, (self.rect.x + 28, self.rect.y + 25))

        # 4. Draw Nodes
        for i, (node_x, node_y) in enumerate(self.nodes):
            level_num = i + 1

            # Calculate absolute screen position
            draw_pos_x = self.rect.x + node_x
            draw_pos_y = self.rect.y + node_y

            if level_num < current_level_idx:
                # Completed Level -> Draw X
                dest = (draw_pos_x - self.icon_x.get_width() // 2,
                        draw_pos_y - self.icon_x.get_height() // 2)
                screen.blit(self.icon_x, dest)

            elif level_num == current_level_idx:
                # Current Level -> Draw Head
                # Head is drawn slightly higher (-2) for visual overlap
                dest = (draw_pos_x - self.icon_head.get_width() // 2,
                        draw_pos_y - self.icon_head.get_height() // 2 - 2)
                screen.blit(self.icon_head, dest)