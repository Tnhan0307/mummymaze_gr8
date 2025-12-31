import pygame
import os
import random
from enum import Enum
from api.io.Lightning.entities.EntityLoader import Entity
from api.io.Lightning.manager.SoundReader import sfx_manager
from api.io.Lightning.utils.ConfigFile import ENTITIES_PATH, maze_coord_x, maze_coord_y


class PlayerState(Enum):
    IDLE = "idle"
    WALK = "walk"
    # AFK
    AFK_READMAP = "readmap"
    AFK_LIGHT = "light"
    AFK_SEARCH = "search"
    AFK_SHRUG = "shrug"
    # Deaths
    DIE_WHITE_MUMMY = 'whitefight'
    DIE_RED_MUMMY = 'redfight'
    DIE_STUNG = "stung"
    DIE_TRAP = "freakout"


class Player(Entity):
    def __init__(self, x, y, maze_size, tile_size):
        super().__init__(x, y)
        self.maze_size = maze_size
        self.tile_size = tile_size

        # --- Position Management ---
        self.target_x = x
        self.target_y = y
        self.pixel_x = x * tile_size
        self.pixel_y = y * tile_size
        self.move_speed = 2
        self.is_moving = False

        # --- Cooldown System ---
        self.next_move_time = 0
        self.move_cooldown = 50  # 1000ms = 1 second cooldown

        # --- State Management ---
        self.state = PlayerState.IDLE
        self.direction = 'down'

        self.frame_index = 0
        self.animation_speed = 0.20
        self.animation_counter = 0

        # --- AFK System ---
        self.last_input_time = pygame.time.get_ticks()
        self.afk_delay = 7000

        # --- Assets ---
        self.current_walk_variant = None
        self.animations = {}
        self._load_assets()

        print(f"🎮 Player initialized at Grid({x}, {y})")

    def _load_assets(self):
        """Loads assets using 'Key.py' logic"""

        def load_img(name):
            for ext in [".png", ".gif"]:
                path = os.path.join(ENTITIES_PATH, f"{name}{self.maze_size}{ext}")
                if os.path.exists(path):
                    try:
                        return pygame.image.load(path).convert_alpha()
                    except:
                        pass
            return None

        def load_strip_square(sheet):
            if not sheet: return []
            sheet_w, sheet_h = sheet.get_size()
            frame_h = sheet_h
            frame_w = sheet_h
            count = sheet_w // frame_w
            frames = []
            for i in range(count):
                frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (i * frame_w, 0, frame_w, frame_h))
                frames.append(frame)
            return frames

        def load_grid_explorer(sheet):
            if not sheet: return {'up': [], 'right': [], 'down': [], 'left': []}
            sheet_w, sheet_h = sheet.get_size()
            cols = 5
            rows = 4
            fw = sheet_w // cols
            fh = sheet_h // rows
            anims = {'up': [], 'right': [], 'down': [], 'left': []}
            directions = ['up', 'right', 'down', 'left']
            for row, direction in enumerate(directions):
                for col in range(cols):
                    frame = pygame.Surface((fw, fh), pygame.SRCALPHA)
                    frame.blit(sheet, (0, 0), (col * fw, row * fh, fw, fh))
                    anims[direction].append(frame)
            return anims

        # 1. Load Explorer (Grid)
        explorer_sheet = load_img("explorer")
        if explorer_sheet:
            walk_anims = load_grid_explorer(explorer_sheet)
            self.animations['walk_up'] = walk_anims['up']
            self.animations['walk_right'] = walk_anims['right']
            self.animations['walk_down'] = walk_anims['down']
            self.animations['walk_left'] = walk_anims['left']

        # 2. Load Strips (Use Square Logic)
        self.animations[PlayerState.AFK_READMAP] = load_strip_square(load_img("readmap"))
        self.animations[PlayerState.AFK_LIGHT] = load_strip_square(load_img("light"))
        self.animations[PlayerState.AFK_SEARCH] = load_strip_square(load_img("search"))
        self.animations[PlayerState.AFK_SHRUG] = load_strip_square(load_img("shrug"))

        # 3. Load Deaths
        self.animations[PlayerState.DIE_TRAP] = load_strip_square(load_img("freakout"))
        self.animations[PlayerState.DIE_STUNG] = load_strip_square(load_img("stung"))
        self.animations[PlayerState.DIE_RED_MUMMY] = load_strip_square(load_img("redfight"))
        self.animations[PlayerState.DIE_WHITE_MUMMY] = load_strip_square(load_img("whitefight"))

    def is_ready(self):
        """Check if player can move (not moving AND cooldown finished)"""
        current_time = pygame.time.get_ticks()
        # Allow if not moving, not dead, and cooldown has passed
        return (not self.is_moving
                and "DIE" not in self.state.name
                and current_time >= self.next_move_time)

    def handle_input(self):
        # Allow input only if ready, or allow interrupting AFK
        if not self.is_ready() and "AFK" not in self.state.name:
            return None

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
        elif keys[pygame.K_SPACE]:
            self._reset_afk()
            return (0, 0)

        if dx != 0 or dy != 0:
            self._reset_afk()
            return (dx, dy)

        return None

    def _reset_afk(self):
        """Reset AFK timer and state"""
        self.last_input_time = pygame.time.get_ticks()
        if "AFK" in self.state.name:
            self.state = PlayerState.IDLE
            self.frame_index = 0

    def move_player(self, dx, dy):
        # Set cooldown timer
        self.next_move_time = pygame.time.get_ticks() + self.move_cooldown

        # WAIT command
        if dx == 0 and dy == 0:
            self.state = PlayerState.IDLE
            self._reset_afk()
            return

        # START MOVING
        self.x += dx
        self.y += dy
        self.target_x = self.x * self.tile_size
        self.target_y = self.y * self.tile_size

        self.is_moving = True
        self.state = PlayerState.WALK
        self._reset_afk()

        # --- NEW: PLAY START SOUND ---
        # Returns '15', '30', or '60' so we know which one to finish with
        self.current_walk_variant = sfx_manager.play_walk_start('player')

        if dx > 0: self.direction = 'right'
        if dx < 0: self.direction = 'left'
        if dy > 0: self.direction = 'down'
        if dy < 0: self.direction = 'up'

    def update(self):
        current_time = pygame.time.get_ticks()

        # --- 1. Movement Logic ---
        if self.is_moving:
            if self.pixel_x < self.target_x:
                self.pixel_x = min(self.pixel_x + self.move_speed, self.target_x)
            elif self.pixel_x > self.target_x:
                self.pixel_x = max(self.pixel_x - self.move_speed, self.target_x)

            if self.pixel_y < self.target_y:
                self.pixel_y = min(self.pixel_y + self.move_speed, self.target_y)
            elif self.pixel_y > self.target_y:
                self.pixel_y = max(self.pixel_y - self.move_speed, self.target_y)

            # Check if movement finished
            if self.pixel_x == self.target_x and self.pixel_y == self.target_y:
                self.is_moving = False

                if self.current_walk_variant:
                    sfx_manager.play_walk_end('player', self.current_walk_variant)
                    self.current_walk_variant = None  # Reset

                self.state = PlayerState.IDLE
                self.frame_index = 0
                self.last_input_time = current_time

                # --- 2. AFK Trigger Logic ---
        # Ensure we only trigger AFK if we are TRULY idle (cooldown passed + delay passed)
        elif self.state == PlayerState.IDLE:
            # Wait until cooldown allows movement before counting AFK time
            if current_time >= self.next_move_time:
                if current_time - self.last_input_time > self.afk_delay:
                    self._trigger_random_afk()

        # --- 3. Animation Update ---
        anim_list = []
        if self.state == PlayerState.WALK:
            anim_list = self.animations.get(f'walk_{self.direction}', [])
        elif self.state == PlayerState.IDLE:
            frames = self.animations.get(f'walk_{self.direction}', [])
            if frames: anim_list = [frames[0]]
        else:
            anim_list = self.animations.get(self.state, [])

        if not anim_list: return

        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1.0:
            self.animation_counter = 0

            if self.state == PlayerState.WALK:
                self.frame_index = (self.frame_index + 1) % len(anim_list)

            elif "AFK" in self.state.name:
                if self.frame_index < len(anim_list) - 1:
                    self.frame_index += 1
                else:
                    self.state = PlayerState.IDLE
                    self.direction = 'down'
                    self.last_input_time = current_time
                    self.frame_index = 0

            elif "DIE" in self.state.name:
                if self.frame_index < len(anim_list) - 1:
                    self.frame_index += 1

    def _trigger_random_afk(self):
        options = [PlayerState.AFK_READMAP, PlayerState.AFK_LIGHT, PlayerState.AFK_SEARCH, PlayerState.AFK_SHRUG]
        self.state = random.choice(options)
        self.frame_index = 0

    def draw(self, surface):
        anim_list = []
        if self.state == PlayerState.WALK or self.state == PlayerState.IDLE:
            anim_list = self.animations.get(f'walk_{self.direction}', [])
        else:
            anim_list = self.animations.get(self.state, [])

        if anim_list:
            idx = self.frame_index if self.frame_index < len(anim_list) else 0
            image = anim_list[idx]

            draw_x = maze_coord_x + self.pixel_x
            draw_y = maze_coord_y + self.pixel_y

            offset_x = (self.tile_size - image.get_width()) // 2
            offset_y = (self.tile_size - image.get_height()) // 2

            surface.blit(image, (draw_x + offset_x, draw_y + offset_y))