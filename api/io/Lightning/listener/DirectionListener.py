import pygame
import os

from api.io.Lightning.manager.Spritesheet import Spritesheet
from api.io.Lightning.utils.ConfigFile import UI_PATH

class Direction:
    def __init__(self, maze_size):
        self.spritesheet = Spritesheet(os.path.join(UI_PATH, f"arrows{maze_size}.gif"))
        self.circle = pygame.image.load(os.path.join(UI_PATH, f"circle{maze_size}.gif")).convert_alpha()
        self.animations = []
        self.move_images = {}

    def load_move_images(self, maze_size):
        w = self.spritesheet.sheet.get_width()
        h = self.spritesheet.sheet.get_height() // 4

        self.move_images = {
            'DOWN': self.spritesheet.get_image(0, 0, w, h),
            'RIGHT': self.spritesheet.get_image(0, h, w, h),
            'LEFT': self.spritesheet.get_image(0, h * 2, w, h),
            'UP': self.spritesheet.get_image(0, h * 3, w, h),
            'STAY': self.circle
        }