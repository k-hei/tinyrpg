WHITE = 0xFFFFFFFF
BLACK = 0xFF000000
RED = 0xFFE64646
RED_DARK = 0xFF951F45
PURPLE = 0xFF8F3ECA
PURPLE_DARK = 0xFF4B238A
YELLOW = 0xFFFBF236
YELLOW_DARK = 0xFFBA9335
GREEN = 0xFF2EC169
GREEN_DARK = 0xFF25755F
GRAY = 0xFF7B748A
GRAY_DARK = 0xFF5A555C
BLUE = 0xFF3C59E3
BLUE_DARK = 0xFF3D35AF
CYAN = 0xFF64ABFF
GOLD = 0xFFFCBC82
GOLD_DARK = 0xFF53324F
PINK = 0xFFDB4EDF
PINK_DARK = 0xFF761BA6
SAFFRON = 0xFFA97352
ORANGE = 0xFFF99F4C

COLOR_TILE = SAFFRON

def darken_color(color):
  if color == WHITE: return GRAY
  elif color == RED: return RED_DARK
  elif color == PURPLE: return PURPLE_DARK
  elif color == YELLOW: return YELLOW_DARK
  elif color == GOLD: return GOLD_DARK
  elif color == SAFFRON: return GOLD_DARK
  elif color == GREEN: return GREEN_DARK
  elif color == GRAY: return GRAY_DARK
  elif color == BLUE: return BLUE_DARK
  elif color == PINK: return PINK_DARK
  return color
