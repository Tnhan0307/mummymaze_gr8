import pygame
import os
from api.io.Lightning.utils.ConfigFile import OBJECTS_PATH

class TorchAnimation:
    def __init__(self):
        self.torch_frames = []
        self.torch_glow_frames = []
        self.frame_index = 0
        self.animation_speed = 0.15  # Adjust speed (lower = slower)
        self.animation_counter = 0
        self.loaded = False

    def load(self):
        """Load torch flame and glow animation frames"""
        try:
            # Load single torch image
            torch_image = pygame.image.load(os.path.join(OBJECTS_PATH, 'torch.png')).convert_alpha()

            # Load torch glow strip (10 frames horizontally)
            torch_glow_strip = pygame.image.load(os.path.join(OBJECTS_PATH, 'glow.png')).convert_alpha()

            # Load flame animation strip (10 frames horizontally)
            flame_strip = pygame.image.load(os.path.join(OBJECTS_PATH, 'flame.png')).convert_alpha()

            # Get dimensions
            glow_frame_width = torch_glow_strip.get_width() // 10  # 10 frames
            glow_frame_height = torch_glow_strip.get_height()

            flame_frame_width = flame_strip.get_width() // 10  # 10 frames
            flame_frame_height = flame_strip.get_height()

            print(f"Torch dimensions - Glow: {glow_frame_width}x{glow_frame_height}, "
                  f"Flame:  {flame_frame_width}x{flame_frame_height}, "
                  f"Base: {torch_image.get_width()}x{torch_image.get_height()}")

            # Extract glow frames
            self.torch_glow_frames = []
            for i in range(10):
                frame = torch_glow_strip.subsurface((i * glow_frame_width, 0, glow_frame_width, glow_frame_height))
                self.torch_glow_frames.append(frame.copy())

            # Extract flame frames and combine with torch base
            self.torch_frames = []
            for i in range(10):
                # Calculate combined dimensions
                combined_width = max(torch_image.get_width(), flame_frame_width)
                combined_height = torch_image.get_height() + flame_frame_height

                # Create a surface to hold the complete torch (base + flame)
                torch_complete = pygame.Surface((combined_width, combined_height), pygame.SRCALPHA)

                # Extract flame frame
                flame_frame = flame_strip.subsurface((i * flame_frame_width, 0, flame_frame_width, flame_frame_height))

                # Center the torch base and flame
                torch_x = (combined_width - torch_image.get_width()) // 2
                flame_x = (combined_width - flame_frame_width) // 2

                # Composite:  flame on top, torch base below (with slight overlap)
                torch_complete.blit(flame_frame, (flame_x, 0))  # Flame at top
                torch_complete.blit(torch_image, (torch_x, flame_frame_height - 5))  # Torch base (slight overlap)

                self.torch_frames.append(torch_complete)

            self.loaded = True
            print(
                f"TorchAnimation:  Loaded {len(self.torch_frames)} torch frames and {len(self.torch_glow_frames)} glow frames")

        except Exception as e:
            print(f"Error loading torch animation:  {e}")
            import traceback
            traceback.print_exc()
            # Create dummy frames as fallback
            self.torch_frames = [pygame.Surface((20, 30), pygame.SRCALPHA)]
            self.torch_glow_frames = [pygame.Surface((40, 40), pygame.SRCALPHA)]
            self.loaded = False

    def update(self):
        """Update torch animation frame"""
        if not self.loaded:
            return

        self.animation_counter += self.animation_speed

        if self.animation_counter >= 1.0:
            self.animation_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.torch_frames)

    def draw(self, screen, x, y):
        """Draw an animated torch with glow at position (x, y)"""
        if not self.loaded or not self.torch_frames or not self.torch_glow_frames:
            return

        glow = self.torch_glow_frames[self.frame_index]
        torch = self.torch_frames[self.frame_index]

        # Calculate torch center point
        torch_center_x = x + (torch.get_width() // 2)
        torch_flame_y = y + 10  # Position on the flame area

        # Center glow on the torch's flame
        glow_x = torch_center_x - (glow.get_width() // 2)
        glow_y = torch_flame_y - (glow.get_height() // 2)

        # Draw glow first (behind torch)
        screen.blit(glow, (glow_x, glow_y))

        # Draw torch with flame on top
        screen.blit(torch, (x, y))

    def set_speed(self, speed):
        """Set animation speed"""
        self.animation_speed = speed

# Global torch animation instance
torch_animation = None

def initialize_torch_animation():
    """Initialize torch animation"""
    global torch_animation
    if torch_animation is None:
        torch_animation = TorchAnimation()
        torch_animation.load()
    return torch_animation

def get_torch_animation():
    """Get torch animation instance"""
    return torch_animation