import pygame

state = {}
inited = False

def init():
  global inited
  inited = True
  keys = pygame.key.get_pressed()
  for key in keys:
    state[key] = 0

def update():
  for key in state:
    state[key] += 1

def handle_keydown(key):
  if not inited: init()
  state[key] = 1

def handle_keyup(key):
  if not inited: init()
  state[key] = 0
