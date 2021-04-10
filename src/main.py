import pygame
from pygame import Surface
from grid import Grid
import gen

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
sprite_hero = pygame.image.load("assets/hero.png").convert_alpha()
sprite_mage = pygame.image.load("assets/mage.png").convert_alpha()
sprite_bat = pygame.image.load("assets/bat.png").convert_alpha()
sprite_rat = pygame.image.load("assets/rat.png").convert_alpha()
sprite_wall = pygame.image.load("assets/wall.png").convert_alpha()
sprite_wall_base = pygame.image.load("assets/wall-base.png").convert_alpha()
sprite_chest = pygame.image.load("assets/chest.png").convert_alpha()

def lerp(a, b, t):
  return a * (1 - t) + b * t

class Actor:
  def __init__(actor, kind, cell):
    actor.kind = kind
    actor.cell = cell

class Anim:
  def __init__(anim, duration, data):
    anim.done = False
    anim.time = 0
    anim.duration = duration
    anim.data = data
  def update(anim):
    if anim.done:
      return -1
    anim.time += 1
    if anim.time == anim.duration:
      anim.done = True
    return anim.time / anim.duration

class Game:
  def __init__(game):
    game.grid = gen.maze(15, 15)
    game.p1 = Actor("hero", (3, 3))
    game.p2 = Actor("mage", (3, 4))
    game.anims = []
    game.actors = [
      game.p1,
      game.p2,
      Actor("bat", (5, 7)),
      Actor("rat", (3, 5)),
      Actor("chest", (1, 1))
    ]
  def get_actor_at(game, cell):
    for actor in game.actors:
      if actor.cell[0] == cell[0] and actor.cell[1] == cell[1]:
        return actor
    return None
  def move(game, delta):
    old_cell = game.p1.cell
    (hero_x, hero_y) = old_cell
    (delta_x, delta_y) = delta
    new_cell = (hero_x + delta_x, hero_y + delta_y)
    target = game.get_actor_at(new_cell)
    if game.grid.get_at(new_cell) == 0 and (target == None or target == game.p2):
      game.anims.append(Anim(6, {
        "target": game.p1,
        "from": old_cell,
        "to": new_cell
      }))
      game.anims.append(Anim(6, {
        "target": game.p2,
        "from": game.p2.cell,
        "to": old_cell
      }))
      game.p2.cell = old_cell
      game.p1.cell = new_cell
      return True
    elif target is not None:
      game.actors.remove(target)
      return False
    else:
      return False

game = Game()

def handle_key(game, key):
  delta_x = 0
  delta_y = 0
  if key == pygame.K_LEFT:
    delta_x = -1
  elif key == pygame.K_RIGHT:
    delta_x = 1
  if key == pygame.K_UP:
    delta_y = -1
  elif key == pygame.K_DOWN:
    delta_y = 1
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

  camera_x = -((hero_x + 0.5) * TILE_SIZE - window_width / 2)
  camera_y = -((hero_y + 0.5) * TILE_SIZE - window_height / 2)

  (grid_width, grid_height) = game.grid.size
  surface.fill((0, 0, 0))
  for y in range(grid_height):
    for x in range(grid_width):
      if game.grid.get_at((x, y)) == 1:
        if game.grid.get_at((x, y + 1)) == 0:
          sprite = sprite_wall_base
        else:
          sprite = sprite_wall
        surface.blit(sprite, (x * TILE_SIZE + camera_x, y * TILE_SIZE + camera_y))

  # depth sorting
  game.actors.sort(key=lambda actor: actor.cell[1])

  for actor in game.actors:
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
