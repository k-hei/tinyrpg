import pygame

key_times = {}
inited = False

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

def handle_keydown(key):
  if not inited: init()
  if key not in key_times or key_times[key] == 0:
    key_times[key] = 1

def handle_keyup(key):
  if not inited: init()
  key_times[key] = 0

def get_pressed(key):
  if key not in key_times:
    return 0
  return key_times[key]
