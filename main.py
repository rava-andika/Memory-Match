import pygame
import sys
import os
import random
import time
import csv
from datetime import datetime
from typing import List, Tuple, Optional
from nightmare_mode import NightmareBoard, NightmareCard


SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

MODES = {"easy": (4, 4), "medium": (4, 6), "hard": (6, 6), "nightmare": (4, 4)}
MODE_LIST = ["easy", "medium", "hard", "nightmare"]
MODE_THEME_MAP = {
    "easy": {
        1: "flowers",
        2: "dresses",
        3: "disney",
        4: "fc_teams"
    },
    "medium": {
        1: "animals",
        2: "disney",
        3: "emoji",
        4: "fc_teams"
    },
    "hard": {
        1: "animals",
        2: "disney",
        3: "emoji",
        4: "fc_teams"
    },
    "nightmare": {
        1: "nightmare"
    }
}

THEME_NAMES = {
    "easy": ["Flowers", "Dresses", "Disney", "FC Teams"],
    "medium": ["Animal", "Disney", "Emoji", "FC Teams"],
    "hard": ["Animal", "Disney", "Emoji", "FC Teams"],
    "nightmare": ["Nightmare"]
}
FLIP_BACK_DELAY = 0.8
FLIP_ANIMATION_SPEED = 15

ASSETS_DIR = "assets"
CARDS_DIR = f"{ASSETS_DIR}/images/cards"
BACKGROUNDS_DIR = f"{ASSETS_DIR}/images/backgrounds"
MUSIC_DIR = f"{ASSETS_DIR}/audio/music"
SFX_DIR = f"{ASSETS_DIR}/audio/sfx"
DATA_DIR = "data"

os.makedirs(CARDS_DIR, exist_ok=True)
os.makedirs(BACKGROUNDS_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR, exist_ok=True)
os.makedirs(SFX_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

USER_FILE = f"{DATA_DIR}/users.csv"
SCORE_FILE = f"{DATA_DIR}/score.csv"

COLOR_BACKGROUND = (30, 30, 40)
COLOR_TEXT = (240, 240, 240)
COLOR_TEXT_DARK = (50, 50, 50)
COLOR_BUTTON_NORMAL = (60, 60, 80, 150)
COLOR_BUTTON_HOVER = (80, 120, 200, 180)
COLOR_BUTTON_SELECTED = (100, 255, 100, 200)
COLOR_BORDER_NORMAL = (100, 150, 255)
COLOR_BORDER_HOVER = (150, 200, 255)
COLOR_BORDER_SELECTED = (255, 215, 0)
COLOR_GOLD = (255, 215, 0)
COLOR_GRAY = (100, 100, 100)
COLOR_TITLE = (255, 200, 50)
COLOR_SUBTITLE = (150, 200, 255)
COLOR_INPUT_BG = (40, 40, 60)
COLOR_INPUT_ACTIVE = (60, 60, 100)
COLOR_ERROR = (255, 100, 100)


STAR_RULES = {
    "easy": [(20, 3), (40, 2), (60, 1)],
    "medium": [(35, 3), (70, 2), (100, 1)],
    "hard": [(50, 3), (90, 2), (120, 1)],
    "nightmare": [(20, 3), (40, 2), (60, 1)]
}


def init_csv() -> None:
    if not os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'username', 'mode', 'theme', 'time_seconds', 'moves', 'stars'])
            print("Score file initialized successfully")
        except Exception as e:
            print(f"Error initializing score file: {e}")
    
    if not os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['username', 'created_at'])
            print("User file initialized successfully")
        except Exception as e:
            print(f"Error initializing user file: {e}")

