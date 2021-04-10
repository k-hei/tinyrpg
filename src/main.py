import math
import pygame
from pygame import Surface
from game import Game

TILE_SIZE = 32
WINDOW_SIZE = (9 * TILE_SIZE, 9 * TILE_SIZE)
WINDOW_SCALE = 2
(WINDOW_WIDTH, WINDOW_HEIGHT) = WINDOW_SIZE
WINDOW_SIZE_SCALED = (WINDOW_WIDTH * WINDOW_SCALE, WINDOW_HEIGHT * WINDOW_SCALE)
WINDOW_FLAGS = 0

def init_display(window_title: str, window_size: (int, int)) -> Surface:
  pygame.display.init()
  pygame.display.set_caption(window_title)
  return pygame.display.set_mode(window_size, WINDOW_FLAGS)

display = init_display("hello", WINDOW_SIZE_SCALED)
surface = Surface(WINDOW_SIZE)

# asset loading
sprite_hero = pygame.image.load("assets/hero.png").convert_alpha()
sprite_mage = pygame.image.load("assets/mage.png").convert_alpha()
sprite_bat = pygame.image.load("assets/bat.png").convert_alpha()
sprite_rat = pygame.image.load("assets/rat.png").convert_alpha()
sprite_wall = pygame.image.load("assets/wall.png").convert_alpha()
sprite_wall_base = pygame.image.load("assets/wall-base.png").convert_alpha()
sprite_chest = pygame.image.load("assets/chest.png").convert_alpha()
sprite_stairs = pygame.image.load("assets/downstairs.png").convert_alpha()
sprite_eye = pygame.image.load("assets/eye.png").convert_alpha()

def lerp(a, b, t):
  return a * (1 - t) + b * t

game = Game()

def handle_key(game, key):
  delta_x = 0
  delta_y = 0
  if key == pygame.K_LEFT:
    delta_x = -1
  elif key == pygame.K_RIGHT:
    delta_x = 1
  elif key == pygame.K_UP:
    delta_y = -1
  elif key == pygame.K_DOWN:
    delta_y = 1

  if delta_x != 0 or delta_y != 0:
    game.move((delta_x, delta_y))

def render_game(surface, game):
  (window_width, window_height) = WINDOW_SIZE
  (hero_x, hero_y) = game.p1.cell
  for anim in game.anims:
    if anim.data["target"] == game.p1:
      (from_x, from_y) = anim.data["from"]
      (to_x, to_y) = anim.data["to"]
      t = (anim.time + 1) / anim.duration
      hero_x = lerp(from_x, to_x, t)
      hero_y = lerp(from_y, to_y, t)

  camera_x = -math.floor((hero_x + 0.5) * TILE_SIZE - window_width / 2)
  camera_y = -math.floor((hero_y + 0.5) * TILE_SIZE - window_height / 2)

  (stage_width, stage_height) = game.stage.size
  surface.fill((0, 0, 0))
  for y in range(stage_height):
    for x in range(stage_width):
      tile = game.stage.get_at((x, y))
      sprite = None
      if tile == 1:
        if game.stage.get_at((x, y + 1)) == 0:
          sprite = sprite_wall_base
        else:
          sprite = sprite_wall
      elif tile == 2:
        sprite = sprite_stairs
      if sprite:
        surface.blit(sprite, (x * TILE_SIZE + camera_x, y * TILE_SIZE + camera_y))

  # depth sorting
  game.stage.actors.sort(key=lambda actor: actor.cell[1])

  for actor in game.stage.actors:
    (col, row) = actor.cell
    if actor.kind == "hero":
      sprite = sprite_hero
    elif actor.kind == "mage":
      sprite = sprite_mage
    elif actor.kind == "bat":
      sprite = sprite_bat
    elif actor.kind == "rat":
      sprite = sprite_rat
    elif actor.kind == "chest":
      sprite = sprite_chest
    elif actor.kind == "eye":
      sprite = sprite_eye

    anim = None
    for anim in game.anims:
      if anim.data["target"] == actor:
        (from_x, from_y) = anim.data["from"]
        (to_x, to_y) = anim.data["to"]
        t = anim.update()
        col = lerp(from_x, to_x, t)
        row = lerp(from_y, to_y, t)
        if anim.done:
          game.anims.remove(anim)
        break

    surface.blit(sprite, (col * TILE_SIZE + camera_x, row * TILE_SIZE + camera_y))


def render_display():
  render_game(surface, game)
  display.blit(pygame.transform.scale(surface, WINDOW_SIZE_SCALED), (0, 0))
  pygame.display.flip()

done = False
clock = pygame.time.Clock()
while not done:
  ms = clock.tick(60)
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      done = True
      break
    elif event.type == pygame.KEYDOWN:
      handle_key(game, event.key)
      break
  render_display()
