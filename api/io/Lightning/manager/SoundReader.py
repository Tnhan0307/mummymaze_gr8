import random
import pygame, os
from api.io.Lightning.utils.ConfigFile import UI_PATH, MUSIC_PATH, SOUNDS_PATH

class MusicManager:
    def __init__(self):
        self.music_enabled = False
        self.current_track = 0
        self.loop_tracks = list(range(1, 13))
        self.current_loop_index = 0
        self.MUSIC_END = pygame.USEREVENT + 1
        self.initialized = False
        self.current_mode = "menu"
        self.volume = 0.5  # Default volume

    def initialize(self):
        if self.initialized: return
        try:
            if not pygame.mixer.get_init(): pygame.mixer.init()
            pygame.mixer.music.set_volume(self.volume)

            start_music = os.path.join(MUSIC_PATH, "00.mp3")
            if os.path.exists(start_music):
                pygame.mixer.music.load(start_music)
                pygame.mixer.music.play()
                pygame.mixer.music.set_endevent(self.MUSIC_END)
                self.music_enabled = True
                self.initialized = True
        except Exception as e:
            print(f'Music Init Error: {e}')

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))
        if self.initialized:
            pygame.mixer.music.set_volume(self.volume)

    def get_volume(self):
        return self.volume

    def handle_event(self, event):
        if event.type == self.MUSIC_END and self.music_enabled:
            try:
                if self.current_mode == "menu":
                    if self.current_track == 0:
                        self.current_track = self.loop_tracks[self.current_loop_index]
                    else:
                        self.current_loop_index = (self.current_loop_index + 1) % len(self.loop_tracks)
                        self.current_track = self.loop_tracks[self.current_loop_index]
                    self._play_track(f'{self.current_track:02d}.mp3')

                elif self.current_mode == "classic":
                    self.current_loop_index = (self.current_loop_index + 1) % len(self.loop_tracks)
                    self.current_track = self.loop_tracks[self.current_loop_index]
                    self._play_track(f'{self.current_track:02d}.mp3')

                elif self.current_mode == "hard":
                    self._play_track("hard_mode.mp3")

            except Exception as e:
                print(f'Music Loop Error: {e}')

    def _play_track(self, filename):
        path = os.path.join(MUSIC_PATH, filename)
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        else:
            print(f"Missing track: {path}")

    def start_classic_mode_music(self):
        self.current_mode = "classic"
        self.loop_tracks = list(range(23, 39))
        self.current_loop_index = 0
        self.current_track = self.loop_tracks[0]
        self._play_track(f'{self.current_track:02d}.mp3')

    def start_menu_music(self):
        self.current_mode = "menu"
        self.loop_tracks = list(range(1, 13))
        self.current_loop_index = 0
        self.current_track = self.loop_tracks[0]
        self._play_track(f'{self.current_track:02d}.mp3')

    def start_hard_mode_music(self):
        self.current_mode = "hard"
        self._play_track("hard_mode.mp3")

    def stop(self):
        if self.music_enabled:
            pygame.mixer.music.stop()


class SoundEffectManager:
    def __init__(self):
        self.sounds = {}
        self.initialized = False
        self.volume = 0.5  # Default volume

    def initialize(self):
        if self.initialized: return
        if not pygame.mixer.get_init(): pygame.mixer.init()

        def load(name):
            path = os.path.join(SOUNDS_PATH, name)
            if os.path.exists(path):
                snd = pygame.mixer.Sound(path)
                snd.set_volume(self.volume)
                return snd
            return None

        # 1. Load Walk Sounds
        for variant in ['15', '30', '60']:
            self.sounds[f'exp_start_{variant}'] = load(f'expwalk{variant}a.wav')
            self.sounds[f'exp_end_{variant}'] = load(f'expwalk{variant}b.wav')
            self.sounds[f'mum_start_{variant}'] = load(f'mumwalk{variant}a.wav')
            self.sounds[f'mum_end_{variant}'] = load(f'mumwalk{variant}b.wav')

        self.sounds['scorp_1'] = load('scorpwalk1.wav')
        self.sounds['scorp_2'] = load('scorpwalk2.wav')

        # 2. Load Action Sounds
        self.sounds['pummel'] = load('pummel.wav')
        self.sounds['tombslide'] = load('tombslide.wav')
        self.sounds['gate'] = load('gate.wav')

        # --- FIX: Ensure these are loaded for the death/ankh logic ---
        self.sounds['badankh'] = load('badankh.wav')
        self.sounds['poison'] = load('poison.wav')
        # -------------------------------------------------------------

        self.initialized = True

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))
        if self.initialized:
            for sound in self.sounds.values():
                if sound: sound.set_volume(self.volume)

    def get_volume(self):
        return self.volume

    def play(self, name):
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].play()

    def play_walk_start(self, entity_type):
        variant = random.choice(['15', '30', '60'])
        if entity_type == 'player':
            self.play(f'exp_start_{variant}')
        elif 'mummy' in entity_type:
            self.play(f'mum_start_{variant}')
        elif 'scorpion' in entity_type:
            scorp_var = random.choice(['1', '2'])
            self.play(f'scorp_{scorp_var}')
            return None
        return variant

    def play_walk_end(self, entity_type, variant):
        if not variant: return
        if entity_type == 'player':
            self.play(f'exp_end_{variant}')
        elif 'mummy' in entity_type:
            self.play(f'mum_end_{variant}')

music_manager = MusicManager()
sfx_manager = SoundEffectManager()