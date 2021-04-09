import pygame
from pygame import Surface

TILE_SIZE = 16
WINDOW_SIZE = (256, 224)
WINDOW_SCALE = 1
(WINDOW_WIDTH, WINDOW_HEIGHT) = WINDOW_SIZE
WINDOW_SIZE_SCALED = (WINDOW_WIDTH * WINDOW_SCALE, WINDOW_HEIGHT * WINDOW_SCALE)
WINDOW_FLAGS = pygame.SCALED

def init_display(window_title: str, window_size: (int, int)) -> Surface:
  pygame.display.init()
  pygame.display.set_caption(window_title)
  return pygame.display.set_mode(window_size, WINDOW_FLAGS)

display = init_display("hello", WINDOW_SIZE_SCALED)
surface = Surface(WINDOW_SIZE)
sprite = pygame.image.load("assets/hero.png").convert_alpha()

class Hero:
  def __init__(hero, cell):
    hero.cell = cell

class Grid:
  def __init__(grid, size):
    grid.size = size
  def contains(grid, cell):
    (width, height) = grid.size
    (x, y) = cell
    return x >= 0 and y >= 0 and x < width and y < height

class Game:
  def __init__(game):
    game.grid = Grid((7, 7))
    game.hero = Hero((2, 1))
  def move(game, delta):
    (hero_x, hero_y) = game.hero.cell
    (delta_x, delta_y) = delta
    new_cell = (hero_x + delta_x, hero_y + delta_y)
    if game.grid.contains(new_cell):
      game.hero.cell = new_cell
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
  (hero_x, hero_y) = game.hero.cell
  surface.fill((0, 0, 0))
  surface.blit(sprite, (hero_x * TILE_SIZE, hero_y * TILE_SIZE))

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
