from __future__ import annotations

from collections import deque
from typing import List, Optional, Dict

from .models import Maze, Coord, CellType


def shortest_path(maze: Maze, start: Coord, target: Coord) -> Optional[List[Coord]]:
    """
    BFS tìm đường đi ngắn nhất từ start -> target trên lưới ô,
    không đi xuyên WALL hoặc GATE_CLOSED.
    Trả về list toạ độ (bao gồm start và target) hoặc None nếu không có đường.
    """
    width, height = maze.width, maze.height
    blocked = {CellType.WALL, CellType.GATE_CLOSED}

    def neighbors(c: Coord):
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = c.x + dx, c.y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if maze.grid[ny][nx] not in blocked:
                    yield Coord(nx, ny)

    q = deque([start])
    prev: Dict[Coord, Optional[Coord]] = {start: None}

    while q:
        cur = q.popleft()
        if cur == target:
            # reconstruct path
            path: List[Coord] = []
            while cur is not None:
                path.append(cur)
                cur = prev[cur]
            path.reverse()
            return path

        for nb in neighbors(cur):
            if nb not in prev:
                prev[nb] = cur
                q.append(nb)

    return None
