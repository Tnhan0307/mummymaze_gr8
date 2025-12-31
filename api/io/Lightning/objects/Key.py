import os
import pygame

from api.io.Lightning.utils.ConfigFile import OBJECTS_PATH, maze_coord_x, maze_coord_y

class Key:
    def __init__(self, x, y, cell_size, maze_size):
        self.grid_x = x
        self.grid_y = y
        self.cell_size = cell_size
        self.maze_size = maze_size

        self.frames = []
        self.frame_index = 0
        self.animation_speed = 0.25
        self.animation_counter = 0
        self.collected = False

        self._load_frames()

    def _load_frames(self):
        """Load key animation frames from sprite strip"""
        try:
            key_strip = pygame.image.load(os.path.join(OBJECTS_PATH, f'key.png')).convert_alpha()

            # Get sheet dimensions
            sheet_width = key_strip.get_width()
            sheet_height = key_strip.get_height()

            # Calculate frame dimensions (assuming square frames in horizontal strip)
            frame_height = sheet_height
            frame_width = frame_height  # Square frames
            total_frames = sheet_width // frame_width

            # Extract frames
            for i in range(total_frames):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(key_strip, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                self.frames.append(frame)

            print(f"✅ Loaded {len(self.frames)} key animation frames")

        except Exception as e:
            print(f"❌ Có lỗi xảy ra khi khởi chạy Key: {e}")
            # Create dummy frame
            dummy = pygame.Surface((self.cell_size // 2, self.cell_size // 2), pygame.SRCALPHA)
            dummy.fill((255, 215, 0))  # Gold color
            self.frames = [dummy]

    def update(self):
        """Update animation"""
        self.animation_counter += self.animation_speed

        if self.animation_counter >= 1.0:
            self.animation_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def draw(self, surface):
        """Draw key at its position"""
        if not self.frames:
            return

        frame = self.frames[self.frame_index]

        # Calculate screen position (centered in cell)
        draw_x = maze_coord_x + self.grid_x * self.cell_size + (self.cell_size - frame.get_width()) // 2
        draw_y = maze_coord_y + self.grid_y * self.cell_size + (self.cell_size - frame.get_height()) // 2 - 6

        surface.blit(frame, (draw_x, draw_y))

    def activate(self):
        """Activate key (for toggling gate) - key stays on map"""
        pass  # Key doesn't get collected, just triggers gate

    def check_collision(self, entity_x, entity_y):
        """Check if entity is at key position"""
        return entity_x == self.grid_x and entity_y == self.grid_y