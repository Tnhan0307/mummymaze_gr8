from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Optional, Dict, Tuple

import pygame

from . import config, maze_data, logic
from .config import Difficulty
from .models import Maze, GameState, Coord, Direction, GameStatus, CellType, EnemyType

# Bao nhiêu level JSON trong Normal mode
NORMAL_LEVEL_MAX = 3


# ============================
# SESSION MODEL
# ============================


@dataclass
class GameSession:
    mode: str  # "normal" / "random"
    board_size: config.BoardSize
    profile: config.BoardVisualProfile
    level_index: int = 1
    moves: int = 0
    time_elapsed: float = 0.0

    def reset_level_stats(self) -> None:
        self.moves = 0
        self.time_elapsed = 0.0


# ============================
# ASSET LOADER
# ============================

BoardAssets = Dict[str, pygame.Surface]


def _load_first_image(directory: config.PathLike, patterns: list[str]) -> Optional[pygame.Surface]:
    """
    Thử lần lượt các pattern, lấy file đầu tiên load được.
    Nếu không có file khớp pattern hoặc load lỗi => trả về None.
    """
    path_dir = directory
    for pattern in patterns:
        for path in path_dir.glob(pattern):
            try:
                img = pygame.image.load(str(path)).convert_alpha()
                return img
            except pygame.error:
                continue
    return None


def load_board_assets(profile: config.BoardVisualProfile) -> BoardAssets:
    """
    Loader linh hoạt, bám theo tên file thực tế trong assets:
      - backwall6/8/10.jpg: nền board
      - floor6/8/10.jpg: sàn
      - walls6/8/10.gif hoặc block6/8/10.gif: sprite tường
      - stairs6/8/10.gif: exit
      - trap6/8/10.png: bẫy
      - key.png: chìa
      - gate6/8/10.gif: cổng
      - explorer6/8/10.png, mummy6/8/10.png, redmummy6/8/10.png, scorpion6/8/10.png
    """
    assets: BoardAssets = {}
    n = profile.cols  # 6, 8, 10

    obj_dir = config.OBJECTS_DIR
    ent_dir = config.ENTITIES_DIR
    ui_dir = config.UI_DIR

    # background (khung board)
    assets["board_bg"] = _load_first_image(
        obj_dir, [f"backwall{n}.*", "backwall*.*", "backdrop*.*"]
    )

    # floor
    assets["floor"] = _load_first_image(
        obj_dir, [f"floor{n}.*", "floor*.*"]
    )

    # walls
    wall_img = _load_first_image(
        obj_dir, [f"walls{n}.*", "walls*.*", f"block{n}.*", "block*.*"]
    )
    if wall_img is not None:
        assets["wall_raw"] = wall_img

    # exit (stairs)
    assets["exit"] = _load_first_image(
        obj_dir, [f"stairs{n}.*", "stairs*.*", "exit*.*"]
    )

    # key
    assets["key"] = _load_first_image(obj_dir, ["key*.*"])

    # trap (skull)
    assets["trap"] = _load_first_image(
        obj_dir, [f"trap{n}.*", "trap*.*", "skull*.*"]
    )

    # gate
    assets["gate_closed"] = _load_first_image(
        obj_dir, [f"gate{n}.*", "gate*.*"]
    )
    assets["gate_open"] = _load_first_image(
        obj_dir, [f"gateopen{n}.*", "gateopen*.*", "gate*open*.*"]
    ) or assets["gate_closed"]

    # entities
    assets["player"] = _load_first_image(
        ent_dir, [f"explorer{n}.*", "explorer*.*"]
    )
    assets["white_mummy"] = _load_first_image(
        ent_dir, [f"mummy{n}.*", "mummy*.*", "whitemummy*.*"]
    )
    assets["red_mummy"] = _load_first_image(
        ent_dir, [f"redmummy{n}.*", "redmummy*.*", "red*.*"]
    )
    assets["scorpion"] = _load_first_image(
        ent_dir, [f"scorpion{n}.*", "scorpion*.*"]
    )

    # art panel bên trái (dùng menufront.png cho nhanh)
    assets["left_art"] = _load_first_image(
        ui_dir, ["menufront*.*", "menu*front*.*", "mummy*.*"]
    )

    return assets


