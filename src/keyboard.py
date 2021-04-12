import pygame

key_times = {}
inited = False

def init():
  global inited
  inited = True
  keys = pygame.key.get_pressed()
  for key in keys:
    key_times[key] = 0


def update():
  for key in key_times:
    key_times[key] += 1

def handle_keydown(key):
  if not inited: init()
  key_times[key] = 1

def handle_keyup(key):
  if not inited: init()
  key_times[key] = 0
