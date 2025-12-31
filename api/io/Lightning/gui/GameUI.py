import pygame
import os
from enum import Enum

from api.io.Lightning.gui.MapTracker import WorldMapPanel
from api.io.Lightning.manager.SoundReader import sfx_manager, music_manager
from api.io.Lightning.manager.TextDesigner import PyramidFont
from api.io.Lightning.maze.MazeLoader import MazeLoader
from api.io.Lightning.listener.AnimatedListener import initialize_torch_animation
from api.io.Lightning.utils.ConfigFile import *
from api.io.Lightning.manager.ButtonManager import ButtonManager
from api.io.Lightning.entities.Player import Player, PlayerState


class TurnState(Enum):
    PLAYER_INPUT = 0
    PLAYER_MOVING = 1
    ENEMY_TURN = 2
    ENEMY_MOVING = 3
    PLAYER_DYING = 4
    FIGHT_PAUSE = 5


_button_manager = None
_torch_animation = None
_maze_loader = None
_maze_size = None
_player = None
_world_map = None
_turn_state = TurnState.PLAYER_INPUT
_death_timer = 0
_killer_ref = None
_death_step = 0
_death_step_timer = 0
_fight_pause_timer = 0
_show_options = False

# ✅ Cache UI images (load 1 lần, dùng lại)
_snake_img = None
_mumlogo_img = None


def _get_ui_images():
    """Load/cached snake + mumlogo once to avoid reloading every frame."""
    global _snake_img, _mumlogo_img

    if _snake_img is None:
        _snake_img = pygame.image.load(os.path.join(UI_PATH, "snake.png")).convert_alpha()

    if _mumlogo_img is None:
        _mumlogo_img = pygame.image.load(os.path.join(UI_PATH, "mumlogo.png")).convert_alpha()

    return _snake_img, _mumlogo_img

def _reset_runtime_state():
    global _turn_state, _death_timer, _killer_ref
    global _death_step, _death_step_timer, _fight_pause_timer
    global _show_options

    _turn_state = TurnState.PLAYER_INPUT
    _death_timer = 0
    _killer_ref = None
    _death_step = 0
    _death_step_timer = 0
    _fight_pause_timer = 0
    _show_options = False

def initialize_ui(mode="random", level_id=1, size=8, difficulty="medium"):
    global _button_manager, _torch_animation, _maze_loader, _player, _turn_state, _world_map
    global _snake_img, _mumlogo_img, _maze_size

    # ✅ reset cache when init (optional but safe)
    _snake_img = None
    _mumlogo_img = None

    _maze_size = size  # lưu để debug nếu cần
    _reset_runtime_state()

    _button_manager = ButtonManager()
    _torch_animation = initialize_torch_animation()
    sfx_manager.initialize()
    music_manager.initialize()
    _world_map = WorldMapPanel(x=8, y=320)

    try:
        if mode == "campaign":
            _maze_loader = MazeLoader(level_id=level_id, difficulty=None, generate_infinite=False)
        else:
            _maze_loader = MazeLoader(level_id=None, difficulty=difficulty, generate_infinite=True, maze_size=size)
    except Exception as e:
        print(f"⚠️ MazeLoader init failed (mode={mode}, level_id={level_id}): {e}")
        # fallback để game vẫn chạy
        _maze_loader = MazeLoader(level_id=None, difficulty=difficulty, generate_infinite=True, maze_size=size)
        mode = "random"

    if _maze_loader and _maze_loader.parsed:
        p = _maze_loader.parsed["player"]
        _player = Player(p["x"], p["y"], _maze_loader.maze_size, _maze_loader.cell_size)

    _turn_state = TurnState.PLAYER_INPUT



def restart_level():
    _reset_runtime_state()
    global _player, _maze_loader, _turn_state, _death_timer, _killer_ref
    if _maze_loader:
        _maze_loader.reset()
        p = _maze_loader.parsed["player"]
        _player = Player(p["x"], p["y"], _maze_loader.maze_size, _maze_loader.cell_size)

    _turn_state = TurnState.PLAYER_INPUT
    _death_timer = 0
    _killer_ref = None
    reset_input()