# ============================
# BOARD RENDERER (EDGE WALLS)
# ============================


def build_board_surface(
    maze: Maze,
    state: GameState,
    assets: BoardAssets,
    profile: config.BoardVisualProfile,
) -> pygame.Surface:
    cols, rows = maze.width, maze.height
    tile = profile.tile_size

    board_w = cols * tile + 2 * config.BOARD_INSET
    board_h = rows * tile + 2 * config.BOARD_INSET

    surface = pygame.Surface((board_w, board_h), pygame.SRCALPHA)

    # 1) background frame
    bg = assets.get("board_bg")
    if bg is not None:
        bg_scaled = pygame.transform.smoothscale(bg, (board_w, board_h))
        surface.blit(bg_scaled, (0, 0))
    else:
        surface.fill((40, 30, 15))

    # 2) floor tiles
    floor = assets.get("floor")
    if floor is not None:
        floor_scaled = pygame.transform.smoothscale(floor, (tile, tile))
    else:
        floor_scaled = None

    for y in range(rows):
        for x in range(cols):
            px = config.BOARD_INSET + x * tile
            py = config.BOARD_INSET + y * tile
            if floor_scaled:
                surface.blit(floor_scaled, (px, py))
            else:
                pygame.draw.rect(surface, (90, 72, 50), (px, py, tile, tile))

    # 3) walls (edge-based)
    wall_raw = assets.get("wall_raw")
    thickness = max(4, tile // 8)

    def draw_h_wall(x: int, y: int) -> None:
        px = config.BOARD_INSET + x * tile
        py = config.BOARD_INSET + y * tile - thickness // 2
        if wall_raw:
            wall = pygame.transform.smoothscale(wall_raw, (tile, thickness))
            surface.blit(wall, (px, py))
        else:
            pygame.draw.rect(surface, (20, 10, 5), (px, py, tile, thickness))

    def draw_v_wall(x: int, y: int) -> None:
        px = config.BOARD_INSET + x * tile - thickness // 2
        py = config.BOARD_INSET + y * tile
        if wall_raw:
            wall = pygame.transform.smoothscale(wall_raw, (thickness, tile))
            surface.blit(wall, (px, py))
        else:
            pygame.draw.rect(surface, (20, 10, 5), (px, py, thickness, tile))

    for x, y in maze.h_walls:
        draw_h_wall(x, y)
    for x, y in maze.v_walls:
        draw_v_wall(x, y)

    # 4) EXIT / KEY / TRAP (cell-based)
    exit_img = assets.get("exit")
    key_img = assets.get("key")
    trap_img = assets.get("trap")

    for y in range(rows):
        for x in range(cols):
            cell = maze.grid[y][x]
            px = config.BOARD_INSET + x * tile
            py = config.BOARD_INSET + y * tile
            rect = pygame.Rect(px, py, tile, tile)

            if cell == CellType.EXIT and exit_img:
                img = pygame.transform.smoothscale(exit_img, rect.size)
                surface.blit(img, rect.topleft)
            elif cell == CellType.KEY and key_img:
                img = pygame.transform.smoothscale(key_img, rect.size)
                surface.blit(img, rect.topleft)
            elif cell == CellType.TRAP and trap_img:
                img = pygame.transform.smoothscale(trap_img, rect.size)
                surface.blit(img, rect.topleft)

    # 5) Gate sprite (dùng 1 ô gần cạnh gate để hiển thị)
    gate_closed_img = assets.get("gate_closed")
    gate_open_img = assets.get("gate_open") or gate_closed_img
    if maze.gate_edge and gate_closed_img:
        kind, gx, gy = maze.gate_edge
        if kind == "h":
            cell_x, cell_y = gx, max(0, gy - 1)
        else:
            cell_x, cell_y = max(0, gx - 1), gy
        if 0 <= cell_x < cols and 0 <= cell_y < rows:
            px = config.BOARD_INSET + cell_x * tile
            py = config.BOARD_INSET + cell_y * tile
            gate_img = gate_open_img if state.gate_open else gate_closed_img
            img = pygame.transform.smoothscale(gate_img, (tile, tile))
            surface.blit(img, (px, py))

    # 6) Player
    player_img = assets.get("player")
    px = config.BOARD_INSET + state.player_pos.x * tile
    py = config.BOARD_INSET + state.player_pos.y * tile
    if player_img:
        img = pygame.transform.smoothscale(player_img, (tile, tile))
        surface.blit(img, (px, py))
    else:
        pygame.draw.circle(
            surface,
            (0, 220, 0),
            (px + tile // 2, py + tile // 2),
            tile // 3,
        )

    # 7) Enemies
    for enemy in state.enemies:
        if enemy.type == EnemyType.WHITE_MUMMY:
            key = "white_mummy"
        elif enemy.type == EnemyType.RED_MUMMY:
            key = "red_mummy"
        else:
            key = "scorpion"
        e_img = assets.get(key)
        ex = config.BOARD_INSET + enemy.pos.x * tile
        ey = config.BOARD_INSET + enemy.pos.y * tile
        if e_img:
            img = pygame.transform.smoothscale(e_img, (tile, tile))
            surface.blit(img, (ex, ey))
        else:
            pygame.draw.circle(
                surface,
                (220, 220, 0),
                (ex + tile // 2, ey + tile // 2),
                tile // 3,
            )

    return surface


# ============================
# SCREEN BASE
# ============================


class Screen:
    def __init__(self, app: "App") -> None:
        self.app = app

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass


# ============================
# MAIN MENU
# ============================


class MainMenuScreen(Screen):
    def __init__(self, app: "App") -> None:
        super().__init__(app)
        self.font_big = pygame.font.SysFont("arial", 48, bold=True)
        self.font_small = pygame.font.SysFont("arial", 24)
        self.options = ["Normal Mode", "Random Mode (WIP)", "Quit"]
        self.selected = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate(self.selected)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            w, h = self.app.window.get_size()
            cx = w // 2
            start_y = h // 2 - len(self.options) * 30
            for i, label in enumerate(self.options):
                text_surf = self.font_small.render(label, True, (255, 255, 255))
                rect = text_surf.get_rect(center=(cx, start_y + i * 60))
                if rect.collidepoint(mx, my):
                    self._activate(i)
                    break

    def _activate(self, index: int) -> None:
        label = self.options[index]
        if "Normal" in label:
            self.app.start_campaign()
        elif "Random" in label:
            self.app.set_screen(NotImplementedScreen(self.app, "Random mode is not implemented yet."))
        else:
            pygame.quit()
            sys.exit(0)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((10, 5, 0))
        title = self.font_big.render("MUMMY MAZE", True, (255, 220, 120))
        title_rect = title.get_rect(center=(config.WINDOW_WIDTH // 2, 140))
        surface.blit(title, title_rect)

        cx = config.WINDOW_WIDTH // 2
        start_y = config.WINDOW_HEIGHT // 2 - len(self.options) * 30

        for i, label in enumerate(self.options):
            color = (255, 255, 255) if i != self.selected else (255, 240, 170)
            text = self.font_small.render(label, True, color)
            rect = text.get_rect(center=(cx, start_y + i * 60))
            surface.blit(text, rect)

        hint = self.font_small.render("Use W/S or Up/Down, Enter to select", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - 80))
        surface.blit(hint, hint_rect)


class NotImplementedScreen(Screen):
    def __init__(self, app: "App", message: str) -> None:
        super().__init__(app)
        self.font_big = pygame.font.SysFont("arial", 36, bold=True)
        self.font_small = pygame.font.SysFont("arial", 24)
        self.message = message

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN or (
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        ):
            self.app.set_screen(MainMenuScreen(self.app))

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((15, 5, 0))
        title = self.font_big.render("Coming Soon", True, (255, 220, 120))
        rect = title.get_rect(center=(config.WINDOW_WIDTH // 2, 160))
        surface.blit(title, rect)

        msg = self.font_small.render(self.message, True, (230, 230, 230))
        msg_rect = msg.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2))
        surface.blit(msg, msg_rect)

        hint = self.font_small.render("Press any key to return", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - 80))
        surface.blit(hint, hint_rect)


# ============================
# GAMEPLAY
# ============================


def _direction_from(src: Coord, dst: Coord) -> Optional[Direction]:
    dx = dst.x - src.x
    dy = dst.y - src.y
    if abs(dx) > abs(dy):
        if dx > 0:
            return Direction.RIGHT
        elif dx < 0:
            return Direction.LEFT
    elif abs(dy) > 0:
        if dy > 0:
            return Direction.DOWN
        elif dy < 0:
            return Direction.UP
    return None


def get_player_coord(state: GameState) -> Coord:
    return state.player_pos


class GameplayScreen(Screen):
    def __init__(self, app: "App") -> None:
        super().__init__(app)
        self.font_small = pygame.font.SysFont("arial", 20)
        self.font_medium = pygame.font.SysFont("arial", 24, bold=True)
        self.hover_cell: Optional[Coord] = None

    # --- board helpers ---

    def _board_surface_and_rect(self) -> Tuple[pygame.Surface, pygame.Rect]:
        assert self.app.session is not None
        assert self.app.state is not None
        profile = self.app.session.profile
        board_surf = build_board_surface(
            self.app.state.maze, self.app.state, self.app.board_assets, profile
        )
        bx = config.LEFT_PANEL_WIDTH + (config.WINDOW_WIDTH - config.LEFT_PANEL_WIDTH - board_surf.get_width()) // 2
        by = (config.WINDOW_HEIGHT - board_surf.get_height()) // 2
        rect = board_surf.get_rect(topleft=(bx, by))
        return board_surf, rect

    def _cell_from_mouse(self, mx: int, my: int) -> Optional[Coord]:
        board_surf, rect = self._board_surface_and_rect()
        if not rect.collidepoint(mx, my):
            return None

        assert self.app.session is not None
        profile = self.app.session.profile
        tile = profile.tile_size

        local_x = mx - rect.left - config.BOARD_INSET
        local_y = my - rect.top - config.BOARD_INSET
        if local_x < 0 or local_y < 0:
            return None

        col = local_x // tile
        row = local_y // tile
        maze = self.app.state.maze
        if 0 <= col < maze.width and 0 <= row < maze.height:
            return Coord(int(col), int(row))
        return None

    # --- events ---

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.app.state is None or self.app.session is None:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.set_screen(PauseScreen(self.app))
                return

            dir_map = {
                pygame.K_w: Direction.UP,
                pygame.K_UP: Direction.UP,
                pygame.K_s: Direction.DOWN,
                pygame.K_DOWN: Direction.DOWN,
                pygame.K_a: Direction.LEFT,
                pygame.K_LEFT: Direction.LEFT,
                pygame.K_d: Direction.RIGHT,
                pygame.K_RIGHT: Direction.RIGHT,
            }
            if event.key in dir_map:
                self._try_move(dir_map[event.key])

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self.hover_cell = self._cell_from_mouse(mx, my)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            tgt = self._cell_from_mouse(mx, my)
            if tgt is None:
                return
            player = get_player_coord(self.app.state)
            direction = _direction_from(player, tgt)
            if direction is not None:
                self._try_move(direction)

    def _try_move(self, direction: Direction) -> None:
        if self.app.state is None or self.app.session is None:
            return
        logic.apply_turn(self.app.state, direction)
        self.app.session.moves = self.app.state.move_count
        self._check_level_end()

    def _check_level_end(self) -> None:
        state = self.app.state
        if state is None:
            return
        if state.status == GameStatus.WIN:
            self.app.set_screen(LevelClearScreen(self.app))
        elif state.status == GameStatus.LOSE:
            self.app.set_screen(LevelFailScreen(self.app))

    def update(self, dt: float) -> None:
        if self.app.session and self.app.state and self.app.state.status == GameStatus.RUNNING:
            self.app.session.time_elapsed += dt

    # --- drawing ---

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))
        if self.app.session is None or self.app.state is None:
            return

        session = self.app.session
        state = self.app.state

        # Left panel
        panel_rect = pygame.Rect(0, 0, config.LEFT_PANEL_WIDTH, config.WINDOW_HEIGHT)
        pygame.draw.rect(surface, (30, 18, 8), panel_rect)

        left_art = self.app.board_assets.get("left_art")
        if left_art:
            art_h = int(config.WINDOW_HEIGHT * 0.6)
            art_w = int(left_art.get_width() * (art_h / left_art.get_height()))
            art_scaled = pygame.transform.smoothscale(left_art, (art_w, art_h))
            surface.blit(art_scaled, (panel_rect.centerx - art_w // 2, 30))

        y_stat = config.WINDOW_HEIGHT - 160
        label = self.font_medium.render("NORMAL MODE", True, (255, 230, 160))
        surface.blit(label, (20, y_stat))
        y_stat += 30

        moves_txt = self.font_small.render(f"Moves: {session.moves}", True, (255, 255, 255))
        surface.blit(moves_txt, (20, y_stat))
        y_stat += 24

        time_txt = self.font_small.render(f"Time: {session.time_elapsed:5.1f}s", True, (255, 255, 255))
        surface.blit(time_txt, (20, y_stat))
        y_stat += 30

        hint = self.font_small.render("WASD / Arrows to move", True, (220, 220, 220))
        surface.blit(hint, (20, y_stat))

        # Board
        board_surf, rect = self._board_surface_and_rect()

        # hover highlight + arrow overlay
        profile = session.profile
        tile = profile.tile_size

        if self.hover_cell is not None:
            hc = self.hover_cell
            if 0 <= hc.x < state.maze.width and 0 <= hc.y < state.maze.height:
                highlight = pygame.Surface((tile, tile), pygame.SRCALPHA)
                highlight.fill((255, 255, 0, 60))
                lx = config.BOARD_INSET + hc.x * tile
                ly = config.BOARD_INSET + hc.y * tile
                board_surf.blit(highlight, (lx, ly))

                player = get_player_coord(state)
                direction = _direction_from(player, hc)
                if direction is not None:
                    arrow = pygame.Surface((tile, tile), pygame.SRCALPHA)
                    cx = tile // 2
                    cy = tile // 2
                    m = 6
                    if direction == Direction.UP:
                        pts = [(cx, m), (m, tile - m), (tile - m, tile - m)]
                    elif direction == Direction.DOWN:
                        pts = [(m, m), (tile - m, m), (cx, tile - m)]
                    elif direction == Direction.LEFT:
                        pts = [(m, cy), (tile - m, m), (tile - m, tile - m)]
                    else:  # RIGHT
                        pts = [(m, m), (m, tile - m), (tile - m, cy)]
                    pygame.draw.polygon(arrow, (255, 255, 0, 200), pts)
                    px = config.BOARD_INSET + player.x * tile
                    py = config.BOARD_INSET + player.y * tile
                    board_surf.blit(arrow, (px, py))

        surface.blit(board_surf, rect.topleft)


# ============================
# PAUSE & RESULT SCREENS
# ============================


class PauseScreen(Screen):
    def __init__(self, app: "App") -> None:
        super().__init__(app)
        self.font_big = pygame.font.SysFont("arial", 40, bold=True)
        self.font_small = pygame.font.SysFont("arial", 24)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                self.app.set_screen(GameplayScreen(self.app))
            elif event.key == pygame.K_q:
                self.app.set_screen(MainMenuScreen(self.app))

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))
        title = self.font_big.render("Paused", True, (255, 230, 160))
        rect = title.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 40))
        surface.blit(title, rect)

        hint1 = self.font_small.render("ESC / Enter: Resume", True, (230, 230, 230))
        hint2 = self.font_small.render("Q: Quit to main menu", True, (230, 230, 230))
        rect1 = hint1.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 10))
        rect2 = hint2.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 40))
        surface.blit(hint1, rect1)
        surface.blit(hint2, rect2)


