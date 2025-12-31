import pygame

from api.io.Lightning.utils.ConfigFile import *


class TextDesigner:
    def __init__(self, color=(0, 255, 255), hover_color=(255, 255, 0)):
        self.color = color
        self.hover_color = hover_color

        # Load the original white bitmap (biggestfont)
        self.original_image = pygame.image.load(os.path.join(UI_PATH, 'biggestfont.gif')).convert_alpha()
        self.original_image.set_colorkey((0, 0, 0))

        # Create colored version
        self.image = self.original_image.copy()
        self.image.fill(color, special_flags=pygame.BLEND_MULT)

        # Create hover colored version
        self.hover_image = self.original_image.copy()
        self.hover_image.fill(hover_color, special_flags=pygame.BLEND_MULT)

        self.letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        height = self.image.get_height()

        widths = {
            "A": 16, "B": 14, "C": 11, "D": 15, "E": 12, "F": 11, "G": 15, "H": 15,
            "I": 6, "J": 7, "K": 14, "L": 10, "M": 19, "N": 16, "O": 16, "P": 15,
            "Q": 17, "R": 15, "S": 13, "T": 12, "U": 16, "V": 15, "W": 23, "X": 15,
            "Y": 16, "Z": 12
        }
        spacings = [4, 4, 3, 4, 4, 3, 3, 3, 3, 4, 4, 4, 3, 3, 4, 3, 4, 4, 4, 4, 4, 4, 4, 3, 4]

        # Create colored glyphs
        self.glyphs = {}
        x = 0
        for i, ch in enumerate(self.letters):
            w = widths[ch]
            rect = pygame.Rect(x, 0, w, height)
            self.glyphs[ch] = self.image.subsurface(rect).copy()

            if i < len(spacings):
                x += w + spacings[i]
            else:
                x += w

        # Create hover colored glyphs
        self.hover_glyphs = {}
        x = 0
        for i, ch in enumerate(self.letters):
            w = widths[ch]
            rect = pygame.Rect(x, 0, w, height)
            self.hover_glyphs[ch] = self.hover_image.subsurface(rect).copy()

            if i < len(spacings):
                x += w + spacings[i]
            else:
                x += w

        # Create original white glyphs (keep for compatibility)
        self.white_glyphs = {}
        x = 0
        for i, ch in enumerate(self.letters):
            w = widths[ch]
            rect = pygame.Rect(x, 0, w, height)
            self.white_glyphs[ch] = self.original_image.subsurface(rect).copy()

            if i < len(spacings):
                x += w + spacings[i]
            else:
                x += w

        # Support lowercase
        for ch in self.letters:
            self.glyphs[ch.lower()] = self.glyphs[ch]
            self.hover_glyphs[ch.lower()] = self.hover_glyphs[ch]
            self.white_glyphs[ch.lower()] = self.white_glyphs[ch]

        # Initialize PyramidFont glyphs
        self._init_pyramid_font()

        # Initialize DefaultFont glyphs
        self._init_default_font()

    def _init_pyramid_font(self):
        """Initialize PyramidFont (0-9) from pyramidfont.png"""
        self.pyramid_image = pygame.image.load(os.path.join(UI_PATH, 'pyramidfont.png')).convert_alpha()
        self.pyramid_image.set_colorkey((0, 0, 0))

        pyramid_chars = "0123456789"
        height = self.pyramid_image.get_height()

        # Font bitmap is 70x12 with 1px spacing between digits
        pyramid_widths = {
            "0": 6, "1": 5, "2": 6, "3": 6, "4": 6,
            "5": 6, "6": 6, "7": 6, "8": 6, "9": 6
        }

        self.pyramid_glyphs = {}
        x = 0
        source_spacing = 1  # 1 pixel spacing between digits

        for ch in pyramid_chars:
            w = pyramid_widths.get(ch, 6)
            if x + w <= self.pyramid_image.get_width():
                rect = pygame.Rect(x, 0, w, height)
                self.pyramid_glyphs[ch] = self.pyramid_image.subsurface(rect).copy()
            x += w + source_spacing

    def _init_default_font(self):
        """Initialize DefaultFont (A-Z, a-z, 0-9, symbols) from font1.png"""
        self.default_image = pygame.image.load(os.path.join(UI_PATH, 'font1.png')).convert_alpha()
        self.default_image.set_colorkey((0, 0, 0))

        self.default_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789`!@#$%&*()+=\\/'\":?-.,"
        height = self.default_image.get_height()

        default_width = 6
        default_widths = {
            # Uppercase
            "I": 4, "M": 8, "W": 8, "L": 5,
            # Lowercase
            "i": 3, "l": 3, "j": 4, "t": 4, "f": 4, "m": 8, "w": 8,
            # Numbers
            "1": 4,
            # Symbols
            "`": 3, "!": 3, "(": 4, ")": 4, ".": 3, ",": 3,
            ":": 3, "'": 3, "\"": 5, "-": 5
        }

        self.default_glyphs = {}
        x = 0
        source_padding = 1

        for ch in self.default_chars:
            w = default_widths.get(ch, default_width)

            if x + w <= self.default_image.get_width():
                rect = pygame.Rect(x, 0, w, height)
                self.default_glyphs[ch] = self.default_image.subsurface(rect).copy()

            x += w + source_padding

    def render(self, text, letter_spacing=2, word_spacing=12, outline=True, outline_thickness=2, hovered=False):
        """Render text using the big font with optional outline and hover effect"""
        text = text.upper()
        height = self.image.get_height()

        # Choose glyphs based on hover state
        glyphs = self.hover_glyphs if hovered else self.glyphs

        # Calculate final surface width
        width = 0
        for ch in text:
            if ch == " ":
                width += word_spacing
            elif ch in glyphs:
                width += glyphs[ch].get_width() + letter_spacing

        width -= letter_spacing

        # Create base surface for the colored text
        base_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        x = 0

        for ch in text:
            if ch == " ":
                x += word_spacing
            elif ch in glyphs:
                glyph = glyphs[ch]
                base_surf.blit(glyph, (x, 0))
                x += glyph.get_width() + letter_spacing

        if not outline:
            return base_surf

        # Create outlined version
        padded_width = width + outline_thickness * 2
        padded_height = height + outline_thickness * 2
        final_surf = pygame.Surface((padded_width, padded_height), pygame.SRCALPHA)

        # Create black version of the text
        black_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        for x in range(width):
            for y in range(height):
                pixel = base_surf.get_at((x, y))
                if pixel.a > 0:
                    black_surf.set_at((x, y), (0, 0, 0, pixel.a))

        # Draw the black outline
        offsets = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)
        ]

        for dx, dy in offsets:
            for layer in range(outline_thickness):
                final_surf.blit(black_surf,
                                (outline_thickness + dx * (layer + 1), outline_thickness + dy * (layer + 1)))

        # Draw the colored text on top
        final_surf.blit(base_surf, (outline_thickness, outline_thickness))

        return final_surf

    def render_pyramid(self, text, letter_spacing=1):
        """Render numbers using PyramidFont (no outline, no hover)"""
        text = str(text)
        height = self.pyramid_image.get_height()

        width = 0
        for ch in text:
            if ch in self.pyramid_glyphs:
                width += self.pyramid_glyphs[ch].get_width() + letter_spacing
        width -= letter_spacing
        if width < 0:
            width = 0

        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        x = 0
        for ch in text:
            if ch in self.pyramid_glyphs:
                glyph = self.pyramid_glyphs[ch]
                surf.blit(glyph, (x, 0))
                x += glyph.get_width() + letter_spacing
        return surf

    def render_default(self, text, letter_spacing=1, word_spacing=4):
        """Render text using DefaultFont (no outline, no hover)"""
        height = self.default_image.get_height()

        width = 0
        for ch in text:
            if ch == " ":
                width += word_spacing
            elif ch in self.default_glyphs:
                width += self.default_glyphs[ch].get_width() + letter_spacing
        width -= letter_spacing
        if width < 0:
            width = 0

        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        x = 0
        for ch in text:
            if ch == " ":
                x += word_spacing
            elif ch in self.default_glyphs:
                glyph = self.default_glyphs[ch]
                surf.blit(glyph, (x, 0))
                x += glyph.get_width() + letter_spacing

        return surf


