import pygame

key_times = {}
inited = False

ARROW_DELTAS = {
  pygame.K_LEFT: (-1, 0),
  pygame.K_RIGHT: (1, 0),
  pygame.K_UP: (0, -1),
  pygame.K_DOWN: (0, 1),
  pygame.K_a: (-1, 0),
  pygame.K_d: (1, 0),
  pygame.K_w: (0, -1),
  pygame.K_s: (0, 1),
  "left": (-1, 0),
  "right": (1, 0),
  "up": (0, -1),
  "down": (0, 1),
}

def init():
  global inited
  inited = True
  keys = pygame.key.get_pressed()
  for i in range(len(keys)):
    key_times[i] = 0

def update():
  for key in key_times:
    if key_times[key] > 0:
      key_times[key] += 1

def handle_press(key):
  if not inited: init()
  if key not in key_times or key_times[key] == 0:
    key_times[key] = 1

def handle_release(key):
  if not inited: init()
  key_times[key] = 0

def get_state(key):
  if key not in key_times:
    return 0
  return key_times[key]
