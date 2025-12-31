import pygame
import os

from api.io.Lightning.gui import GameUI
from api.io.Lightning.gui.LoseState import lose_screen
from api.io.Lightning.manager.TextDesigner import TextDesigner
from api.io.Lightning.utils.ConfigFile import UI_PATH, SOUNDS_PATH, fps
from api.io.Lightning.manager.SoundReader import music_manager


def init():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Mummy Maze Ultimate 1.0")
    icon = pygame.image.load(os.path.join(UI_PATH, 'game.ico'))
    pygame.display.set_icon(icon)
    GameUI.initialize_ui()
    return screen


def loading_screen(screen, clock):
    music_manager.initialize()
    title = pygame.image.load(os.path.join(UI_PATH, 'title.jpg'))
    progress_bar = pygame.image.load(os.path.join(UI_PATH, 'titlebar.jpg')).convert_alpha()
    color = TextDesigner(color=(255, 125, 17), hover_color=(255, 255, 255))
    play = color.render('CLICK HERE TO PLAY', outline_thickness=1, hovered=False)
    play_hovered = color.render('CLICK HERE TO PLAY', outline_thickness=1, hovered=True)
    play_rect = play.get_rect(topleft=(190, 430))

    progress = 0
    speed = 0.2
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            music_manager.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and progress >= 100:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                mouse_pos = pygame.mouse.get_pos()
                if play_rect.collidepoint(mouse_pos):
                    return "main_menu"

        screen.blit(title, (0, 0))
        fill_px = int((progress / 100) * 340)
        bar_crop = progress_bar.subsurface((0, 0, fill_px, 24))
        screen.blit(bar_crop, (147, 392))
        if progress < 100:
            progress += speed
            if progress > 100: progress = 100
        else:
            mouse_pos = pygame.mouse.get_pos()
            if play_rect.collidepoint(mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                screen.blit(play_hovered, (190, 430))
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                screen.blit(play, (190, 430))
        pygame.display.flip()
        clock.tick(fps)
    return None


def main_menu(screen, clock):
    menuback = pygame.image.load(os.path.join(UI_PATH, 'menuback.jpg'))
    menufront = pygame.image.load(os.path.join(UI_PATH, 'menufront.png'))
    logo = pygame.image.load(os.path.join(UI_PATH, 'menulogo.png'))
    color = TextDesigner(color=(0, 0, 0), hover_color=(245, 0, 0))
    tombslide_sound = pygame.mixer.Sound(os.path.join(SOUNDS_PATH, 'tombslide.wav'))
    tombslide_sound.play()

    classic = color.render('CLASSIC MODE', outline=False, hovered=False)
    classic_hovered = color.render('CLASSIC MODE', outline_thickness=1, hovered=True)
    classic_rect = classic.get_rect(topleft=(100, 360))
    tutorial = color.render('TUTORIAL', outline=False, hovered=False)
    tutorial_hovered = color.render('TUTORIAL', outline_thickness=1, hovered=True)
    tutorial_rect = tutorial.get_rect(topleft=(390, 360))

    logo_x = 92.5
    logo_target_y = 10
    logo_start_y = -logo.get_height()
    menu_target_y = 0
    menu_start_y = 480
    animation_progress = 0.0
    animation_speed = 0.02
    animation_complete = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            music_manager.handle_event(event)
            if animation_complete and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if classic_rect.collidepoint(mouse_pos):
                    return "classic_mode"
                elif tutorial_rect.collidepoint(mouse_pos):
                    return "tutorial"

        screen.blit(menuback, (0, 0))
        if animation_progress < 1.0:
            animation_progress += animation_speed
            if animation_progress > 1.0:
                animation_progress = 1.0
                animation_complete = True
            eased_progress = 1 - (1 - animation_progress) ** 2
            current_logo_y = logo_start_y + (logo_target_y - logo_start_y) * eased_progress
            current_menu_y = menu_start_y + (menu_target_y - menu_start_y) * eased_progress
            screen.blit(menufront, (0, current_menu_y))
            button_y = 360 + (current_menu_y - menu_target_y)
            screen.blit(classic, (100, button_y))
            screen.blit(tutorial, (390, button_y))
            screen.blit(logo, (logo_x, current_logo_y))
        else:
            screen.blit(menufront, (0, menu_target_y))
            mouse_pos = pygame.mouse.get_pos()
            hovered = 'classic' if classic_rect.collidepoint(mouse_pos) else 'tutorial' if tutorial_rect.collidepoint(
                mouse_pos) else None

            if hovered == 'classic':
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                screen.blit(classic_hovered, (100, 360))
                screen.blit(tutorial, (390, 360))
            elif hovered == 'tutorial':
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                screen.blit(classic, (100, 360))
                screen.blit(tutorial_hovered, (390, 360))
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                screen.blit(classic, (100, 360))
                screen.blit(tutorial, (390, 360))
            screen.blit(logo, (logo_x, logo_target_y))
        pygame.display.flip()
        clock.tick(fps)
    return None


def classic_mode(screen, clock):
    GameUI.reset_input()
    music_manager.start_hard_mode_music()
    tombslide_sound = pygame.mixer.Sound(os.path.join(SOUNDS_PATH, 'tombslide.wav'))
    tombslide_sound.play()
    mumlogo = pygame.image.load(os.path.join(UI_PATH, 'mumlogo.png')).convert_alpha()

    mumlogo_target_y = 14
    mumlogo_start_y = -mumlogo.get_height()
    mumlogo_x = 14
    animation_progress = 0.0
    animation_speed = 0.02
    animation_complete = False

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            music_manager.handle_event(event)
            if animation_complete:
                action = GameUI.handle_game_input(event, mouse_pos)
                if action == 'quit': return "main_menu"

        hovered = GameUI.get_hover_state(mouse_pos) if animation_complete else None
        clicked = GameUI.get_clicked_state() if animation_complete else None

        if animation_complete:
            if hovered:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if animation_progress < 1.0:
            animation_progress += animation_speed
            if animation_progress > 1.0:
                animation_progress = 1.0
                animation_complete = True
            eased_progress = 1 - (1 - animation_progress) ** 2
            current_mumlogo_y = mumlogo_start_y + (mumlogo_target_y - mumlogo_start_y) * eased_progress
            GameUI.draw_screen(screen, hovered, clicked, draw_mumlogo=False, mumlogo_y=current_mumlogo_y)
            screen.blit(mumlogo, (mumlogo_x, current_mumlogo_y))
        else:
            status = GameUI.draw_screen(screen, hovered, clicked)
            if status == "lose":
                # Snapshot GameUI for the overlay background
                game_snapshot = screen.copy()
                return "lose_screen", game_snapshot

        pygame.display.flip()
        clock.tick(fps)
    return None


if __name__ == '__main__':
    screen = init()
    clock = pygame.time.Clock()
    current_screen = "classic_mode"
    background_capture = None

    while current_screen:
        if current_screen == "loading":
            current_screen = loading_screen(screen, clock)
        elif current_screen == "main_menu":
            current_screen = main_menu(screen, clock)
        elif current_screen == "classic_mode":
            result = classic_mode(screen, clock)

            if isinstance(result, tuple):
                status, data = result
                if status == "lose_screen":
                    background_capture = data
                    current_screen = "lose_screen"
            elif result == "main_menu":
                current_screen = "main_menu"
                music_manager.start_menu_music()
            else:
                current_screen = None

        elif current_screen == "lose_screen":
            current_screen = lose_screen(screen, clock, background_surf=background_capture)
            if current_screen == "retry":
                # CALL THE RESTART FUNCTION HERE
                GameUI.restart_level()
                current_screen = "classic_mode"
            elif current_screen == "save_quit":
                GameUI.restart_level()
                current_screen = "main_menu"
                music_manager.start_menu_music()
            elif current_screen == "undo":
                # FIX: Actually call the undo function!
                GameUI.undo_move()
                current_screen = "classic_mode"

        elif current_screen == "tutorial":
            current_screen = None
            if current_screen == "main_menu":
                music_manager.start_menu_music()
        else:
            break

    pygame.quit()