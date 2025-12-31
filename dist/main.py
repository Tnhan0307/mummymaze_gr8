import os
import sys
import pygame
import json
from pathlib import Path
import MummyMaze.api.io.Lightning.utils.ConfigFile as cf
# dùng: cf.UI_PATH, cf.PROJECT_PATH, cf.LEVELS_PATH...

# === Thêm project root (MummyMaze) vào sys.path để import được 'api' ===
ROOT_DIR = Path(__file__).resolve().parent.parent  # .../MummyMaze
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from MummyMaze.api.io.Lightning.gui.GameUI import (
    initialize_ui,
    draw_screen,
    handle_game_input,
    get_hover_state,
    get_clicked_state,
)

STATE_MENU = "MENU"
STATE_RANDOM_CFG   = "RANDOM_CFG"
STATE_CAMPAIGN_SEL = "CAMPAIGN_SEL"
STATE_GAME = "GAME"
STATE_WIN  = "WIN"
STATE_LOSE = "LOSE"

ctx = {
    "mode": "random",     # "random" | "campaign"
    "level_id": 1,        # cho campaign (placeholder)
    "size": 8,            # cho random size (placeholder)
    "difficulty": "medium"
}

def _scan_campaign_levels():
    """Trả về list level_id có file level_X.json trong cf.LEVELS_PATH"""
    ids = []
    try:
        for name in os.listdir(cf.LEVELS_PATH):
            if name.startswith("level_") and name.endswith(".json"):
                mid = name[len("level_"):-len(".json")]
                if mid.isdigit():
                    ids.append(int(mid))
    except Exception:
        return [1]
    ids.sort()
    return ids if ids else [1]

def _level_exists(level_id: int) -> bool:
    return os.path.exists(os.path.join(cf.LEVELS_PATH, f"level_{level_id}.json"))

def _draw_text(screen, text, x, y, font, color=(255,255,255)):
    surf = font.render(text, True, color)
    rect = surf.get_rect(topleft=(x, y))
    screen.blit(surf, rect)
    return rect

def _button(screen, rect: pygame.Rect, label: str, font, mouse_pos, clicked):
    # hover effect nhẹ
    hovered = rect.collidepoint(mouse_pos)
    border = (220, 220, 220) if hovered else (140, 140, 140)
    fill   = (60, 60, 60) if hovered else (40, 40, 40)

    pygame.draw.rect(screen, fill, rect, border_radius=10)
    pygame.draw.rect(screen, border, rect, width=2, border_radius=10)

    # center text
    text_surf = font.render(label, True, (255,255,255))
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

    return hovered and clicked

def build_game_session(ctx):
    # truyền lựa chọn từ menu vào gameplay
    initialize_ui(
        mode=ctx["mode"],
        level_id=ctx["level_id"],
        size=ctx["size"],
        difficulty=ctx["difficulty"],
    )

def random_config_screen(screen, font, mouse_pos, clicked):
    screen.fill((15, 15, 20))
    _draw_text(screen, "RANDOM - CONFIG", 40, 30, font)

    # Size buttons
    _draw_text(screen, "Choose size:", 40, 90, font)
    btn_6  = pygame.Rect(40, 130, 120, 50)
    btn_8  = pygame.Rect(170, 130, 120, 50)
    btn_10 = pygame.Rect(300, 130, 120, 50)

    # Difficulty buttons
    _draw_text(screen, "Difficulty:", 40, 200, font)
    btn_e = pygame.Rect(40, 240, 120, 50)
    btn_m = pygame.Rect(170, 240, 120, 50)
    btn_h = pygame.Rect(300, 240, 120, 50)

    # Start / Back
    btn_start = pygame.Rect(40, 330, 260, 55)
    btn_back  = pygame.Rect(320, 330, 160, 55)

    # --- size select ---
    if _button(screen, btn_6,  "6x6",  font, mouse_pos, clicked):
        ctx["size"] = 6
    if _button(screen, btn_8,  "8x8",  font, mouse_pos, clicked):
        ctx["size"] = 8
    if _button(screen, btn_10, "10x10", font, mouse_pos, clicked):
        ctx["size"] = 10

    # --- diff select ---
    if _button(screen, btn_e, "easy", font, mouse_pos, clicked):
        ctx["difficulty"] = "easy"
    if _button(screen, btn_m, "medium", font, mouse_pos, clicked):
        ctx["difficulty"] = "medium"
    if _button(screen, btn_h, "hard", font, mouse_pos, clicked):
        ctx["difficulty"] = "hard"

    # show current selection
    _draw_text(screen, f"Selected: size={ctx['size']}  diff={ctx['difficulty']}", 40, 410, font)

    if _button(screen, btn_start, "START", font, mouse_pos, clicked):
        ctx["mode"] = "random"
        build_game_session(ctx)
        return STATE_GAME

    if _button(screen, btn_back, "BACK", font, mouse_pos, clicked):
        return STATE_MENU

    return STATE_RANDOM_CFG

