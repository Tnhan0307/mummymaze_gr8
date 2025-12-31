import pygame
import os

from api.io.Lightning.manager.TextDesigner import TextDesigner
from api.io.Lightning.utils.ConfigFile import UI_PATH, fps


def lose_screen(screen, clock, background_surf=None):
    """
    Displays the Lose Screen.
    If background_surf is provided, it is drawn as the static background (overlay effect).
    """

    # 1. Load Background Assets
    if background_surf:
        menuback = background_surf
    else:
        menuback = pygame.image.load(os.path.join(UI_PATH, 'menuback.jpg'))

    menufront = pygame.image.load(os.path.join(UI_PATH, 'menufront.png'))

    # 2. Setup Text Designer
    designer = TextDesigner(color=(0, 0, 0), hover_color=(245, 0, 0))

    # 3. Create Button Surfaces
    btn_try = designer.render('TRY AGAIN', outline=False, hovered=False)
    btn_try_h = designer.render('TRY AGAIN', outline_thickness=1, hovered=True)

    btn_abandon = designer.render('ABANDON HOPE', outline=False, hovered=False)
    btn_abandon_h = designer.render('ABANDON HOPE', outline_thickness=1, hovered=True)

    btn_undo = designer.render('UNDO MOVE', outline=False, hovered=False)
    btn_undo_h = designer.render('UNDO MOVE', outline_thickness=1, hovered=True)

    btn_save = designer.render('SAVE AND QUIT', outline=False, hovered=False)
    btn_save_h = designer.render('SAVE AND QUIT', outline_thickness=1, hovered=True)

    # 4. Define Layout Positions
    col1_x = 110
    col2_x = 360
    row1_y = 360
    row2_y = 410

    rect_try = btn_try.get_rect(topleft=(col1_x, row1_y))
    rect_abandon = btn_abandon.get_rect(topleft=(col2_x, row1_y))
    rect_undo = btn_undo.get_rect(topleft=(col1_x, row2_y))
    rect_save = btn_save.get_rect(topleft=(col2_x, row2_y))

    # 5. Animation Variables
    menu_target_y = 0
    menu_start_y = 480

    animation_progress = 0.0
    animation_speed = 0.02
    animation_complete = False

    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if animation_complete and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if rect_try.collidepoint(mouse_pos):
                    return "retry"
                elif rect_abandon.collidepoint(mouse_pos):
                    return "main_menu"
                elif rect_undo.collidepoint(mouse_pos):
                    return "undo"
                elif rect_save.collidepoint(mouse_pos):
                    return "save_quit"

        # --- Update Animation ---
        current_menu_y = menu_target_y

        if animation_progress < 1.0:
            animation_progress += animation_speed
            if animation_progress > 1.0:
                animation_progress = 1.0
                animation_complete = True

            eased_progress = 1 - (1 - animation_progress) ** 2
            current_menu_y = menu_start_y + (menu_target_y - menu_start_y) * eased_progress

        # --- Drawing ---
        screen.blit(menuback, (0, 0))
        screen.blit(menufront, (0, current_menu_y))

        # Draw Buttons
        y_offset = current_menu_y - menu_target_y
        mouse_pos = pygame.mouse.get_pos()

        # Try Again
        if animation_complete and rect_try.collidepoint(mouse_pos):
            screen.blit(btn_try_h, (col1_x, row1_y + y_offset))
        else:
            screen.blit(btn_try, (col1_x, row1_y + y_offset))

        # Abandon Hope
        if animation_complete and rect_abandon.collidepoint(mouse_pos):
            screen.blit(btn_abandon_h, (col2_x, row1_y + y_offset))
        else:
            screen.blit(btn_abandon, (col2_x, row1_y + y_offset))

        # Undo Move
        if animation_complete and rect_undo.collidepoint(mouse_pos):
            screen.blit(btn_undo_h, (col1_x, row2_y + y_offset))
        else:
            screen.blit(btn_undo, (col1_x, row2_y + y_offset))

        # Save and Quit
        if animation_complete and rect_save.collidepoint(mouse_pos):
            screen.blit(btn_save_h, (col2_x, row2_y + y_offset))
        else:
            screen.blit(btn_save, (col2_x, row2_y + y_offset))

        # Cursor Logic
        if animation_complete:
            is_hovering = (rect_try.collidepoint(mouse_pos) or
                           rect_abandon.collidepoint(mouse_pos) or
                           rect_undo.collidepoint(mouse_pos) or
                           rect_save.collidepoint(mouse_pos))

            if is_hovering:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        pygame.display.flip()
        clock.tick(fps)

    return "quit"