class LevelClearScreen(Screen):
    def __init__(self, app: "App") -> None:
        super().__init__(app)
        self.font_big = pygame.font.SysFont("arial", 40, bold=True)
        self.font_small = pygame.font.SysFont("arial", 24)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN or (
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        ):
            self._next_level()

    def _next_level(self) -> None:
        if self.app.session is None:
            self.app.set_screen(MainMenuScreen(self.app))
            return
        next_index = self.app.session.level_index + 1
        if next_index > NORMAL_LEVEL_MAX:
            next_index = 1
        self.app.start_level(next_index)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))
        title = self.font_big.render("Level Clear!", True, (255, 230, 160))
        rect = title.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 40))
        surface.blit(title, rect)

        msg = self.font_small.render("Press any key to continue", True, (230, 230, 230))
        rect2 = msg.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 20))
        surface.blit(msg, rect2)


class LevelFailScreen(Screen):
    def __init__(self, app: "App") -> None:
        super().__init__(app)
        self.font_big = pygame.font.SysFont("arial", 40, bold=True)
        self.font_small = pygame.font.SysFont("arial", 24)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN or (
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        ):
            if self.app.session is None:
                self.app.set_screen(MainMenuScreen(self.app))
            else:
                self.app.start_level(self.app.session.level_index)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))
        title = self.font_big.render("You were caught!", True, (255, 100, 80))
        rect = title.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 40))
        surface.blit(title, rect)

        msg = self.font_small.render("Press any key to retry", True, (230, 230, 230))
        rect2 = msg.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 20))
        surface.blit(msg, rect2)