def undo_move():
    global _player, _maze_loader, _turn_state, _death_timer, _killer_ref
    if _maze_loader and _player:
        if _maze_loader.undo_last_move(_player):
            _turn_state = TurnState.PLAYER_INPUT
            _death_timer = 0
            _killer_ref = None
            _player.state = PlayerState.IDLE
            _player.frame_index = 0
            print("↺ Undo successful: State reset to PLAYER_INPUT")
        else:
            print("Cannot Undo: History stack empty")


def reset_input():
    if _button_manager:
        _button_manager.clear_clicked()

def _is_win():
    """Win nếu player đứng tại ô 'win cell' do MazeLoader tính (thống nhất với cách vẽ stairs)."""
    global _maze_loader, _player
    if not _maze_loader or not _player:
        return False

    win = _maze_loader.get_win_cell()  # (x,y) trong grid
    if not win:
        return False

    return (_player.x == win[0] and _player.y == win[1])



def draw_screen(screen, hovered=None, clicked=None, draw_mumlogo=True, mumlogo_y=None):
    global _torch_animation, _maze_loader, _player, _turn_state
    global _death_step, _death_step_timer, _fight_pause_timer, _killer_ref

    # ✅ Use cached images
    snake, mumlogo = _get_ui_images()

    # --- Update gameplay state ---
    if not _show_options and _player and _maze_loader:
        _player.update()
        _maze_loader.update()

        if _turn_state == TurnState.PLAYER_MOVING:
            if not _player.is_moving:
                _maze_loader.check_key_collision(_player.x, _player.y)
                # Trap is deadly: stepping onto a trap triggers immediate loss animation.
                if _maze_loader.check_trap_collision(_player.x, _player.y):
                    _maze_loader.pause_enemies()
                    _player.state = PlayerState.DIE_TRAP
                    _player.frame_index = 0
                    _turn_state = TurnState.PLAYER_DYING
                    _death_step = 3
                    _death_step_timer = 0
                    _killer_ref = None
                    return None
                if _is_win():
                    return "win"
                _turn_state = TurnState.ENEMY_TURN
                _maze_loader.init_enemy_turn_sequence()

        elif _turn_state == TurnState.ENEMY_TURN:
            for e in _maze_loader.enemies_list:
                e.prev_x = e.x
                e.prev_y = e.y
            _maze_loader.init_enemy_turn_sequence()
            _turn_state = TurnState.ENEMY_MOVING

        elif _turn_state == TurnState.ENEMY_MOVING:
            kill = False
            for e in _maze_loader.enemies_list:
                if e.x == _player.x and e.y == _player.y:
                    sfx_manager.play("pummel")
                    e.move_queue.clear()
                    _killer_ref = e
                    _maze_loader.spawn_fight_cloud(_player.x, _player.y)
                    _killer_ref.face_target(_player.x, _player.y)

                    _turn_state = TurnState.PLAYER_DYING
                    _death_step = 1
                    _death_step_timer = pygame.time.get_ticks()
                    kill = True
                    break

            if not kill:
                if _maze_loader.resolve_enemy_collisions():
                    _maze_loader.pause_enemies()
                    _turn_state = TurnState.FIGHT_PAUSE
                    _fight_pause_timer = pygame.time.get_ticks()
                else:
                    if _maze_loader.update_turn_sequence(_player.get_pos()):
                        _maze_loader.face_enemies_to_player(_player)
                        _turn_state = TurnState.PLAYER_INPUT
                        _player.last_input_time = pygame.time.get_ticks()
                        _maze_loader.check_solvability(_player)

        elif _turn_state == TurnState.FIGHT_PAUSE:
            if pygame.time.get_ticks() - _fight_pause_timer > 500:
                _maze_loader.process_pending_deaths()
                _maze_loader.resume_enemies()
                _turn_state = TurnState.ENEMY_MOVING

        elif _turn_state == TurnState.PLAYER_DYING:
            now = pygame.time.get_ticks()
            if _death_step == 1:
                if now - _death_step_timer > 550:
                    if _killer_ref and "scorpion" in _killer_ref.type:
                        _killer_ref.retreat_to(_killer_ref.prev_x, _killer_ref.prev_y)
                        _death_step = 2
                    else:
                        if _killer_ref and "mummy" in _killer_ref.type:
                            _player.state = (
                                PlayerState.DIE_RED_MUMMY
                                if _killer_ref.type == "red_mummy"
                                else PlayerState.DIE_WHITE_MUMMY
                            )
                            if _killer_ref in _maze_loader.enemies_list:
                                _maze_loader.enemies_list.remove(_killer_ref)
                        _player.frame_index = 0
                        _death_step = 3

            elif _death_step == 2:
                if _killer_ref and not _killer_ref.is_moving:
                    _player.state = PlayerState.DIE_STUNG
                    sfx_manager.play("poison")
                    _player.frame_index = 0
                    _death_step = 3
                    _death_step_timer = now

            elif _death_step == 3:
                anim = _player.animations.get(_player.state, [])
                if anim and _player.frame_index >= len(anim) - 1:
                    if _death_step_timer == 0:
                        _death_step_timer = now
                    if now - _death_step_timer > 1000:
                        return "lose"

        elif _turn_state == TurnState.PLAYER_INPUT:
            if "AFK" in _player.state.name:
                _maze_loader.trigger_enemy_afk()

    # --- Render ---
    if _maze_loader:
        _maze_loader.draw_background(screen)

    if _torch_animation and _torch_animation.loaded and _maze_loader:
        _torch_animation.update()
        ms = _maze_loader.maze_size
        if ms == 6:
            _torch_animation.draw(screen, 300, 40)
            _torch_animation.draw(screen, 475, 40)
        elif ms == 8:
            _torch_animation.draw(screen, 320, 40)
            _torch_animation.draw(screen, 455, 40)
        elif ms == 10:
            _torch_animation.draw(screen, 295, 40)
            _torch_animation.draw(screen, 475, 40)

    if _maze_loader:
        m = pygame.mouse.get_pos() if _turn_state == TurnState.PLAYER_INPUT else None
        _maze_loader.draw(screen, _player, None, m)

    # Left UI
    screen.blit(snake, (8, 80))
    if draw_mumlogo:
        screen.blit(mumlogo, (14, mumlogo_y if mumlogo_y else 14))

    if _world_map and _maze_loader:
        current_lvl = int(_maze_loader.level_id) if _maze_loader.level_id else 15
        _world_map.draw(screen, current_lvl)

    if _maze_loader:
        _maze_loader.draw_ankh(screen)

    if _button_manager:
        _button_manager.draw_buttons(screen, hovered, clicked)

    if _show_options:
        _draw_options_menu(screen)

    return None


