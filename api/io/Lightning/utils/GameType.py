from enum import Enum

class EnemyType(Enum):
    WHITE_MUMMY = "white_mummy"      # Horizontal priority, 2 moves
    RED_MUMMY = "red_mummy"          # Vertical priority, 2 moves
    SCORPION = "scorpion"            # Random/patrol, 1 move
    RED_SCORPION = "red_scorpion"    # Smart, 1 move

class Difficulty(Enum):
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"

class GameMode(Enum):
    CLASSIC = "classic"
    ADVENTURE = "adventure"
    TUTORIAL = "tutorial"
