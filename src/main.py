import math
import pygame
from pygame import Surface

import config
import assets
import keyboard
from contexts.game import GameContext
from contexts.dungeon import DungeonContext

WINDOW_TITLE = "hello"
WINDOW_SIZE = (config.window_width, config.window_height)
WINDOW_SIZE_SCALED = (
  config.window_width * config.window_scale,
  config.window_height * config.window_scale
)

pygame.display.init()
pygame.display.set_caption("hello")
display = pygame.display.set_mode(WINDOW_SIZE_SCALED)
surface = Surface(WINDOW_SIZE)
pygame.key.set_repeat(1000 // config.fps)

assets.load()
keyboard.init()

game_ctx = GameContext()
game_ctx.child = DungeonContext(parent=game_ctx)

def handle_keydown(key):
  keyboard.handle_keydown(key)
  game_ctx.handle_keydown(key)

def handle_keyup(key):
  keyboard.handle_keyup(key)
  game_ctx.handle_keyup(key)

def render():
  game_ctx.draw(surface)
  display.blit(pygame.transform.scale(surface, WINDOW_SIZE_SCALED), (0, 0))
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