def save_user(username: str) -> bool:
    try:
        with open(USER_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([username, timestamp])
        print(f"User saved: {username}")
        return True
    except Exception as e:
        print(f"Error saving user: {e}")
        return False

def save_score(username: str, mode: str, theme: int, time_seconds: int, moves: int, stars: int) -> None:
    try:
        with open(SCORE_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([timestamp, username, mode, theme, time_seconds, moves, stars])
        print(f"Score saved: {username}, {mode}, theme {theme}, {time_seconds}s, {moves} moves, {stars} stars")
    except Exception as e:
        print(f"Error saving score: {e}")

def load_scores() -> List[dict]:
    scores = []
    if not os.path.exists(SCORE_FILE):
        return scores

    with open(SCORE_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                scores.append({
                    'timestamp': row.get('timestamp', ''),
                    'username': row.get('username', 'Unknown'),
                    'mode': row.get('mode', 'easy'),
                    'theme': int(row.get('theme', 1)),
                    'time_seconds': int(row.get('time_seconds', 0)),
                    'moves': int(row.get('moves', 0)),
                    'stars': int(row.get('stars', 0))
                })
            except Exception as e:
                print("Skipping invalid row:", row, e)
    return scores


def get_top_scores(mode: Optional[str] = None, limit: int = 10, username: Optional[str] = None) -> List[dict]:
    scores = load_scores()
    if mode:
        scores = [s for s in scores if s['mode'] == mode]
    if username:
        scores = [s for s in scores if s['username'] == username]
    scores.sort(key=lambda x: (-x['stars'], x['time_seconds'], x['moves']))
    return scores[:limit]

def user_exists(username: str) -> bool:
    try:
        if not os.path.exists(USER_FILE):
            return False
        with open(USER_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['username'] == username:
                    return True
        return False
    except Exception as e:
        print(f"Error checking user: {e}")
        return False


def load_theme_images(mode: str, theme: int) -> Tuple[List[Tuple], Optional[pygame.Surface]]:
    """
    OPTIMIZED: Load from shared card collections
    
    OLD: assets/images/easy/theme1/card1.png
         assets/images/medium/theme2/card1.png (DUPLICATE!)
         assets/images/hard/theme3/card1.png (DUPLICATE!)
    
    NEW: assets/images/cards/flowers/card1.png (SHARED!)
    """
    collection_name = MODE_THEME_MAP.get(mode, {}).get(theme)
    
    if not collection_name:
        print(f"Warning: No collection for {mode} theme {theme}")
        collection_name = "animals"
    
    collection_path = f"{CARDS_DIR}/{collection_name}"
    imgs = []
    
    # Load shared card back
    back_path = f"{CARDS_DIR}/shared/card_back.png"
    back = None
    
    try:
        if os.path.exists(back_path):
            back = pygame.image.load(back_path).convert_alpha()
        else:
            back = create_default_back_image()
    except Exception as e:
        print(f"Error loading card back: {e}")
        back = create_default_back_image()
    
    try:
        if os.path.isdir(collection_path):
            for f in os.listdir(collection_path):
                if f.lower().endswith((".png", ".jpg", ".jpeg")):
                    p = os.path.join(collection_path, f)
                    try:
                        surf = pygame.image.load(p).convert_alpha()
                        imgs.append((surf, f))
                    except Exception as e:
                        print(f"Error loading {p}: {e}")
        
        pairs_needed = (MODES[mode][0] * MODES[mode][1]) // 2
        while len(imgs) < pairs_needed:
            imgs.append(create_placeholder_image(len(imgs) + 1))
            
    except Exception as e:
        print(f"Error loading from {collection_path}: {e}")
        pairs_needed = (MODES[mode][0] * MODES[mode][1]) // 2
        imgs = [create_placeholder_image(i + 1) for i in range(pairs_needed)]
    
    return imgs, back


def load_background_image(path: str, default_color: Tuple = COLOR_BACKGROUND) -> Optional[pygame.Surface]:
    """Load and scale background"""
    if os.path.exists(path):
        try:
            bg = pygame.image.load(path).convert()
            return pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"Error loading background {path}: {e}")
    return None


def load_menu_background(mode: str = "normal", theme: int = 1) -> Optional[pygame.Surface]:
    """Load menu background - different for nightmare mode"""
    if mode == "nightmare":
        path = f"{BACKGROUNDS_DIR}/nightmare_menu.jpg"
    else:
        path = f"{BACKGROUNDS_DIR}/menu.jpg"
    return load_background_image(path)


def load_difficulty_background() -> Optional[pygame.Surface]:
    """KEEP unique difficulty background"""
    return load_background_image(f"{BACKGROUNDS_DIR}/difficulty.jpg")


def load_leaderboard_background() -> Optional[pygame.Surface]:
    """KEEP unique leaderboard background"""
    return load_background_image(f"{BACKGROUNDS_DIR}/leaderboard.jpg")


def load_settings_background() -> Optional[pygame.Surface]:
    """KEEP unique settings background"""
    return load_background_image(f"{BACKGROUNDS_DIR}/settings.jpg")


def load_theme_background() -> Optional[pygame.Surface]:
    """KEEP unique theme selection background"""
    return load_background_image(f"{BACKGROUNDS_DIR}/theme_selection.jpg")


def load_game_background(mode: str, theme: int) -> Optional[pygame.Surface]:
    """
    Load game background (can be same or different per preference)
    """
    if mode == "nightmare":
        return load_background_image(f"{BACKGROUNDS_DIR}/nightmare.jpg")
    else:
        # Option 1: Use default game background for all
        # return load_background_image(f"{BACKGROUNDS_DIR}/game_default.jpg")
        
        # Option 2: If you want theme-specific game backgrounds, uncomment:
        collection = MODE_THEME_MAP.get(mode, {}).get(theme)
        return load_background_image(f"{BACKGROUNDS_DIR}/{collection}.jpg")


def load_menu_music() -> Optional[str]:
    """KEEP unique menu music"""
    music_path = f"{MUSIC_DIR}/menu.mp3"
    return music_path if os.path.exists(music_path) else None


def load_game_music(mode: str, theme: int) -> Optional[str]:
    if mode == "nightmare":
        music_path = f"{MUSIC_DIR}/nightmare.mp3"
    else:
        collection = MODE_THEME_MAP.get(mode, {}).get(theme)
        
        if collection:
            music_path = f"{MUSIC_DIR}/{collection}.mp3"
        else:
            print(f"Warning: No collection found for {mode} theme {theme}")
            return None
    
    if os.path.exists(music_path):
        return music_path
    
    print(f"Warning: Music not found at {music_path}")
    return None


def load_sound_effects() -> dict:
    """Load sound effects"""
    sounds = {}
    
    sound_files = {
        'flip': 'card_flip.wav',
        'match': 'card_match.wav',
        'win': 'win.wav',
    }
    
    for key, filename in sound_files.items():
        path = f"{SFX_DIR}/{filename}"
        if os.path.exists(path):
            try:
                sounds[key] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"Error loading sound {path}: {e}")
                sounds[key] = None
        else:
            sounds[key] = None
    
    return sounds


def create_default_back_image() -> pygame.Surface:
    """Create default card back"""
    surf = pygame.Surface((100, 100))
    surf.fill((50, 50, 150))
    pygame.draw.rect(surf, (100, 100, 200), (10, 10, 80, 80), 5)
    font = pygame.font.SysFont(None, 40)
    text = font.render("?", True, (255, 255, 255))
    surf.blit(text, (35, 25))
    return surf


def create_placeholder_image(number: int) -> Tuple[pygame.Surface, str]:
    """Create placeholder card"""
    surf = pygame.Surface((100, 100))
    surf.fill((random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)))
    font = pygame.font.SysFont(None, 50)
    text = font.render(str(number), True, (255, 255, 255))
    text_rect = text.get_rect(center=(50, 50))
    surf.blit(text, text_rect)
    return (surf, f"placeholder_{number}")


class AudioController:
    
    def __init__(self):
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.music_enabled = True
        self.sfx_enabled = True
        self.current_music = None
    
    def play_music(self, music_path: Optional[str], loop: int = -1, volume: Optional[float] = None) -> None:
        if not self.music_enabled or not music_path:
            return
        
        try:
            if self.current_music != music_path:
                pygame.mixer.music.load(music_path)
                self.current_music = music_path

            if volume is not None:
                self.music_volume = volume
            
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loop)
            
        except Exception as e:
            print(f"Error playing music: {e}")
    
    def stop_music(self) -> None:
        pygame.mixer.music.stop()
    
    def play_sound(self, sound: Optional[pygame.mixer.Sound]) -> None:
        if self.sfx_enabled and sound:
            try:
                sound.set_volume(self.sfx_volume)
                sound.play()
            except Exception as e:
                print(f"Error playing sound: {e}")
    
    def set_music_volume(self, volume: float) -> None:
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume: float) -> None:
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def toggle_music(self) -> None:
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()
        else:
            if self.current_music:
                try:
                    pygame.mixer.music.load(self.current_music)
                    pygame.mixer.music.set_volume(self.music_volume)
                    pygame.mixer.music.play(-1)
                except Exception as e:
                    print(f"Error replaying music: {e}")
    
    def toggle_sfx(self) -> None:
        self.sfx_enabled = not self.sfx_enabled