class PyramidFont:
    """
    Handles the number-only font from pyramidfont.png (0-9)
    """

    def __init__(self):
        self.image = pygame.image.load(os.path.join(UI_PATH, 'pyramidfont.png')).convert_alpha()
        self.image.set_colorkey((0, 0, 0))

        self.chars = "0123456789"
        height = self.image.get_height()

        # Font bitmap is 70x12 with 1px spacing between digits
        widths = {
            "0": 6, "1": 5, "2": 6, "3": 6, "4": 6,
            "5": 6, "6": 6, "7": 6, "8": 6, "9": 6
        }

        # Spacing between numbers in the source image strip
        self.source_spacing = 1

        self.glyphs = {}
        x = 0
        for ch in self.chars:
            w = widths.get(ch, 6)
            if x + w <= self.image.get_width():
                rect = pygame.Rect(x, 0, w, height)
                self.glyphs[ch] = self.image.subsurface(rect).copy()
            x += w + self.source_spacing

    def render(self, text, letter_spacing=1):
        text = str(text)  # Ensure input is string
        height = self.image.get_height()

        width = 0
        for ch in text:
            if ch in self.glyphs: width += self.glyphs[ch].get_width() + letter_spacing
        width -= letter_spacing
        if width < 0: width = 0

        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        x = 0
        for ch in text:
            if ch in self.glyphs:
                glyph = self.glyphs[ch]
                surf.blit(glyph, (x, 0))
                x += glyph.get_width() + letter_spacing
        return surf


