from api.io.Lightning.maze.MazeGenerator import MazeBuilder
from api.io.Lightning.utils.ConfigFile import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()

        pygame.display.set_caption("Mummy Maze Ultimate 1.0")
        icon = pygame.image.load(os.path.join(UI_PATH, 'game.ico'))
        pygame.display.set_icon(icon)

        self.maze = MazeBuilder('none')
        cell_size = self.maze.cell_size

    def run_game(self):
        while self.running:
            self.events()
            self.update()
            self.draw()

            self.clock.tick(fps)
        pygame.quit()