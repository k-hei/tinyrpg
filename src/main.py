import pygame
from pygame import Surface

TILE_SIZE = 16
WINDOW_SIZE = (9 * 16, 9 * 16)
WINDOW_SCALE = 3
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

class Actor:
  def __init__(actor, kind, cell):
    actor.kind = kind
    actor.cell = cell

class Grid:
  def __init__(grid):
    grid.size = (9, 9)
    grid.data = [
      1, 1, 1, 1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1, 1, 1, 1,
      1, 0, 0, 0, 0, 0, 0, 0, 1,
      1, 0, 0, 0, 0, 0, 1, 0, 1,
      1, 0, 0, 0, 0, 0, 1, 0, 1,
      1, 0, 0, 0, 0, 0, 0, 0, 1,
      1, 0, 0, 0, 0, 0, 0, 0, 1,
      1, 0, 0, 0, 0, 0, 0, 0, 1,
      1, 1, 1, 1, 1, 1, 1, 1, 1,
    ]
  def get_at(grid, cell):
    width = grid.size[0]
    (x, y) = cell
    if not grid.contains(cell):
      return None
    return grid.data[y * width + x]
  def contains(grid, cell):
    (width, height) = grid.size
    (x, y) = cell
    return x >= 0 and y >= 0 and x < width and y < height

class Game:
  def __init__(game):
    game.grid = Grid()
    game.p1 = Actor("hero", (4, 4))
    game.p2 = Actor("mage", (3, 4))
    game.actors = [game.p1, game.p2, Actor("bat", (5, 6)), Actor("rat", (2, 5))]
  def move(game, delta):
    (hero_x, hero_y) = game.p1.cell
    (delta_x, delta_y) = delta
    new_cell = (hero_x + delta_x, hero_y + delta_y)
    if game.grid.get_at(new_cell) == 0:
      game.p2.cell = game.p1.cell
      game.p1.cell = new_cell
      return True
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
  (grid_width, grid_height) = game.grid.size
  surface.fill((0, 0, 0))
  for y in range(grid_height):
    for x in range(grid_width):
      if game.grid.get_at((x, y)) == 1:
        if game.grid.get_at((x, y + 1)) == 0:
          sprite = sprite_wall_base
        else:
          sprite = sprite_wall
        surface.blit(sprite, (x * TILE_SIZE, y * TILE_SIZE))

  game.actors.sort(key=lambda actor: actor.cell[1])
  for actor in game.actors:
    (col, row) = actor.cell
    if actor.kind == "hero":
      sprite = sprite_hero
    if actor.kind == "mage":
      sprite = sprite_mage
    if actor.kind == "bat":
      sprite = sprite_bat
    elif actor.kind == "rat":
      sprite = sprite_rat
    if sprite.get_height() > 16:
      row -= 0.5
    surface.blit(sprite, (col * TILE_SIZE, row * TILE_SIZE))

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