class InputBox:
    
    def __init__(self, x: int, y: int, width: int, height: int, font: pygame.font.Font, placeholder: str = ""):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return False
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return True
            elif event.key == pygame.K_RETURN:
                return False
            elif len(self.text) < 20:
                if event.unicode.isprintable() and event.unicode not in [' ', '\t', '\n']:
                    self.text += event.unicode
                    return True
        return False
    
    def update(self) -> None:
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, screen: pygame.Surface) -> None:
        bg_color = COLOR_INPUT_ACTIVE if self.active else COLOR_INPUT_BG
        
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=5)
        
        border_color = COLOR_BORDER_HOVER if self.active else COLOR_BORDER_NORMAL
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=5)
        
        if self.text:
            text_surf = self.font.render(self.text, True, COLOR_TEXT)
        else:
            text_surf = self.font.render(self.placeholder, True, COLOR_GRAY)
        
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        screen.blit(text_surf, text_rect)
        
        if self.active and self.cursor_visible and self.text:
            cursor_x = text_rect.right + 2
            cursor_y1 = self.rect.centery - 12
            cursor_y2 = self.rect.centery + 12
            pygame.draw.line(screen, COLOR_TEXT, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)

class Card:
    
    def __init__(self, rect: pygame.Rect, surf: pygame.Surface, card_id: str):
        self.rect = rect
        self.surf = surf
        self.id = card_id
        self.flipped = False
        self.matched = False
        self.flip_progress = 0
        self.target_flip = 0
    
    def start_flip(self, show_front: bool) -> None:
        self.target_flip = 1 if show_front else 0
    
    def update_animation(self) -> None:
        if self.flip_progress < self.target_flip:
            self.flip_progress = min(1, self.flip_progress + FLIP_ANIMATION_SPEED / 100)
        elif self.flip_progress > self.target_flip:
            self.flip_progress = max(0, self.flip_progress - FLIP_ANIMATION_SPEED / 100)

        if abs(self.flip_progress - self.target_flip) < 0.01:
            self.flipped = (self.target_flip == 1)
    
    def draw(self, screen: pygame.Surface, back: pygame.Surface) -> None:
        if self.matched or self.flip_progress > 0.5:
            img = self.surf
        else:
            img = back

        scale_x = abs(1 - 2 * self.flip_progress)
        if scale_x < 0.1:
            scale_x = 0.1

        scaled_w = int(self.rect.w * scale_x)
        scaled_h = self.rect.h
        
        if scaled_w > 0 and scaled_h > 0:
            scaled_img = pygame.transform.smoothscale(img, (scaled_w, scaled_h))
            draw_x = self.rect.x + (self.rect.w - scaled_w) // 2
            screen.blit(scaled_img, (draw_x, self.rect.y))

        pygame.draw.rect(screen, (220, 220, 220), self.rect, 2)


class Board:
    
    def __init__(self, mode: str, theme: int):
        self.rows, self.cols = MODES[mode]
        self.mode = mode
        self.theme = theme

        imgs, back = load_theme_images(mode, theme)
        self.back = back

        pairs = (self.rows * self.cols) // 2
        random.shuffle(imgs)
        chosen = imgs[:pairs]
        pool = [x for x in chosen for _ in (0, 1)]
        random.shuffle(pool)
        
        self.cards = []
        w = 100 if mode == "easy" else 80
        h = w
        pad = 12
        totw = self.cols * w + (self.cols - 1) * pad
        toth = self.rows * h + (self.rows - 1) * pad
        sx = (SCREEN_WIDTH - totw) // 2
        sy = (SCREEN_HEIGHT - toth) // 2
        
        for i, (surf, card_id) in enumerate(pool):
            r = i // self.cols
            c = i % self.cols
            x = sx + c * (w + pad)
            y = sy + r * (h + pad)
            self.cards.append(Card(pygame.Rect(x, y, w, h), surf, card_id))
    
    def update(self) -> None:
        for card in self.cards:
            card.update_animation()
    
    def draw(self, screen: pygame.Surface) -> None:
        for card in self.cards:
            card.draw(screen, self.back)
    
    def all_matched(self) -> bool:
        return all(card.matched for card in self.cards)


class Button:
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, font: pygame.font.Font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.hovered = False
        self.enabled = True
    
    def draw(self, screen: pygame.Surface, selected: bool = False) -> None:
        if not self.enabled:
            bg_color = (40, 40, 40, 100)
            border_color = (80, 80, 80)
            text_color = (100, 100, 100)
        elif selected:
            bg_color = COLOR_BUTTON_SELECTED
            border_color = COLOR_BORDER_SELECTED
            text_color = COLOR_TEXT_DARK
        elif self.hovered:
            bg_color = COLOR_BUTTON_HOVER
            border_color = COLOR_BORDER_HOVER
            text_color = COLOR_TEXT
        else:
            bg_color = COLOR_BUTTON_NORMAL
            border_color = COLOR_BORDER_NORMAL
            text_color = (200, 200, 200)

        btn_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        btn_surf.fill(bg_color)
        screen.blit(btn_surf, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=10)

        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.enabled and self.rect.collidepoint(pos)
    
    def update_hover(self, pos: Tuple[int, int]) -> None:
        self.hovered = self.enabled and self.rect.collidepoint(pos)


class Slider:
    
    def __init__(self, x: int, y: int, width: int, min_val: float, max_val: float, initial_val: float, label: str):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        self.handle_radius = 12
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        label_surf = font.render(self.label, True, COLOR_TEXT)
        screen.blit(label_surf, (self.rect.x, self.rect.y - 25))

        pygame.draw.rect(screen, (100, 100, 100), self.rect, border_radius=5)

        fill_width = int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(screen, COLOR_SUBTITLE, fill_rect, border_radius=5)

        handle_x = self.rect.x + fill_width
        handle_y = self.rect.centery
        pygame.draw.circle(screen, COLOR_TEXT, (handle_x, handle_y), self.handle_radius)
        pygame.draw.circle(screen, COLOR_SUBTITLE, (handle_x, handle_y), self.handle_radius - 2)
        
        value_text = font.render(f"{int(self.value * 100)}%", True, COLOR_TEXT)
        screen.blit(value_text, (self.rect.right + 10, self.rect.y))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            handle_x = self.rect.x + int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
            if ((mouse_x - handle_x) ** 2 + (mouse_y - self.rect.centery) ** 2) <= self.handle_radius ** 2:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_x = event.pos[0]
            relative_x = mouse_x - self.rect.x
            ratio = max(0, min(1, relative_x / self.rect.width))
            new_value = self.min_val + ratio * (self.max_val - self.min_val)
            if abs(new_value - self.value) > 0.01:
                self.value = new_value
                return True
        return False


