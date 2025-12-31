from __future__ import annotations

from typing import List

from .config import Difficulty
from .models import (
    Maze,
    GameState,
    Coord,
    Direction,
    CellType,
    GameStatus,
    Enemy,
    EnemyType,
)


def initial_state(maze: Maze, difficulty: Difficulty = Difficulty.NORMAL) -> GameState:
    """
    Khởi tạo GameState từ Maze.
    """
    enemies: List[Enemy] = [Enemy(e.pos, e.type) for e in maze.enemies_start]
    state = GameState(
        maze=maze,
        player_pos=maze.start,
        enemies=enemies,
        has_key=False,
        gate_open=False,
        status=GameStatus.RUNNING,
        move_count=0,
        difficulty=difficulty,
    )
    return state


# ============================
# CORE TURN LOGIC
# ============================


def apply_turn(state: GameState, direction: Direction) -> None:
    """
    Một lượt chơi:
      1. Player di chuyển 1 ô (nếu hợp lệ).
      2. Xử lý key / trap / exit.
      3. Enemy di chuyển.
      4. Check va chạm (bao gồm trường hợp "đi xuyên qua nhau" -> chết).
    """
    if state.status is not GameStatus.RUNNING:
        return

    maze = state.maze
    old_player_pos = state.player_pos

    # 1. Player move (edge-based walls + gate)
    target = old_player_pos.moved(direction)
    if not _is_inside(maze, target):
        return
    if _edge_blocked(maze, state, old_player_pos, direction):
        return

    state.player_pos = target
    state.move_count += 1

    # 2. xử lý ô player đứng
    target_cell = maze.grid[target.y][target.x]

    if target_cell == CellType.KEY:
        state.has_key = True
        # Phase 2: đơn giản hóa: lấy key là mở gate luôn
        state.gate_open = True
        maze.grid[target.y][target.x] = CellType.EMPTY

    if target_cell == CellType.TRAP:
        state.status = GameStatus.LOSE
        return

    if target_cell == CellType.EXIT:
        state.status = GameStatus.WIN
        return

    # 3. Enemy move
    if state.enemies:
        old_enemy_positions = [e.pos for e in state.enemies]
        _move_enemies_towards_player(state)

        # 4. Check enemy collide (bao gồm swap vị trí)
        new_player_pos = state.player_pos
        for enemy, old_e_pos in zip(state.enemies, old_enemy_positions):
            # cùng ô
            if enemy.pos == new_player_pos:
                state.status = GameStatus.LOSE
                return
            # swap vị trí: enemy mới ở chỗ player cũ và ngược lại
            if enemy.pos == old_player_pos and old_e_pos == new_player_pos:
                state.status = GameStatus.LOSE
                return


# ============================
# HELPERS
# ============================


def _is_inside(maze: Maze, c: Coord) -> bool:
    return 0 <= c.x < maze.width and 0 <= c.y < maze.height


def _edge_blocked(maze: Maze, state: GameState, c: Coord, direction: Direction) -> bool:
    """
    Kiểm tra cạnh giữa ô c và ô phía direction có bị chặn không
    (tường edge hoặc gate đang đóng).
    """
    x, y = c.x, c.y
    if direction == Direction.UP:
        edge = ("h", x, y)  # giữa hàng y-1 và y
    elif direction == Direction.DOWN:
        edge = ("h", x, y + 1)
    elif direction == Direction.LEFT:
        edge = ("v", x, y)
    else:  # RIGHT
        edge = ("v", x + 1, y)

    kind, ex, ey = edge

    # Gate edge
    if maze.gate_edge is not None:
        gk, gx, gy = maze.gate_edge
        if gk == kind and gx == ex and gy == ey:
            # gate đóng => ai cũng không đi qua
            if not state.gate_open:
                return True

    # Tường thường
    if kind == "h":
        return (ex, ey) in maze.h_walls
    else:
        return (ex, ey) in maze.v_walls


def _move_enemies_towards_player(state: GameState) -> None:
    """
    AI đơn giản:
      - White/Red mummy: tối đa 2 bước/lượt, luôn đi hướng giảm Manhattan distance
      - Scorpion: 1 bước/lượt
    Tôn trọng tường edge + gate.
    """
    maze = state.maze
    if not state.enemies:
        return

    for enemy in state.enemies:
        steps = 2 if enemy.type in (EnemyType.WHITE_MUMMY, EnemyType.RED_MUMMY) else 1
        for _ in range(steps):
            new_pos = _best_step_towards(maze, state, enemy.pos, state.player_pos)
            if new_pos == enemy.pos:
                break
            enemy.pos = new_pos
            if enemy.pos == state.player_pos:
                # sẽ được check sau ở apply_turn
                break


def _best_step_towards(maze: Maze, state: GameState, start: Coord, target: Coord) -> Coord:
    """
    Thử 4 hướng, chọn hướng hợp lệ (không văng khỏi board, không bị tường/gate chặn)
    làm giảm khoảng cách Manhattan. Nếu không có hướng nào tốt hơn thì đứng yên.
    """
    best = start
    best_dist = _manhattan(start, target)

    for direction in (Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT):
        candidate = start.moved(direction)
        if not _is_inside(maze, candidate):
            continue
        if _edge_blocked(maze, state, start, direction):
            continue
        d = _manhattan(candidate, target)
        if d < best_dist:
            best_dist = d
            best = candidate

    return best


def _manhattan(a: Coord, b: Coord) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)
