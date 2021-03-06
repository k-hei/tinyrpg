DEBUG = True
DEBUG_GEN = False
CUTSCENES = True

# feature flags
ENABLED_MINIMAP = True

# dungeon generation
SEED = None
TOP_FLOOR = 3
MAX_LOOPS = 0
MAX_ROOM_FAILS = 3
FLOOR_SIZE = (27, 27)
ROOM_WIDTHS = (3, 5, 7, 9)
ROOM_HEIGHTS = (4, 7, 10)

# game settings
FPS = 60
FPS_FAST = 120
FPS_SLOW = 15
MAX_SP = 40
INVENTORY_COLS = 2
INVENTORY_ROWS = 4
VISION_RANGE = 3.5
TILE_SIZE = 32
DEPTH_SIZE = TILE_SIZE * 2
ITEM_OFFSET = 16
WINDOW_WIDTH = 384
WINDOW_HEIGHT = 216
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
WINDOW_SCALE_INIT = 2
WINDOW_SCALE_MAX = 6

# defaults
KNIGHT_NAME = "Yorgen"
KNIGHT_HP = 23
KNIGHT_BUILD = {
    "Stick": (0, 0),
    "Blitzritter": (1, 0)
}

MAGE_NAME = "Minxia"
MAGE_HP = 17
MAGE_BUILD = {}

ROGUE_NAME = "Fray"
ROGUE_HP = 19
ROGUE_BUILD = {}

HUSBAND_NAME = "Thag"
WIFE_NAME = "Sylvia"
ORACLE_NAME = "Mira"
BUNNY_NAME = "Bunji"
BOAR_NAME = "Grink"
MOUSE_NAME = "Rossoh"

# generic animations
WALK_DURATION = 16
MOVE_DURATION = WALK_DURATION
RUN_DURATION = 12
JUMP_DURATION = 12
ATTACK_DURATION = 12
NUDGE_DURATION = 8
FLICKER_DURATION = 45
FLINCH_DURATION = 25
FLINCH_PAUSE_DURATION = 15
SIDESTEP_DURATION = 20
SIDESTEP_AMPLITUDE = 8
PUSH_DURATION = 45

# combat
MISS_CHANCE = 1 / 8
CRIT_CHANCE = 1 / 64
CRIT_MODIFIER = 1.33

# misc
LABEL_FRAMES = 120
COMBAT_THRESHOLD = 112
ENABLED_COMBAT_LOG = False
SKILL_BADGE_POS_SOLO = (46, 42)
SKILL_BADGE_POS_ALLY = (60, 54)



import sys
import os
from os.path import abspath, dirname, join


def resolve_path(*args):
    return join(dirname(__file__), *args)    


ROOT_PATH = resolve_path()
ASSETS_PATH = resolve_path("assets")
ROOMS_PATH = resolve_path("rooms")
SAVEDATA_PATH = resolve_path("src")
LOCATIONS_PATH = resolve_path("src", "locations")
