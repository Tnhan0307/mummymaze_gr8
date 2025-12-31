from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple

from .config import Difficulty


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


@dataclass(frozen=True)
class Coord:
    x: int
    y: int

    def moved(self, dir: Direction) -> "Coord":
        if dir == Direction.UP:
            return Coord(self.x, self.y - 1)
        if dir == Direction.DOWN:
            return Coord(self.x, self.y + 1)
        if dir == Direction.LEFT:
            return Coord(self.x - 1, self.y)
        if dir == Direction.RIGHT:
            return Coord(self.x + 1, self.y)
        return self


class CellType(Enum):
    """
    Cell không còn dùng để biểu diễn tường nữa (tường = edge).
    WALL, GATE_* giữ lại cho tương thích nhưng không dùng trong Phase 2.
    """
    EMPTY = auto()
    WALL = auto()          # legacy
    START = auto()
    EXIT = auto()
    KEY = auto()
    GATE_CLOSED = auto()   # legacy (edge gate dùng gate_edge)
    GATE_OPEN = auto()     # legacy
    TRAP = auto()


class GameStatus(Enum):
    RUNNING = auto()
    WIN = auto()
    LOSE = auto()


class EnemyType(Enum):
    WHITE_MUMMY = auto()
    RED_MUMMY = auto()
    SCORPION = auto()


@dataclass
class Enemy:
    pos: Coord
    type: EnemyType


@dataclass
class Maze:
    """
    Mô hình board mới:
      - grid: chỉ chứa START/EXIT/KEY/TRAP/...; KHÔNG dùng WALL để chặn đường.
      - h_walls: danh sách cạnh tường ngang (PopCap style):
          (x, y) với 0 <= x < width, 0 <= y <= height
          -> tường nằm giữa hàng y-1 và y, trải từ cột x đến x+1
      - v_walls: danh sách cạnh tường dọc:
          (x, y) với 0 <= x <= width, 0 <= y < height
          -> tường nằm giữa cột x-1 và x, trải từ hàng y đến y+1
      - gate_edge: một cạnh đặc biệt đóng/mở, format ("h"/"v", x, y)
    """
    width: int
    height: int
    grid: List[List[CellType]]

    start: Coord
    exit: Coord
    key: Optional[Coord] = None
    traps: List[Coord] = field(default_factory=list)
    enemies_start: List[Enemy] = field(default_factory=list)

    # Edge walls
    h_walls: List[Tuple[int, int]] = field(default_factory=list)
    v_walls: List[Tuple[int, int]] = field(default_factory=list)
    gate_edge: Optional[Tuple[str, int, int]] = None  # ("h" | "v", x, y)


@dataclass
class GameState:
    maze: Maze
    player_pos: Coord
    enemies: List[Enemy] = field(default_factory=list)
    has_key: bool = False
    gate_open: bool = False
    status: GameStatus = GameStatus.RUNNING
    move_count: int = 0
    difficulty: Difficulty = Difficulty.NORMAL


class GameMode(Enum):
    NORMAL = "normal"
    RANDOM = "random"
