from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# ============================
# 1. ĐƯỜNG DẪN THƯ MỤC
# ============================

ROOT_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR   = ROOT_DIR / "assets"
OBJECTS_DIR  = ASSETS_DIR / "objects"
ENTITIES_DIR = ASSETS_DIR / "entities"
UI_DIR       = ASSETS_DIR / "ui"
MUSIC_DIR    = ASSETS_DIR / "music"
SFX_DIR      = ASSETS_DIR / "sfx"
LEVELS_DIR   = ASSETS_DIR / "levels"

SAVES_DIR      = ROOT_DIR / "saves"
GAMES_SAVE_DIR = SAVES_DIR / "games"
PROFILES_FILE  = SAVES_DIR / "profiles.json"

SAVES_DIR.mkdir(exist_ok=True)
GAMES_SAVE_DIR.mkdir(exist_ok=True)

# ============================
# 2. CỬA SỔ & HÌNH HỌC BOARD
# ============================

WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
FPS           = 60

# panel bên trái (Undo / Reset / Options / World map / Quit)
LEFT_PANEL_WIDTH = 220   # bạn có thể chỉnh 220 → 240 nếu muốn rộng hơn

# khoảng cách từ viền backdrop tới ô đầu tiên
BOARD_INSET = 32

# độ dày tường mỏng
WALL_THICK = 8

# fallback board logic mặc định (cho code cũ nếu có dùng)
BOARD_COLS_DEFAULT = 10
BOARD_ROWS_DEFAULT = 10

# ============================
# 3. ENUM: ĐỘ KHÓ, MODE, SIZE
# ============================

class Difficulty(str, Enum):
    EASY   = "easy"
    NORMAL = "normal"
    HARD   = "hard"


class GameMode(str, Enum):
    NORMAL = "normal"
    RANDOM = "random"


class BoardSize(str, Enum):
    SMALL  = "small"   # 6x6
    MEDIUM = "medium"  # 8x8
    LARGE  = "large"   # 10x10


# ============================
# 4. PROFILE VẼ BOARD
# ============================

@dataclass(frozen=True)
class BoardVisualProfile:
    size: BoardSize
    cols: int        # số cột logic của mê cung
    rows: int        # số hàng logic của mê cung
    tile_size: int   # kích thước 1 ô khi vẽ (pixel)
    suffix: str      # "6"/"8"/"10" để chọn đúng asset (floor6, walls8, ...)


# Ở đây mình scale mọi bộ về tile 48x48 cho dễ căn (bạn có thể đổi 48 nếu muốn)
TILE_SIZE_SMALL  = 48
TILE_SIZE_MEDIUM = 48
TILE_SIZE_LARGE  = 48

BOARD_PROFILES: dict[BoardSize, BoardVisualProfile] = {
    BoardSize.SMALL: BoardVisualProfile(
        size=BoardSize.SMALL,
        cols=6,
        rows=6,
        tile_size=TILE_SIZE_SMALL,
        suffix="6",
    ),
    BoardSize.MEDIUM: BoardVisualProfile(
        size=BoardSize.MEDIUM,
        cols=8,
        rows=8,
        tile_size=TILE_SIZE_MEDIUM,
        suffix="8",
    ),
    BoardSize.LARGE: BoardVisualProfile(
        size=BoardSize.LARGE,
        cols=10,
        rows=10,
        tile_size=TILE_SIZE_LARGE,
        suffix="10",
    ),
}

# ============================
# 5. ALIAS CHO CODE CŨ
# ============================

DEFAULT_BOARD_SIZE = BoardSize.LARGE
DEFAULT_PROFILE = BOARD_PROFILES[DEFAULT_BOARD_SIZE]

# một số file (vd logic, maze_data đời cũ) có thể vẫn dùng 3 hằng này:
TILE_SIZE = DEFAULT_PROFILE.tile_size
BOARD_COLS = DEFAULT_PROFILE.cols
BOARD_ROWS = DEFAULT_PROFILE.rows
