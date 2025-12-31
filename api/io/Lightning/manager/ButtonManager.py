import pygame
import os

from api.io.Lightning.utils.ConfigFile import *
from api.io.Lightning.manager.Spritesheet import Spritesheet

class ButtonManager:
    def __init__(self):
        # Load buttonstrip using Spritesheet
        buttonstrip_path = os.path.join(UI_PATH, 'buttonstrip.jpg')
        spritesheet = Spritesheet(buttonstrip_path)

        # Calculate button dimensions
        button_width = 135
        button_height = 42

        # Extract each button from the spritesheet
        self.buttons = {
            'undo_move_hover': spritesheet.get_image(0, 0 * button_height, button_width, button_height),
            'undo_move_clicked': spritesheet.get_image(0, 1 * button_height, button_width, button_height),
            'reset_maze_hover': spritesheet.get_image(0, 2 * button_height, button_width, button_height),
            'reset_maze_clicked':  spritesheet.get_image(0, 3 * button_height, button_width, button_height),
            'options_hover': spritesheet.get_image(0, 4 * button_height, button_width, button_height),
            'options_clicked': spritesheet.get_image(0, 5 * button_height, button_width, button_height),
            'world_map_disabled': spritesheet.get_image(0, 8 * button_height, button_width, button_height),
            'quit_to_main_hover': spritesheet.get_image(0, 9 * button_height, button_width, button_height),
            'quit_to_main_clicked': spritesheet.get_image(0, 10 * button_height, button_width, button_height),
        }

        # Define button rectangles for collision detection
        self.button_rects = {
            'undo': pygame.Rect(8, 130, button_width, button_height),
            'reset': pygame.Rect(8, 172, button_width, button_height),
            'option': pygame.Rect(8, 225, button_width, button_height),
            'quit': pygame.Rect(8, 430, button_width, button_height),
        }

        # Track which button is currently being clicked
        self.clicked_button = None

        print(f"ButtonManager initialized successfully!")

    def get_button(self, name):
        return self.buttons. get(name)

    def set_clicked(self, button_name):
        """Set which button is being clicked"""
        self.clicked_button = button_name

    def clear_clicked(self):
        """Clear the clicked button state"""
        self.clicked_button = None

    def draw_buttons(self, screen, hovered=None, clicked=None):
        """Draw all buttons with hover and click states"""
        # Only draw buttons when hovered or clicked

        # Undo button
        if clicked == 'undo':
            screen.blit(self.buttons['undo_move_clicked'], (8, 130))
        elif hovered == 'undo':
            screen.blit(self.buttons['undo_move_hover'], (8, 130))

        # Reset button
        if clicked == 'reset':
            screen.blit(self.buttons['reset_maze_clicked'], (8, 172))
        elif hovered == 'reset':
            screen.blit(self. buttons['reset_maze_hover'], (8, 172))

        # Options button
        if clicked == 'option':
            screen.blit(self.buttons['options_clicked'], (8, 225))
        elif hovered == 'option':
            screen.blit(self.buttons['options_hover'], (8, 225))

        # World map (always visible - disabled)
        screen.blit(self.buttons['world_map_disabled'], (8, 267))

        # Quit button
        if clicked == 'quit':
            screen.blit(self.buttons['quit_to_main_clicked'], (8, 430))
        elif hovered == 'quit':
            screen.blit(self.buttons['quit_to_main_hover'], (8, 430))