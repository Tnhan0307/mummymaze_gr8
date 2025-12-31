from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple, Optional

from .config import LEVELS_DIR, Difficulty
from .models import Maze, CellType, Coord, Enemy, EnemyType

# Số level JSON dùng cho Normal mode
NORMAL_LEVEL_COUNT = 3


# ============================
# HÀM PHỤ
# ============================


def _coord_from_list(raw, name: str, width: int, height: int) -> Coord:
    """Chuyển [x, y] trong JSON thành Coord và kiểm tra biên."""
    if not isinstance(raw, (list, tuple)) or len(raw) != 2:
        raise ValueError(f"{name} phải là list [x, y]")
    x, y = int(raw[0]), int(raw[1])
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(f"{name} ({x},{y}) nằm ngoài board {width}x{height}")
    return Coord(x, y)


# ============================
# LOAD LEVEL TỪ JSON
# ============================


def load_level_json(level_index: int) -> Maze:
    """
    Đọc level_{XX}.json trong assets/levels theo schema:

    {
      "size": 6,

      "start": [x, y],
      "exit": [x, y],
      "key": [x, y] | null,

      "traps": [[x, y], ...],

      "enemies": [
        {"type": "white_mummy", "pos": [x, y]},
        {"type": "red_mummy",   "pos": [x, y]},
        {"type": "scorpion",    "pos": [x, y]}
      ],

      "walls": {
        "h": [[x, y], ...],   // cạnh ngang
        "v": [[x, y], ...]    // cạnh dọc
      },

      "gate": {"dir": "h" | "v", "x": x, "y": y} | null
    }
    """
    name = f"level_{level_index:02d}.json"
    path: Path = LEVELS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file level JSON: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # ---- Kích thước board ----
    size = int(data.get("size") or data.get("width") or data.get("height") or 0)
    if size <= 0:
        raise ValueError("Level JSON phải có 'size' (ví dụ 6 / 8 / 10).")

    width = height = size

    # Khởi tạo grid toàn EMPTY
    grid: List[List[CellType]] = [
        [CellType.EMPTY for _ in range(width)] for _ in range(height)
    ]

    # ---- Start / Exit / Key / Traps ----
    start = _coord_from_list(data["start"], "start", width, height)
    exit_ = _coord_from_list(data["exit"], "exit", width, height)

    key_raw = data.get("key")
    key: Optional[Coord] = None
    if key_raw is not None:
        key = _coord_from_list(key_raw, "key", width, height)

    traps: List[Coord] = []
    for t in data.get("traps", []):
        c = _coord_from_list(t, "trap", width, height)
        traps.append(c)

    # ---- Enemies ----
    enemies: List[Enemy] = []
    for e in data.get("enemies", []):
        t_str = str(e.get("type", "")).lower()
        pos = _coord_from_list(e.get("pos"), "enemy.pos", width, height)

        if "white" in t_str:
            et = EnemyType.WHITE_MUMMY
        elif "red" in t_str:
            et = EnemyType.RED_MUMMY
        elif "scorpion" in t_str:
            et = EnemyType.SCORPION
        else:
            # Type lạ thì bỏ qua
            continue
        enemies.append(Enemy(pos=pos, type=et))

    # ---- Walls (edge-based) ----
    walls = data.get("walls", {}) or {}
    h_walls: List[Tuple[int, int]] = []
    for item in walls.get("h", []):
        x, y = int(item[0]), int(item[1])
        h_walls.append((x, y))

    v_walls: List[Tuple[int, int]] = []
    for item in walls.get("v", []):
        x, y = int(item[0]), int(item[1])
        v_walls.append((x, y))

    # ---- Gate edge ----
    gate_edge: Optional[Tuple[str, int, int]] = None
    gate_data = data.get("gate")
    if gate_data:
        dir_str = str(gate_data.get("dir", "h")).lower()
        if dir_str not in ("h", "v"):
            raise ValueError("gate.dir phải là 'h' hoặc 'v'")
        gx = int(gate_data["x"])
        gy = int(gate_data["y"])
        gate_edge = (dir_str, gx, gy)

    # ---- set cell types ----
    grid[start.y][start.x] = CellType.START
    grid[exit_.y][exit_.x] = CellType.EXIT
    if key is not None:
        grid[key.y][key.x] = CellType.KEY
    for t in traps:
        grid[t.y][t.x] = CellType.TRAP

    # ---- tạo Maze ----
    maze = Maze(
        width=width,
        height=height,
        grid=grid,
        start=start,
        exit=exit_,
        key=key,
        traps=traps,
        enemies_start=enemies,
        h_walls=h_walls,
        v_walls=v_walls,
        gate_edge=gate_edge,
    )
    return maze


# ============================
# LEGACY / RANDOM (STUB)
# ============================


def load_level_txt(size: int, level_index: int) -> Maze:  # type: ignore[override]
    """
    Stub giữ lại cho tương thích cũ. Không dùng nữa.
    """
    raise RuntimeError("Legacy TXT levels are not supported in this build. Use JSON levels instead.")


def generate_random_maze(
    width: int,
    height: int,
    difficulty: Difficulty = Difficulty.NORMAL,
) -> Maze:
    """
    Stub cho Random mode (Phase 3). Hiện tại không dùng.
    """
    raise NotImplementedError("Random maze generation is not implemented in this phase.")