# ============================
# APP ROOT
# ============================


class App:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Mummy Maze - CSLTAI")
        self.window = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))

        # tạm chọn profile LARGE, sẽ cập nhật theo level thực
        default_size = config.BoardSize.LARGE
        default_profile = config.BOARD_PROFILES[default_size]
        self.board_assets: BoardAssets = load_board_assets(default_profile)

        self.clock = pygame.time.Clock()
        self.session: Optional[GameSession] = None
        self.state: Optional[GameState] = None

        self.current_screen: Screen = MainMenuScreen(self)

    def set_screen(self, screen: Screen) -> None:
        self.current_screen = screen

    # -------- NORMAL CAMPAIGN --------

    def start_campaign(self) -> None:
        """
        Normal mode: chạy level_01 (6x6) -> 02 (8x8) -> 03 (10x10) -> quay lại 1.
        """
        profile = config.BOARD_PROFILES[config.BoardSize.SMALL]
        self.board_assets = load_board_assets(profile)
        self.session = GameSession(
            mode="normal",
            board_size=config.BoardSize.SMALL,
            profile=profile,
            level_index=1,
        )
        self.start_level(1)

    def start_level(self, level_index: int) -> None:
        if self.session is None:
            return

        self.session.level_index = level_index
        self.session.reset_level_stats()

        maze = self._load_maze_for_session(self.session, level_index)

        # cập nhật profile theo kích thước board (6 / 8 / 10)
        if maze.width <= 6:
            board_size = config.BoardSize.SMALL
        elif maze.width <= 8:
            board_size = config.BoardSize.MEDIUM
        else:
            board_size = config.BoardSize.LARGE

        profile = config.BOARD_PROFILES[board_size]
        self.session.board_size = board_size
        self.session.profile = profile
        self.board_assets = load_board_assets(profile)

        self.state = logic.initial_state(maze, Difficulty.NORMAL)
        self.current_screen = GameplayScreen(self)

    def _load_maze_for_session(self, session: GameSession, level_index: int) -> Maze:
        if session.mode == "normal":
            return maze_data.load_level_json(level_index)
        # random mode (tạm disable)
        raise RuntimeError("Random mode should not call _load_maze_for_session in Phase 2.")

    # -------- MAIN LOOP --------

    def run(self) -> None:
        running = True
        while running:
            dt_ms = self.clock.tick(config.FPS)
            dt = dt_ms / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                self.current_screen.handle_event(event)

            self.current_screen.update(dt)
            self.current_screen.draw(self.window)
            pygame.display.flip()

        pygame.quit()


# ============================
# ENTRY POINT
# ============================


def run_app() -> None:
    app = App()
    app.run()


if __name__ == "__main__":
    run_app()