def campaign_select_screen(screen, font, mouse_pos, clicked):
    screen.fill((15, 15, 20))
    _draw_text(screen, "CAMPAIGN - SELECT LEVEL", 40, 30, font)

    levels = _scan_campaign_levels()
    _draw_text(screen, "Choose level:", 40, 90, font)

    # Vẽ tối đa 6 level buttons (đủ cho demo)
    start_x, start_y = 40, 130
    bw, bh, gap = 120, 50, 15

    chosen = ctx.get("level_id", levels[0])

    for i, lid in enumerate(levels[:6]):
        r = pygame.Rect(start_x + (i % 3) * (bw + gap), start_y + (i // 3) * (bh + gap), bw, bh)
        label = f"Lv {lid}"
        if lid == chosen:
            label = f"> {label} <"
        if _button(screen, r, label, font, mouse_pos, clicked):
            ctx["level_id"] = lid

    _draw_text(screen, "Difficulty:", 40, 260, font)
    btn_e = pygame.Rect(40, 300, 120, 50)
    btn_m = pygame.Rect(170, 300, 120, 50)
    btn_h = pygame.Rect(300, 300, 120, 50)

    if _button(screen, btn_e, "easy", font, mouse_pos, clicked):
        ctx["difficulty"] = "easy"
    if _button(screen, btn_m, "medium", font, mouse_pos, clicked):
        ctx["difficulty"] = "medium"
    if _button(screen, btn_h, "hard", font, mouse_pos, clicked):
        ctx["difficulty"] = "hard"

    btn_start = pygame.Rect(40, 380, 260, 55)
    btn_back  = pygame.Rect(320, 380, 160, 55)

    _draw_text(screen, f"Selected: level={ctx['level_id']}  diff={ctx['difficulty']}", 40, 440, font)

    if _button(screen, btn_start, "START", font, mouse_pos, clicked):
        ctx["mode"] = "campaign"
        build_game_session(ctx)
        return STATE_GAME

    if _button(screen, btn_back, "BACK", font, mouse_pos, clicked):
        return STATE_MENU

    return STATE_CAMPAIGN_SEL


def menu_screen(screen, font, mouse_pos, clicked):
    screen.fill((15, 15, 20))
    _draw_text(screen, "MUMMY MAZE - MENU", 40, 30, font)

    btn_random = pygame.Rect(40, 120, 260, 55)
    btn_campaign = pygame.Rect(40, 190, 260, 55)
    btn_quit = pygame.Rect(40, 260, 260, 55)

    if _button(screen, btn_random, "Play Random", font, mouse_pos, clicked):
        ctx["mode"] = "random"
        return STATE_RANDOM_CFG


    if _button(screen, btn_campaign, "Campaign", font, mouse_pos, clicked):
        ctx["mode"] = "campaign"
        return STATE_CAMPAIGN_SEL

    if _button(screen, btn_quit, "Quit", font, mouse_pos, clicked):
        return "__QUIT__"

    return STATE_MENU


def lose_screen(screen, font, mouse_pos, clicked):
    screen.fill((25, 10, 10))
    _draw_text(screen, "YOU LOSE!", 40, 30, font)

    btn_retry = pygame.Rect(40, 120, 260, 55)
    btn_menu  = pygame.Rect(40, 190, 260, 55)
    btn_quit  = pygame.Rect(40, 260, 260, 55)

    if _button(screen, btn_retry, "Retry", font, mouse_pos, clicked):
        build_game_session(ctx)
        return STATE_GAME

    if _button(screen, btn_menu, "Back to Menu", font, mouse_pos, clicked):
        return STATE_MENU

    if _button(screen, btn_quit, "Quit", font, mouse_pos, clicked):
        return "__QUIT__"

    return STATE_LOSE


def win_screen(screen, font, mouse_pos, clicked):
    screen.fill((10, 25, 10))
    _draw_text(screen, "YOU WIN!", 40, 30, font)

    btn_primary = pygame.Rect(40, 120, 260, 55)
    btn_menu    = pygame.Rect(40, 190, 260, 55)
    btn_quit    = pygame.Rect(40, 260, 260, 55)

    if ctx.get("mode") == "campaign":
        primary_label = "Next Level"
        if _button(screen, btn_primary, primary_label, font, mouse_pos, clicked):
            nxt = ctx.get("level_id", 1) + 1
            if _level_exists(nxt):
                ctx["level_id"] = nxt
                build_game_session(ctx)
                return STATE_GAME
            else:
                # hết level -> về menu
                return STATE_MENU
    else:
        primary_label = "Play Again"
        if _button(screen, btn_primary, primary_label, font, mouse_pos, clicked):
            build_game_session(ctx)
            return STATE_GAME

    if _button(screen, btn_menu, "Back to Menu", font, mouse_pos, clicked):
        return STATE_MENU

    if _button(screen, btn_quit, "Quit", font, mouse_pos, clicked):
        return "__QUIT__"

    return STATE_WIN

def main():
    pygame.init()

    # QUAN TRỌNG: set_mode trước rồi mới initialize_ui()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()

    pygame.display.set_caption("Mummy Maze Ultimate 1.0")
    icon = pygame.image.load(os.path.join(cf.UI_PATH, "game.ico"))
    pygame.display.set_icon(icon)

    font = pygame.font.SysFont(None, 36)
    state = STATE_MENU

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        # click "1 lần trong frame" để bấm nút menu/win/lose cho dễ
        clicked_frame = False

        # --- Event loop ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked_frame = True

            # Chỉ gửi input vào gameplay khi đang ở GAME
            if state == STATE_GAME:
                result = handle_game_input(event, mouse_pos)
                if result == "lose":
                    state = STATE_LOSE
                elif result == "win":
                    state = STATE_WIN
                elif result == "menu":
                    state = STATE_MENU

        if not running:
            break

        # --- Render theo state ---
        if state == STATE_MENU:
            nxt = menu_screen(screen, font, mouse_pos, clicked_frame)
            if nxt == "__QUIT__":
                running = False
            else:
                state = nxt
                
        elif state == STATE_RANDOM_CFG:
            nxt = random_config_screen(screen, font, mouse_pos, clicked_frame)
            state = nxt

        elif state == STATE_CAMPAIGN_SEL:
            nxt = campaign_select_screen(screen, font, mouse_pos, clicked_frame)
            state = nxt

        elif state == STATE_GAME:
            hovered = get_hover_state(mouse_pos)
            clicked = get_clicked_state()
            result = draw_screen(screen, hovered, clicked)

            if result == "lose":
                state = STATE_LOSE
            elif result == "win":
                state = STATE_WIN

        elif state == STATE_LOSE:
            nxt = lose_screen(screen, font, mouse_pos, clicked_frame)
            if nxt == "__QUIT__":
                running = False
            else:
                state = nxt

        elif state == STATE_WIN:
            nxt = win_screen(screen, font, mouse_pos, clicked_frame)
            if nxt == "__QUIT__":
                running = False
            else:
                state = nxt

        pygame.display.flip()
        clock.tick(cf.fps)

    pygame.quit()
    
if __name__ == "__main__":
    main()
