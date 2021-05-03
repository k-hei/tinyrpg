import math
import pygame
from pygame import Surface

import config
import assets
import keyboard
from contexts.game import GameContext

WINDOW_TITLE = "tinyrpg"
WINDOW_SIZE = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
window_scale = config.SCALE_INIT
fullscreen = False

pygame.init()
pygame.display.set_caption(WINDOW_TITLE)
display = None
window_size_scaled = None
game = None

def resize(new_scale):
  if new_scale < 1 or new_scale > config.SCALE_MAX:
    return False
  global window_scale, window_size_scaled, display
  window_scale = new_scale
  new_width = config.WINDOW_WIDTH * new_scale
  new_height = config.WINDOW_HEIGHT * new_scale
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

def new_game():
  global game
  game = GameContext()
  game.goto_town()

resize(window_scale)
surface = Surface(WINDOW_SIZE)
pygame.key.set_repeat(1000 // config.FPS)
assets.load()
keyboard.init()
new_game()

def handle_keydown(key):
  keyboard.handle_keydown(key)
  tapping = keyboard.get_pressed(key) == 1
  ctrl = tapping and (keyboard.get_pressed(pygame.K_LCTRL)
      or keyboard.get_pressed(pygame.K_RCTRL))
  shift = tapping and (keyboard.get_pressed(pygame.K_LSHIFT)
      or keyboard.get_pressed(pygame.K_RSHIFT))
  if key == pygame.K_MINUS and ctrl:
    resize(window_scale - 1)
  elif key == pygame.K_EQUALS and ctrl:
    resize(window_scale + 1)
  elif key == pygame.K_f and ctrl:
    toggle_fullscreen()
  elif key == pygame.K_r and ctrl and shift:
    new_game()
  elif key == pygame.K_r and ctrl:
    game.reset()
  else:
    game.handle_keydown(key)

def handle_keyup(key):
  keyboard.handle_keyup(key)
  game.handle_keyup(key)

def render():
  game.draw(surface)
  display.blit(pygame.transform.scale(surface, window_size_scaled), (0, 0))
  pygame.display.flip()

done = False
clock = pygame.time.Clock()
while not done:
  ms = clock.tick(config.FPS)
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
