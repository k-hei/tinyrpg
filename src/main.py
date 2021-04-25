import math
import pygame
from pygame import Surface

import config
import assets
import keyboard
from contexts.game import GameContext
from contexts.dungeon import DungeonContext

WINDOW_TITLE = "tinyrpg"
WINDOW_SIZE = (config.window_width, config.window_height)
window_scale = config.SCALE_INIT
fullscreen = False

pygame.display.init()
pygame.display.set_caption(WINDOW_TITLE)
display = None
window_size_scaled = None

def resize(new_scale):
  if new_scale < 1 or new_scale > config.SCALE_MAX:
    return False
  global window_scale, window_size_scaled, display
  window_scale = new_scale
  new_width = config.window_width * new_scale
  new_height = config.window_height * new_scale
  window_size_scaled = (new_width, new_height)
  display = pygame.display.set_mode(window_size_scaled)
  return True

def toggle_fullscreen():
  global display, fullscreen
  fullscreen = not fullscreen
  if fullscreen:
    display = pygame.display.set_mode(window_size_scaled, pygame.FULLSCREEN)
  else:
    display = pygame.display.set_mode(window_size_scaled)

resize(window_scale)
surface = Surface(WINDOW_SIZE)
pygame.key.set_repeat(1000 // config.fps)

assets.load()
keyboard.init()

game_ctx = GameContext()
game_ctx.child = DungeonContext(parent=game_ctx)

def handle_keydown(key):
  keyboard.handle_keydown(key)
  tapping = keyboard.get_pressed(key) == 1
  ctrl = (keyboard.get_pressed(pygame.K_LCTRL)
      or keyboard.get_pressed(pygame.K_RCTRL))
  if key == pygame.K_MINUS and ctrl and tapping:
    resize(window_scale - 1)
  elif key == pygame.K_EQUALS and ctrl and tapping:
    resize(window_scale + 1)
  elif key == pygame.K_f and ctrl and tapping:
    toggle_fullscreen()
  else:
    game_ctx.handle_keydown(key)

def handle_keyup(key):
  keyboard.handle_keyup(key)
  game_ctx.handle_keyup(key)

def render():
  game_ctx.draw(surface)
  display.blit(pygame.transform.scale(surface, window_size_scaled), (0, 0))
  pygame.display.flip()

done = False
clock = pygame.time.Clock()
while not done:
  ms = clock.tick(config.fps)
  keyboard.update()
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      done = True
      break
    elif event.type == pygame.KEYDOWN:
      handle_keydown(event.key)
    elif event.type == pygame.KEYUP:
      handle_keyup(event.key)
  render()