class DefaultFont:
    r"""
    Handles the small white font from font1.png
    Supports: A-Z, a-z, 0-9, and symbols `!@#$%&*()+=\/'":?-.,
    """

    def __init__(self):
        self.image = pygame.image.load(os.path.join(UI_PATH, 'font1.png')).convert_alpha()
        self.image.set_colorkey((0, 0, 0))

        # The Exact order provided
        # Note: double quotes " and backslashes \ are escaped
        self.chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789`!@#$%&*()+=\\/'\":?-.,"

        height = self.image.get_height()

        # SETUP WIDTHS
        # Most chars in small pixel fonts are ~6px.
        # Adjust these specific values if your font1.png alignment is slightly off.
        self.default_width = 6

        widths = {
            # Uppercase
            "I": 4, "M": 8, "W": 8, "L": 5,
            # Lowercase
            "i": 3, "l": 3, "j": 4, "t": 4, "f": 4, "m": 8, "w": 8,
            # Numbers
            "1": 4,
            # Symbols
            "`": 3, "!": 3, "(": 4, ")": 4, ".": 3, ",": 3,
            ":": 3, "'": 3, "\"": 5, "-": 5
        }

        self.glyphs = {}
        x = 0
        source_padding = 1  # Gap between letters in the .png file

        for ch in self.chars:
            w = widths.get(ch, self.default_width)

            # Safety check: don't slice past image end
            if x + w <= self.image.get_width():
                rect = pygame.Rect(x, 0, w, height)
                self.glyphs[ch] = self.image.subsurface(rect).copy()

            x += w + source_padding

    def render(self, text, letter_spacing=1, word_spacing=4):
        height = self.image.get_height()

        width = 0
        for ch in text:
            if ch == " ":
                width += word_spacing
            elif ch in self.glyphs:
                width += self.glyphs[ch].get_width() + letter_spacing
        width -= letter_spacing
        if width < 0: width = 0

        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        x = 0
        for ch in text:
            if ch == " ":
                x += word_spacing
            elif ch in self.glyphs:
                glyph = self.glyphs[ch]
                surf.blit(glyph, (x, 0))
                x += glyph.get_width() + letter_spacing

        return surf