class Game:
    
    def __init__(self, screen: pygame.Surface, mode: str, theme: int, 
                 audio: AudioController, sounds: dict, username: str):
        self.screen = screen
        self.mode = mode
        self.theme = theme
        self.audio = audio
        self.sounds = sounds
        self.username = username
        
        if mode == "nightmare":
            self.board = NightmareBoard(rows=4, cols=4)
        else:
            self.board = Board(mode, theme)
        self.flipped_cards = []
        self.lock_until = 0
        self.start_time = time.time()
        self.end_time = None
        self.score_saved = False
        self.moves = 0
        self.paused = False
        self.pause_time = 0 
        self.pause_start = 0

        self.game_bg = load_game_background(mode, theme)
        
        game_music = load_game_music(mode, theme)
        self.audio.play_music(game_music)
        
        self.create_pause_menu()
    
    def create_pause_menu(self) -> None:
        font = pygame.font.SysFont(None, 36)
        self.pause_buttons = {
            'resume': Button(250, 240, 300, 50, "Resume", font),
            'restart': Button(250, 310, 300, 50, "Restart", font),
            'settings': Button(250, 380, 300, 50, "Settings", font),
            'menu': Button(250, 450, 300, 50, "Main Menu", font)
        }
    
    def toggle_pause(self) -> None:
        if not self.end_time:
            self.paused = not self.paused
            
            if self.paused:
                self.pause_start = time.time()
                pygame.mixer.music.pause()
            else:
                self.pause_time += (time.time() - self.pause_start)
                pygame.mixer.music.unpause()
    
    def click(self, pos: Tuple[int, int]) -> None:
        if time.time() < self.lock_until or self.end_time or self.paused:
            return
        
        for card in self.board.cards:
            if card.rect.collidepoint(pos) and not card.flipped and not card.matched:
                card.start_flip(True)
                self.flipped_cards.append(card)
                self.audio.play_sound(self.sounds['flip'])
                
                if len(self.flipped_cards) == 2:
                    self.moves += 1
                    self.check_match()
                return
    
    def check_match(self) -> None:
        c1, c2 = self.flipped_cards
        
        if c1.id == c2.id:
            c1.matched = c2.matched = True
            self.flipped_cards = []
            self.audio.play_sound(self.sounds['match'])

            if self.board.all_matched():
                self.end_time = time.time()
                self.audio.stop_music()
                self.audio.play_sound(self.sounds['win'])
        else:
            self.lock_until = time.time() + FLIP_BACK_DELAY
    
    def update(self) -> None:
        if self.paused:
            return

        self.board.update()

        if self.lock_until and time.time() >= self.lock_until:
            for card in self.flipped_cards:
                card.start_flip(False)
            self.flipped_cards = []
            self.lock_until = 0
    
    def draw(self) -> None:
        if self.game_bg:
            self.screen.blit(self.game_bg, (0, 0))
        else:
            self.screen.fill(COLOR_BACKGROUND)

        self.board.draw(self.screen)

        self.draw_hud()

        if self.paused:
            self.draw_pause_menu()
        
        if self.end_time:
            self.draw_win_screen()
    
    def draw_hud(self) -> None:
        if self.end_time:
            elapsed = int(self.end_time - self.start_time - self.pause_time)
        elif self.paused:
            elapsed = int(self.pause_start - self.start_time - self.pause_time)
        else:
            current_pause = (time.time() - self.pause_start) if self.paused else 0
            elapsed = int(time.time() - self.start_time - self.pause_time - current_pause)
        font = pygame.font.SysFont(None, 30)
        font_small = pygame.font.SysFont(None, 24)

        hud_surf = pygame.Surface((140, 85), pygame.SRCALPHA)
        hud_surf.fill((0, 0, 0, 150))
        self.screen.blit(hud_surf, (10, 10))

        time_text = font.render(f"Time: {elapsed}s", True, COLOR_TEXT)
        self.screen.blit(time_text, (20, 20))

        moves_text = font.render(f"Moves: {self.moves}", True, COLOR_TEXT)
        self.screen.blit(moves_text, (20, 45))
        
        user_text = font_small.render(f"Player: {self.username}", True, COLOR_SUBTITLE)
        self.screen.blit(user_text, (20, 70))
    
    def draw_pause_menu(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        font_title = pygame.font.SysFont(None, 70)
        title = font_title.render("PAUSED", True, COLOR_TITLE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        for button in self.pause_buttons.values():
            button.update_hover(mouse_pos)
            button.draw(self.screen)
    
    def handle_pause_click(self, pos: Tuple[int, int]) -> Optional[str]:
        if self.pause_buttons['resume'].is_clicked(pos):
            self.toggle_pause()
            return None
        elif self.pause_buttons['restart'].is_clicked(pos):
            return 'restart'
        elif self.pause_buttons['settings'].is_clicked(pos):
            return 'settings'
        elif self.pause_buttons['menu'].is_clicked(pos):
            return 'menu'
        return None
    
    def draw_win_screen(self) -> None:
        elapsed = int(self.end_time - self.start_time - self.pause_time)
        stars = self.calculate_stars(elapsed)
        
        if not self.score_saved:
            save_score(self.username, self.mode, self.theme, elapsed, self.moves, stars)
            self.score_saved = True
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.SysFont(None, 60)
        font_medium = pygame.font.SysFont(None, 40)
        font_small = pygame.font.SysFont(None, 30)
        
        title = font_large.render("VICTORY!", True, COLOR_TITLE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)
        
        stats_y = 200
        time_text = font_medium.render(f"Time: {elapsed}s", True, COLOR_TEXT)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, stats_y))
        self.screen.blit(time_text, time_rect)
        
        moves_text = font_medium.render(f"Moves: {self.moves}", True, COLOR_TEXT)
        moves_rect = moves_text.get_rect(center=(SCREEN_WIDTH // 2, stats_y + 40))
        self.screen.blit(moves_text, moves_rect)
        
        self.draw_stars(stars, stats_y + 100)
        
        inst_y = stats_y + 200
        r_text = font_small.render("Press R to Restart", True, COLOR_SUBTITLE)
        m_text = font_small.render("Press M for Main Menu", True, COLOR_SUBTITLE)
        
        r_rect = r_text.get_rect(center=(SCREEN_WIDTH // 2, inst_y))
        m_rect = m_text.get_rect(center=(SCREEN_WIDTH // 2, inst_y + 35))
        
        self.screen.blit(r_text, r_rect)
        self.screen.blit(m_text, m_rect)
    
    def draw_stars(self, count: int, y: int) -> None:
        star_size = 50
        spacing = 70
        start_x = SCREEN_WIDTH // 2 - spacing
        
        for i in range(3):
            x = start_x + i * spacing
            color = COLOR_GOLD if i < count else COLOR_GRAY
            self.draw_star(x, y, star_size, color)
    
    def draw_star(self, cx: int, cy: int, size: int, color: Tuple) -> None:
        import math
        points = []
        for i in range(10):
            angle = math.pi / 2 + (2 * math.pi * i / 10)
            radius = size if i % 2 == 0 else size * 0.4
            x = cx + radius * math.cos(angle)
            y = cy - radius * math.sin(angle)
            points.append((x, y))
        pygame.draw.polygon(self.screen, color, points)
    
    def calculate_stars(self, elapsed: int) -> int:
        for time_limit, star_count in STAR_RULES[self.mode]:
            if elapsed <= time_limit:
                return star_count
        return 0

def draw_background(screen: pygame.Surface, bg_image: Optional[pygame.Surface]) -> None:
    if bg_image:
        screen.blit(bg_image, (0, 0))
    else:
        screen.fill(COLOR_BACKGROUND)

def draw_title(screen: pygame.Surface, text: str, y: int = 120) -> None:
    font = pygame.font.SysFont(None, 60)
    shadow = font.render(text, True, (0, 0, 0))
    title = font.render(text, True, COLOR_TITLE)
    
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, y))
    shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, y + 2))
    
    screen.blit(shadow, shadow_rect)
    screen.blit(title, title_rect)

def start_menu(screen: pygame.Surface, bg_image: Optional[pygame.Surface], 
               audio: AudioController, sounds: dict) -> str:
    font_btn = pygame.font.SysFont(None, 40)
    font_small = pygame.font.SysFont(None, 28)
    
    buttons = {
        'start': Button(250, 180, 300, 60, "START", font_btn),
        'leaderboard': Button(250, 260, 300, 60, "LEADERBOARD", font_btn),
        'settings': Button(250, 340, 300, 60, "SETTINGS", font_btn),
    }
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons['start'].is_clicked(mouse_pos):
                    return 'start'
                elif buttons['leaderboard'].is_clicked(mouse_pos):
                    return 'leaderboard'
                elif buttons['settings'].is_clicked(mouse_pos):
                    return 'settings'

        for button in buttons.values():
            button.update_hover(mouse_pos)

        draw_background(screen, bg_image)
        draw_title(screen, "")
        
        for button in buttons.values():
            button.draw(screen)
        
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

def mode_selection_menu(screen: pygame.Surface, bg_image: Optional[pygame.Surface],
                        audio: AudioController, sounds: dict) -> Optional[str]:
    font_btn = pygame.font.SysFont(None, 40)
    font_small = pygame.font.SysFont(None, 28)
    font_desc = pygame.font.SysFont(None, 24)
    
    buttons = {
        'normal': Button(220, 240, 360, 60, "NORMAL MODE", font_btn),
        'nightmare': Button(220, 330, 360, 60, "NIGHTMARE MODE", font_btn),
    }
    
    descriptions = {
        'normal': "Memory Match",
        'nightmare': "Memory Math"
    }
    
    back_btn = Button(30, 30, 100, 40, "Back", font_small)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.is_clicked(mouse_pos):
                    return 'back'
                elif buttons['normal'].is_clicked(mouse_pos):
                    return 'normal'
                elif buttons['nightmare'].is_clicked(mouse_pos):
                    return 'nightmare'
        
        back_btn.update_hover(mouse_pos)
        for btn in buttons.values():
            btn.update_hover(mouse_pos)

        draw_background(screen, bg_image)

        frame_rect = pygame.Rect(180, 200, 440, 240)
        pygame.draw.rect(screen, (40, 40, 60), frame_rect, border_radius=15)
        pygame.draw.rect(screen, (100, 200, 255), frame_rect, 3, border_radius=15)
        
        draw_title(screen, "SELECT MODE", y=140)
        
        back_btn.draw(screen)

        for key, btn in buttons.items():
            btn.draw(screen)
            desc_text = font_desc.render(descriptions[key], True, (150, 200, 255))
            desc_rect = desc_text.get_rect(center=(btn.rect.centerx, btn.rect.bottom + 18))
            screen.blit(desc_text, desc_rect)
        
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

def difficulty_menu(screen: pygame.Surface, bg_image: Optional[pygame.Surface],
                    audio: AudioController, sounds: dict) -> Optional[str]:
    font_btn = pygame.font.SysFont(None, 36)
    font_small = pygame.font.SysFont(None, 28)
    
    modes_text = ["Easy (4x4)", "Medium (4x6)", "Hard (6x6)"]
    buttons = []
    
    for i, text in enumerate(modes_text):
        btn = Button(220, 240 + i * 70, 360, 55, text, font_btn)
        buttons.append(btn)
    
    back_btn = Button(30, 30, 100, 40, "Back", font_small)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.is_clicked(mouse_pos):
                    return 'back'
                for i, btn in enumerate(buttons):
                    if btn.is_clicked(mouse_pos):
                        return MODE_LIST[i]

        back_btn.update_hover(mouse_pos)
        for btn in buttons:
            btn.update_hover(mouse_pos)
        
        draw_background(screen, bg_image)
        draw_title(screen, "SELECT DIFFICULTY", y=150)
        
        back_btn.draw(screen)
        for btn in buttons:
            btn.draw(screen)
        
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

def theme_menu(screen: pygame.Surface, mode: str, bg_image: Optional[pygame.Surface],
               audio: AudioController, sounds: dict) -> Optional[int]:
    font_btn = pygame.font.SysFont(None, 36)
    font_small = pygame.font.SysFont(None, 28)
    
    themes = THEME_NAMES.get(mode, [f"Theme {i+1}" for i in range(4)])
    buttons = []
    
    for i, text in enumerate(themes):
        btn = Button(220, 220 + i * 65, 360, 50, text, font_btn)
        buttons.append(btn)
    
    back_btn = Button(30, 30, 100, 40, "Back", font_small)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.is_clicked(mouse_pos):
                    return -1
                for i, btn in enumerate(buttons):
                    if btn.is_clicked(mouse_pos):
                        return i + 1

        back_btn.update_hover(mouse_pos)
        for btn in buttons:
            btn.update_hover(mouse_pos)

        draw_background(screen, bg_image)
        draw_title(screen, "SELECT THEME", y=150)
        
        back_btn.draw(screen)
        for btn in buttons:
            btn.draw(screen)
        
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

def nightmare_menu(screen: pygame.Surface, bg_image: Optional[pygame.Surface],
                   audio: AudioController, sounds: dict) -> str:
    font_btn = pygame.font.SysFont(None, 40)
    font_small = pygame.font.SysFont(None, 28)
    
    buttons = {
        'start': Button(250, 220, 300, 60, "START", font_btn),
        'leaderboard': Button(250, 300, 300, 60, "LEADERBOARD", font_btn),
        'settings': Button(250, 380, 300, 60, "SETTINGS", font_btn),
    }
    
    back_btn = Button(30, 30, 100, 40, "Back", font_small)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.is_clicked(mouse_pos):
                    return 'back'
                elif buttons['start'].is_clicked(mouse_pos):
                    return 'start'
                elif buttons['leaderboard'].is_clicked(mouse_pos):
                    return 'leaderboard'
                elif buttons['settings'].is_clicked(mouse_pos):
                    return 'settings'
        
        for button in buttons.values():
            button.update_hover(mouse_pos)
        back_btn.update_hover(mouse_pos)
        
        draw_background(screen, bg_image)
        draw_title(screen, "", y=140)
        
        back_btn.draw(screen)
        for button in buttons.values():
            button.draw(screen)
        
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

def nightmare_leaderboard(screen: pygame.Surface, bg_image: Optional[pygame.Surface],
                         audio: AudioController, sounds: dict) -> None:
    font_title = pygame.font.SysFont(None, 50)
    font_tab = pygame.font.SysFont(None, 32)
    font_entry = pygame.font.SysFont(None, 24)
    font_small = pygame.font.SysFont(None, 20)
    
    back_btn = Button(30, 30, 100, 40, "Back", font_small)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.is_clicked(mouse_pos):
                    return
        
        back_btn.update_hover(mouse_pos)

        scores = get_top_scores(mode="nightmare")
        
        draw_background(screen, bg_image)
        draw_title(screen, "")
        
        main_frame = pygame.Rect(30, 145, SCREEN_WIDTH - 60, SCREEN_HEIGHT - 190)
        frame_bg = pygame.Surface((main_frame.width, main_frame.height), pygame.SRCALPHA)
        frame_bg.fill((20, 30, 45, 200))
        screen.blit(frame_bg, main_frame)
        pygame.draw.rect(screen, (255, 100, 100), main_frame, 3, border_radius=15)
        
        back_btn.draw(screen)

        header_y = 170
        headers = ["No", "Player", "Date", "Mode", "Time", "Moves", "Stars"]
        header_x = [40, 120, 280, 380, 500, 600, 700]
        
        for i, header in enumerate(headers):
            text = font_tab.render(header, True, COLOR_TITLE)
            screen.blit(text, (header_x[i], header_y))
        
        pygame.draw.line(screen, COLOR_SUBTITLE, (50, header_y + 35), 
                        (SCREEN_WIDTH - 50, header_y + 35), 2)

        entry_y = header_y + 50
        for i, score in enumerate(scores[:10]):
            if entry_y > SCREEN_HEIGHT - 80:
                break

            rank_color = COLOR_TEXT
            if i == 0:
                rank_color = (255, 215, 0)
            elif i == 1:
                rank_color = (192, 192, 192)
            elif i == 2:
                rank_color = (205, 127, 50)
            player_text = font_entry.render(score['username'], True, COLOR_SUBTITLE)
            screen.blit(player_text, (header_x[1], entry_y))

            rank_text = font_entry.render(f"{i+1}", True, rank_color)
            screen.blit(rank_text, (header_x[0], entry_y))

            date_str = score['timestamp'].split()[0]
            date_text = font_entry.render(date_str, True, COLOR_TEXT)
            screen.blit(date_text, (header_x[1], entry_y))

            time_text = font_entry.render(f"{score['time_seconds']}s", True, COLOR_TEXT)
            screen.blit(time_text, (header_x[2], entry_y))

            moves_text = font_entry.render(str(score['moves']), True, COLOR_TEXT)
            screen.blit(moves_text, (header_x[3], entry_y))

            for j in range(score['stars']):
                star_x = header_x[4] + j * 25
                draw_small_star(screen, star_x, entry_y + 10, 8, COLOR_GOLD)
            
            entry_y += 35

        if not scores:
            no_scores = font_tab.render("No nightmare scores yet!", True, (255, 100, 100))
            no_scores_rect = no_scores.get_rect(center=(SCREEN_WIDTH // 2, 350))
            screen.blit(no_scores, no_scores_rect)
        
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

def leaderboard_screen(screen: pygame.Surface, bg_image: Optional[pygame.Surface],
                       audio: AudioController, sounds: dict) -> None:
    font_tab = pygame.font.SysFont(None, 32)
    font_entry = pygame.font.SysFont(None, 24)
    font_small = pygame.font.SysFont(None, 20)
    
    back_btn = Button(30, 30, 100, 40, "Back", font_small)

    mode_buttons = {}
    mode_texts = ["All", "Easy", "Medium", "Hard"]
    for i, text in enumerate(mode_texts):
        btn = Button(200 + i * 110, 110, 100, 35, text, font_small)
        mode_buttons[text.lower()] = btn
    
    selected_mode = "all"
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.is_clicked(mouse_pos):
                    return
                for mode_name, btn in mode_buttons.items():
                    if btn.is_clicked(mouse_pos):
                        selected_mode = mode_name

        back_btn.update_hover(mouse_pos)
        for btn in mode_buttons.values():
            btn.update_hover(mouse_pos)

        if selected_mode == "all":
            scores = get_top_scores()
        else:
            scores = get_top_scores(mode=selected_mode)

        draw_background(screen, bg_image)
        draw_title(screen, "", y=100)
        
        main_frame = pygame.Rect(30, 105, SCREEN_WIDTH - 60, SCREEN_HEIGHT - 150)
        frame_bg = pygame.Surface((main_frame.width, main_frame.height), pygame.SRCALPHA)
        frame_bg.fill((20, 30, 45, 200))
        screen.blit(frame_bg, main_frame)
        pygame.draw.rect(screen, (100, 200, 255), main_frame, 3, border_radius=15)
        filter_frame = pygame.Rect(190, 105, 450, 50)
        filter_bg = pygame.Surface((filter_frame.width, filter_frame.height), pygame.SRCALPHA)
        filter_bg.fill((30, 40, 60, 180))
        screen.blit(filter_bg, filter_frame)
        pygame.draw.rect(screen, (100, 200, 255), filter_frame, 2, border_radius=10)

        back_btn.draw(screen)

        for mode_name, btn in mode_buttons.items():
            btn.draw(screen, selected=(mode_name == selected_mode))

        header_y = 160
        headers = ["No", "Player", "Date", "Mode", "Time", "Moves", "Stars"]
        header_x = [40, 120, 280, 380, 500, 600, 700]
        
        for i, header in enumerate(headers):
            text = font_tab.render(header, True, COLOR_TITLE)
            screen.blit(text, (header_x[i], header_y))

        pygame.draw.line(screen, COLOR_SUBTITLE, (40, header_y + 35), 
                        (SCREEN_WIDTH - 40, header_y + 35), 2)

        entry_y = header_y + 50
        for i, score in enumerate(scores[:10]):
            if entry_y > SCREEN_HEIGHT - 50:
                break

            rank_text = font_entry.render(f"{i+1}", True, COLOR_TEXT)
            screen.blit(rank_text, (header_x[0], entry_y))

            player_text = font_entry.render(
                score.get('username', 'Unknown'),
                True,
                COLOR_SUBTITLE
            )
            screen.blit(player_text, (header_x[1], entry_y))

            date_str = score['timestamp'].split()[0]
            date_text = font_entry.render(date_str, True, COLOR_TEXT)
            screen.blit(date_text, (header_x[2], entry_y))

            mode_text = font_entry.render(score['mode'].capitalize(), True, COLOR_TEXT)
            screen.blit(mode_text, (header_x[3], entry_y))

            time_text = font_entry.render(f"{score['time_seconds']}s", True, COLOR_TEXT)
            screen.blit(time_text, (header_x[4], entry_y))

            moves_text = font_entry.render(str(score['moves']), True, COLOR_TEXT)
            screen.blit(moves_text, (header_x[5], entry_y))

            for j in range(score['stars']):
                star_x = header_x[-1] + j * 25
                draw_small_star(screen, star_x, entry_y + 10, 8, COLOR_GOLD)

            entry_y += 35


        if not scores:
            no_scores = font_tab.render("No scores yet. Play to set records!", True, COLOR_SUBTITLE)
            no_scores_rect = no_scores.get_rect(center=(SCREEN_WIDTH // 2, 350))
            screen.blit(no_scores, no_scores_rect)
        
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

def draw_small_star(screen: pygame.Surface, cx: int, cy: int, size: int, color: Tuple) -> None:
    import math
    points = []
    for i in range(10):
        angle = math.pi / 2 + (2 * math.pi * i / 10)
        radius = size if i % 2 == 0 else size * 0.4
        x = cx + radius * math.cos(angle)
        y = cy - radius * math.sin(angle)
        points.append((x, y))
    pygame.draw.polygon(screen, color, points)

def settings_screen(screen: pygame.Surface, bg_image: Optional[pygame.Surface],
                    audio: AudioController, sounds: dict) -> None:
    font_label = pygame.font.SysFont(None, 28)
    font_small = pygame.font.SysFont(None, 24)
    
    back_btn = Button(30, 30, 100, 40, "Back", font_small)

    music_slider = Slider(200, 230, 350, 0, 1, audio.music_volume, "Music Volume")
    sfx_slider = Slider(200, 300, 350, 0, 1, audio.sfx_volume, "Sound Effects Volume")
    
    music_toggle = Button(200, 360, 200, 45, 
                         "Music: ON" if audio.music_enabled else "Music: OFF", font_label)
    sfx_toggle = Button(420, 360, 200, 45,
                       "SFX: ON" if audio.sfx_enabled else "SFX: OFF", font_label)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.is_clicked(mouse_pos):
                    return
                if music_toggle.is_clicked(mouse_pos):
                    audio.toggle_music()
                    music_toggle.text = "Music: ON" if audio.music_enabled else "Music: OFF"
                if sfx_toggle.is_clicked(mouse_pos):
                    audio.toggle_sfx()
                    sfx_toggle.text = "SFX: ON" if audio.sfx_enabled else "SFX: OFF"

            if music_slider.handle_event(event):
                audio.set_music_volume(music_slider.value)
            if sfx_slider.handle_event(event):
                audio.set_sfx_volume(sfx_slider.value)

        back_btn.update_hover(mouse_pos)
        music_toggle.update_hover(mouse_pos)
        sfx_toggle.update_hover(mouse_pos)

        draw_background(screen, bg_image)
        draw_title(screen, "", y=100)

        back_btn.draw(screen)

        music_slider.draw(screen, font_label)
        sfx_slider.draw(screen, font_label)

        music_toggle.draw(screen)
        sfx_toggle.draw(screen)
        
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

def login_screen(screen: pygame.Surface, bg_image: Optional[pygame.Surface],
                 audio: AudioController, sounds: dict) -> Optional[str]:
    font_title = pygame.font.SysFont(None, 50)
    font_btn = pygame.font.SysFont(None, 32)
    font_input = pygame.font.SysFont(None, 28)
    font_small = pygame.font.SysFont(None, 24)
    font_error = pygame.font.SysFont(None, 22)
    
    input_box = InputBox(250, 210, 300, 45, font_input, "Enter username...")
    
    login_btn = Button(250, 280, 140, 45, "Login", font_btn)
    register_btn = Button(410, 280, 140, 45, "Register", font_btn)
    back_btn = Button(30, 30, 100, 40, "Back", font_small)
    
    error_msg = ""
    error_time = 0
    
    while True:
        current_time = time.time()
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.is_clicked(mouse_pos):
                    return None
                
                if login_btn.is_clicked(mouse_pos):
                    username = input_box.text.strip()
                    if not username:
                        error_msg = "Please enter a username!"
                        error_time = current_time
                    elif not user_exists(username):
                        error_msg = "User not found! Please register first."
                        error_time = current_time
                    else:
                        return username
                
                if register_btn.is_clicked(mouse_pos):
                    username = input_box.text.strip()
                    if not username:
                        error_msg = "Please enter a username!"
                        error_time = current_time
                    elif len(username) < 3:
                        error_msg = "Username must be at least 3 characters!"
                        error_time = current_time
                    elif user_exists(username):
                        error_msg = "Username already exists! Please login."
                        error_time = current_time
                    else:
                        if save_user(username):
                            return username
                        else:
                            error_msg = "Error saving user. Please try again."
                            error_time = current_time
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    username = input_box.text.strip()
                    if username and user_exists(username):
                        return username
            
            input_box.handle_event(event)

        input_box.update()
        back_btn.update_hover(mouse_pos)
        login_btn.update_hover(mouse_pos)
        register_btn.update_hover(mouse_pos)

        draw_background(screen, bg_image)

        frame_rect = pygame.Rect(200, 180, 400, 200)
        pygame.draw.rect(screen, (40, 40, 60), frame_rect, border_radius=15)
        pygame.draw.rect(screen, (100, 200, 255), frame_rect, 3, border_radius=15)
        
        draw_title(screen, "LOGIN / REGISTER", y=140)
        
        back_btn.draw(screen)
        input_box.draw(screen)
        login_btn.draw(screen)
        register_btn.draw(screen)
        
        if error_msg and current_time - error_time < 3:
            error_surf = font_error.render(error_msg, True, COLOR_ERROR)
            error_rect = error_surf.get_rect(center=(SCREEN_WIDTH // 2, 375))
            screen.blit(error_surf, error_rect)
        
        
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)



def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Memory Match")
    
    init_csv()
    audio = AudioController()
    sounds = load_sound_effects()
    
    menu_bg = load_menu_background()
    difficulty_bg = load_difficulty_background()
    theme_bg = load_theme_background()
    leaderboard_bg = load_leaderboard_background()
    settings_bg = load_settings_background()
    nightmare_menu_bg = load_menu_background("nightmare")
    nightmare_leaderboard_bg = leaderboard_bg

    menu_music = load_menu_music()
    audio.play_music(menu_music, volume=0.3)
    
    game = None
    clock = pygame.time.Clock()
    current_username = None
    
    while True:
        action = start_menu(screen, menu_bg, audio, sounds)
        
        if action == 'quit':
            break
        elif action == 'leaderboard':
            leaderboard_screen(screen, leaderboard_bg, audio, sounds)
            continue
        elif action == 'settings':
            settings_screen(screen, settings_bg, audio, sounds)
            continue
        elif action != 'start':
            continue

        username = login_screen(screen, menu_bg, audio, sounds)
        if username is None:
            continue
        
        current_username = username

        mode_choice = mode_selection_menu(screen, difficulty_bg, audio, sounds)
        
        if mode_choice == 'back' or mode_choice is None:
            continue

        if mode_choice == 'normal':
            while True:
                mode = difficulty_menu(screen, difficulty_bg, audio, sounds)
                if mode == 'back':
                    break
                elif mode is None:
                    pygame.quit()
                    sys.exit()
                elif mode in MODE_LIST:
                    theme = theme_menu(screen, mode, theme_bg, audio, sounds)
                    if theme == -1:
                        continue
                    elif theme is None:
                        pygame.quit()
                        sys.exit()
                    else:
                        game = Game(screen, mode, theme, audio, sounds, current_username)

                        running = True
                        while running:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                elif event.type == pygame.MOUSEBUTTONDOWN:
                                    if game.paused:
                                        action = game.handle_pause_click(event.pos)
                                        if action == 'restart':
                                            game = Game(screen, mode, theme, audio, sounds, current_username)
                                        elif action == 'settings':
                                            settings_screen(screen, settings_bg, audio, sounds)
                                            if not game.end_time:
                                                game_music = load_game_music(mode, theme)
                                                audio.play_music(game_music)
                                        elif action == 'menu':
                                            audio.play_music(menu_music, volume=0.3)
                                            running = False
                                    else:
                                        game.click(event.pos)
                                elif event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_ESCAPE:
                                        game.toggle_pause()
                                    elif event.key == pygame.K_r and game.end_time:
                                        game = Game(screen, mode, theme, audio, sounds, current_username)
                                    elif event.key == pygame.K_m and game.end_time:
                                        audio.play_music(menu_music, volume=0.3)
                                        running = False
                            
                            game.update()
                            game.draw()
                            
                            pygame.display.flip()
                            clock.tick(FPS)
                        
                        break
                
                if not running:
                    break

        elif mode_choice == 'nightmare':
            while True:
                nightmare_action = nightmare_menu(screen, nightmare_menu_bg, audio, sounds)
                
                if nightmare_action == 'back' or nightmare_action == 'quit':
                    break
                elif nightmare_action == 'leaderboard':
                    nightmare_leaderboard(screen, nightmare_leaderboard_bg, audio, sounds)
                elif nightmare_action == 'settings':
                    settings_screen(screen, settings_bg, audio, sounds)
                elif nightmare_action == 'start':
                    mode = 'nightmare'
                    theme = 1
                    
                    game = Game(screen, mode, theme, audio, sounds, current_username)
                    
                    running = True
                    while running:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif event.type == pygame.MOUSEBUTTONDOWN:
                                if game.paused:
                                    action = game.handle_pause_click(event.pos)
                                    if action == 'restart':
                                        game = Game(screen, mode, theme, audio, sounds, current_username)
                                    elif action == 'settings':
                                        settings_screen(screen, settings_bg, audio, sounds)
                                        if not game.end_time:
                                            game_music = load_game_music(mode, theme)
                                            audio.play_music(game_music)
                                    elif action == 'menu':
                                        audio.play_music(menu_music, volume=0.3)
                                        running = False
                                else:
                                    game.click(event.pos)
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                    game.toggle_pause()
                                elif event.key == pygame.K_r and game.end_time:
                                    game = Game(screen, mode, theme, audio, sounds, current_username)
                                elif event.key == pygame.K_m and game.end_time:
                                    audio.play_music(menu_music, volume=0.3)
                                    running = False
                        
                        game.update()
                        game.draw()
                        
                        pygame.display.flip()
                        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()