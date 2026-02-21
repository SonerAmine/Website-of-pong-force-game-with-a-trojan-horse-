# ===== PONG FORCE - GAME CONFIGURATION =====

import os

# ===== WINDOW SETTINGS =====
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
FPS = 60
TITLE = "Pong Force"

# ===== COLORS (Neon Arcade Theme) =====
BLACK = (11, 12, 16)          # Background
WHITE = (255, 255, 255)       # Text
NEON_BLUE = (0, 255, 255)     # Player 1, UI elements
NEON_PINK = (255, 0, 204)     # Player 2, Force effects
NEON_YELLOW = (255, 215, 0)   # Ball, highlights
NEON_GREEN = (0, 255, 128)     # Success indicators, positive stats
GRAY = (128, 128, 128)        # Secondary text
DARK_GRAY = (64, 64, 64)      # Borders

# ===== GAME PHYSICS =====
PADDLE_SPEED = 24              # Vitesse x3 (était 8)
BALL_SPEED = 6                 # Much slower initial speed for better tracking
BALL_SPEED_INCREASE = 0.3      # Speed increase per hit (augmenté)
MAX_BALL_SPEED = 45            # Max speed x3 (était 15)

# ===== FORCE PUSH SYSTEM =====
FORCE_MULTIPLIER = 2.5        # Speed multiplier when force push is used (2.5x for significant increase)
FORCE_COOLDOWN = 75           # 75 seconds to charge force push bar
FORCE_METER_FILL_RATE = 1/75   # How fast meter fills (full in 75 seconds)
FORCE_STUN_DURATION = 0.5     # Seconds of stun if force push fails
FORCE_EFFECT_DURATION = 1.0   # How long the force effect lasts
FORCE_DASH_DISTANCE = 80      # Distance paddle moves when using force
FORCE_DASH_DURATION = 0.3     # Duration of dash movement

# ===== PADDLE SETTINGS =====
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
PADDLE_MARGIN = 20

# ===== BALL SETTINGS =====
BALL_SIZE = 12
BALL_TRAIL_LENGTH = 10

# ===== SCORING =====
WIN_SCORE = 10
SCORE_DISPLAY_SIZE = 48

# ===== NETWORKING =====
SERVER_PORT = 5555
SERVER_IP = "0.0.0.0"  # Listen on all network interfaces (for internet play)
BUFFER_SIZE = 1024
NETWORK_UPDATE_RATE = 60  # Updates per second

# ===== MATCHMAKING SERVER =====
# URL du serveur de matchmaking central

MATCHMAKING_SERVER_URL = "https://pong-force-matchmaking.onrender.com"

# Paramètres de connexion
CONNECTION_TIMEOUT = 15  # Secondes
MATCHMAKING_TIMEOUT = 20  # Secondes
MAX_CONNECTION_RETRIES = 3

# ===== UI SETTINGS =====
UI_MARGIN = 20
FORCE_METER_WIDTH = 200
FORCE_METER_HEIGHT = 20
FORCE_METER_Y_OFFSET = 50

# ===== EFFECTS =====
PARTICLE_COUNT = 20
PARTICLE_LIFE = 30
FORCE_GLOW_SIZE = 50
TRAIL_ALPHA_DECAY = 0.1

# ===== SOUND SETTINGS =====
SOUND_VOLUME = 0.7
MUSIC_VOLUME = 0.3

# ===== PATHS =====
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")

# ===== FONT SETTINGS =====
FONT_SIZE_LARGE = 48
FONT_SIZE_MEDIUM = 24
FONT_SIZE_SMALL = 16

# ===== GAME STATES =====
STATE_MENU = "menu"
STATE_CONNECTING = "connecting"
STATE_WAITING = "waiting"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"

# ===== INPUT KEYS =====
# Player 1 controls (vs Robot and 2-Player)
P1_UP = "up"
P1_DOWN = "down"
P1_FORCE = "space"

# Player 2 controls (vs Robot)
P2_ROBOT_UP = "w"
P2_ROBOT_DOWN = "s"
P2_ROBOT_FORCE = "shift"

# Player 2 controls (2-Player Local)
P2_LOCAL_UP = "z"
P2_LOCAL_DOWN = "s"
P2_LOCAL_FORCE = "a"

# General controls
PAUSE_KEY = "escape"
RESTART_KEY = "r"

# ===== NETWORK MESSAGE TYPES =====
MSG_CONNECT = "connect"
MSG_DISCONNECT = "disconnect"
MSG_INPUT = "input"
MSG_GAME_STATE = "game_state"
MSG_SCORE = "score"
MSG_FORCE_PUSH = "force_push"
MSG_PAUSE = "pause"
MSG_RESTART = "restart"

# ===== DEBUG SETTINGS =====
DEBUG_MODE = False
SHOW_FPS = True
SHOW_NETWORK_STATS = False
SHOW_COLLISION_BOXES = False

# ===== PERFORMANCE SETTINGS =====
MAX_PARTICLES = 100
PARTICLE_CLEANUP_INTERVAL = 60  # frames
MEMORY_CLEANUP_INTERVAL = 300   # frames

# ===== GAME BALANCE =====
# Force push timing window (how close to ball you need to be)
FORCE_HIT_RANGE = 300  # Augmenté pour permettre d'utiliser la Force plus facilement
# Ball speed reduction over time
BALL_SPEED_DECAY = 0.99
# Minimum ball speed
MIN_BALL_SPEED = 3
# Maximum angle change on paddle hit
MAX_ANGLE_CHANGE = 45

# ===== VISUAL EFFECTS =====
SCREEN_SHAKE_INTENSITY = 5
SCREEN_SHAKE_DURATION = 10
GLOW_INTENSITY = 2.0
TRAIL_FADE_SPEED = 0.05

# ===== AUDIO SETTINGS =====
AUDIO_FREQUENCY = 22050
AUDIO_SIZE = -16
AUDIO_CHANNELS = 2
AUDIO_BUFFER = 1024

# ===== DEVELOPMENT SETTINGS =====
DEVELOPMENT_MODE = True
AUTO_RESTART_ON_ERROR = True
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# ===== EXPORT SETTINGS =====
# For PyInstaller
ICON_PATH = os.path.join(IMAGES_DIR, "icon.ico")
VERSION = "1.0.0"
COMPANY = "Pong Force Studios"
PRODUCT = "Pong Force"
DESCRIPTION = "Revolutionary Pong with Force Push mechanics"