def _draw_options_menu(screen):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    cx, cy = screen.get_width() // 2, screen.get_height() // 2
    rect = pygame.Rect(cx - 150, cy - 100, 300, 200)

    pygame.draw.rect(screen, (40, 30, 10), rect)
    pygame.draw.rect(screen, (150, 100, 50), rect, 3)

    font = pygame.font.SysFont("arial", 24, bold=True)
    small = pygame.font.SysFont("arial", 18)

    t = font.render("OPTIONS", True, (255, 200, 50))
    screen.blit(t, (cx - t.get_width() // 2, rect.y + 15))

    m_vol = int(music_manager.get_volume() * 100)
    s_vol = int(sfx_manager.get_volume() * 100)

    screen.blit(small.render(f"Music: {m_vol}%  [- / +]", True, (255, 255, 255)), (rect.x + 40, rect.y + 60))
    screen.blit(small.render(f"SFX: {s_vol}%  [- / +]", True, (255, 255, 255)), (rect.x + 40, rect.y + 100))

    c = small.render("Click OPTIONS to Close", True, (150, 150, 150))
    screen.blit(c, (cx - c.get_width() // 2, rect.bottom - 30))


def handle_game_input(event, mouse_pos):
    global _button_manager, _player, _maze_loader, _turn_state, _show_options
    
    # --- KEYBOARD SHORTCUTS ---
    if event.type == pygame.KEYDOWN:
        # ESC: toggle options
        if event.key == pygame.K_ESCAPE:
            _show_options = not _show_options
            return "option"

        # Khi đang mở options: M về menu
        if _show_options and event.key == pygame.K_m:
            _show_options = False
            return "menu"

        # Khi đang mở options: +/- chỉnh volume nhanh
        if event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            v = music_manager.get_volume() - 0.1
            music_manager.set_volume(max(0.0, min(1.0, v)))
            return None

        if event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
            v = music_manager.get_volume() + 0.1
            music_manager.set_volume(max(0.0, min(1.0, v)))
            return None

    # --------------------------

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        clicked_btn = None
        for name, rect in _button_manager.button_rects.items():
            if rect.collidepoint(mouse_pos):
                clicked_btn = name
                _button_manager.set_clicked(name)
                break

        if clicked_btn == "option":
            _show_options = not _show_options
            return "option"

        if not _show_options:
            if clicked_btn == "undo":
                if _turn_state == TurnState.PLAYER_INPUT:
                    undo_move()
                return "undo"

            if clicked_btn == "reset":
                restart_level()
                return "reset"

        if _show_options:
            cx, cy = 640 // 2, 480 // 2
            bx, by = cx - 150, cy - 100
            if bx < mouse_pos[0] < bx + 300:
                if by + 50 < mouse_pos[1] < by + 80:
                    dv = 0.1 if mouse_pos[0] > cx else -0.1
                    music_manager.set_volume(max(0.0, min(1.0, music_manager.get_volume() + dv)))
                elif by + 90 < mouse_pos[1] < by + 120:
                    dv = 0.1 if mouse_pos[0] > cx else -0.1
                    sfx_manager.set_volume(max(0.0, min(1.0, sfx_manager.get_volume() + dv)))
            return None

    if _show_options:
        return None
    if _turn_state != TurnState.PLAYER_INPUT:
        return None

    if _player and _maze_loader:
        move = _player.handle_input()
        if move:
            dx, dy = move
            _execute_player_move(dx, dy)

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if _player and _maze_loader:
            mx, my = mouse_pos
            gx = (mx - maze_coord_x) // _maze_loader.cell_size
            gy = (my - maze_coord_y) // _maze_loader.cell_size
            if 0 <= gx < _maze_loader.maze_size and 0 <= gy < _maze_loader.maze_size:
                dx = gx - _player.x
                dy = gy - _player.y
                if dx == 0 and dy == 0:
                    _execute_player_move(0, 0)
                elif abs(dx) + abs(dy) == 1:
                    _execute_player_move(dx, dy)

    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        _button_manager.clear_clicked()

    return None


def _execute_player_move(dx, dy):
    global _player, _maze_loader, _turn_state
    if not _player.is_ready():
        return

    tx = _player.x + dx
    ty = _player.y + dy

    for e in _maze_loader.enemies_list:
        if e.x == tx and e.y == ty:
            return

    if _player.check_eligible_move(tx, ty, _maze_loader.maze_size, _maze_loader.parsed["walls"], _maze_loader.gate_obj):
        _maze_loader.save_state(_player)
        _player.move_player(dx, dy)
        _turn_state = TurnState.PLAYER_MOVING


def get_hover_state(mouse_pos):
    if not _button_manager:
        return None
    for name, rect in _button_manager.button_rects.items():
        if rect.collidepoint(mouse_pos):
            return name
    return None


def get_clicked_state():
    return _button_manager.clicked_button if _button_manager else None
