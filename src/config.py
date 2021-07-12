# dungeon generation
SEED = None
DEBUG = False
CUTSCENES = True
TOP_FLOOR = 3
MAX_LOOPS = 0
MAX_ROOM_FAILS = 3
FLOOR_SIZE = (27, 27)
ROOM_WIDTHS = (3, 5, 7)
ROOM_HEIGHTS = (4, 7)

# game settings
FPS = 60
FPS_SLOW = 15
VISION_RANGE = 3.5
TILE_SIZE = 32
ITEM_OFFSET = 20
WINDOW_WIDTH = 256
WINDOW_HEIGHT = 224
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
WINDOW_SCALE_INIT = 2
WINDOW_SCALE_MAX = 6
ASSETS_PATH = "assets/"

# defaults
KNIGHT_NAME = "Yorgen"
KNIGHT_HP = 23
KNIGHT_BUILD = {
  "Stick": (0, 0),
  "Blitzritter": (1, 0)
}

MAGE_NAME = "Minxia"
MAGE_HP = 16
MAGE_BUILD = {
  "Ignis": (1, 0),
  "Somnus": (0, 0)
}

ROGUE_NAME = "Fray"
ROGUE_HP = 19
ROGUE_BUILD = {}

# animations
WALK_DURATION = 16
MOVE_DURATION = WALK_DURATION
RUN_DURATION = 12
JUMP_DURATION = 12
ATTACK_DURATION = 12
FLICKER_DURATION = 75
