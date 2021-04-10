import math
import pygame
from pygame import Surface
from game import Game
from stage import Stage
import fov

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
pygame.key.set_repeat(1)

# asset loading
sprites = {
  "hero": pygame.image.load("assets/hero.png").convert_alpha(),
  "mage": pygame.image.load("assets/mage.png").convert_alpha(),
  "bat": pygame.image.load("assets/bat.png").convert_alpha(),
  "rat": pygame.image.load("assets/rat.png").convert_alpha(),
  "wall": pygame.image.load("assets/wall.png").convert_alpha(),
  "wall_base": pygame.image.load("assets/wall-base.png").convert_alpha(),
  "chest": pygame.image.load("assets/chest.png").convert_alpha(),
  "stairs": pygame.image.load("assets/downstairs.png").convert_alpha(),
  "door": pygame.image.load("assets/door.png").convert_alpha(),
  "door_open": pygame.image.load("assets/door-open.png").convert_alpha(),
  "eye": pygame.image.load("assets/eye.png").convert_alpha(),
  "eye_flinch": pygame.image.load("assets/eye-flinch.png").convert_alpha()
}

def lerp(a, b, t):
  return a * (1 - t) + b * t

game = Game()
is_key_invalid = {
  pygame.K_LEFT: False,
  pygame.K_RIGHT: False,
  pygame.K_UP: False,
  pygame.K_DOWN: False
}

def handle_keydown(key):
  if len(game.anims) > 0:
    return

  if pygame.key.get_mods() & pygame.KMOD_SHIFT and key == pygame.K_PERIOD:
    game.descend()
    return

  delta_x = 0
  delta_y = 0
  if key == pygame.K_LEFT and not is_key_invalid[key]:
    delta_x = -1
  elif key == pygame.K_RIGHT and not is_key_invalid[key]:
    delta_x = 1
  elif key == pygame.K_UP and not is_key_invalid[key]:
    delta_y = -1
  elif key == pygame.K_DOWN and not is_key_invalid[key]:
    delta_y = 1

  if delta_x == 0 and delta_y == 0:
    return

  moved = game.move((delta_x, delta_y))
  if not moved:
    is_key_invalid[key] = True

def handle_keyup(key):
  is_key_invalid[key] = False

facings = []
vision_range = 3.5
visited_cells = []
def render_game(surface, game):
  (window_width, window_height) = WINDOW_SIZE
  (hero_x, hero_y) = game.p1.cell
  visible_cells = fov.shadowcast(game.stage, game.p1.cell, vision_range)
  for cell in visible_cells:
    if cell not in visited_cells:
      visited_cells.append(cell)

  for anim in game.anims:
    if anim.data["actor"] == game.p1 and anim.data["kind"] != "attack":
      (from_x, from_y) = anim.data["from"]
      (to_x, to_y) = anim.data["to"]
      t = (anim.time + 1) / anim.duration
      hero_x = lerp(from_x, to_x, t)
      hero_y = lerp(from_y, to_y, t)

  camera_x = -math.floor((hero_x + 0.5) * TILE_SIZE - window_width / 2)
  camera_y = -math.floor((hero_y + 0.5) * TILE_SIZE - window_height / 2)

  (stage_width, stage_height) = game.stage.size
  surface.fill((0, 0, 0))
  for x, y in visited_cells:
    tile = game.stage.get_tile_at((x, y))
    sprite = None
    if tile is Stage.WALL:
      if game.stage.get_tile_at((x, y + 1)) is Stage.FLOOR:
        sprite = sprites["wall_base"]
      else:
        sprite = sprites["wall"]
    elif tile is Stage.STAIRS:
      sprite = sprites["stairs"]
    elif tile is Stage.DOOR:
      sprite = sprites["door"]
    elif tile is Stage.DOOR_OPEN:
      sprite = sprites["door_open"]
    if sprite:
      opacity = 255
      if (x, y) not in visible_cells:
        distance = math.sqrt(math.pow(x - hero_x, 2) + math.pow(y - hero_y, 2))
        opacity = (1 - distance / 8) * 128
      sprite.set_alpha(opacity)
      surface.blit(sprite, (x * TILE_SIZE + camera_x, y * TILE_SIZE + camera_y))
      sprite.set_alpha(None)

  # depth sorting
  def get_actor_y(actor):
    return actor.cell[1]
  game.stage.actors.sort(key=get_actor_y)

  for actor in game.stage.actors:
    if actor.cell not in visible_cells:
      continue

    (col, row) = actor.cell
    sprite_x = col * TILE_SIZE
    sprite_y = row * TILE_SIZE
    sprite = sprites[actor.kind]
    facing = None

    anim = None
    for anim in game.anims:
      if anim.data["actor"] != actor:
        continue

      if anim.data["kind"] in ("attack", "move"):
        (from_x, from_y) = anim.data["from"]
        (to_x, to_y) = anim.data["to"]
        if to_x < from_x:
          facing = -1
        elif to_x > from_x:
          facing = 1

      if anim.data["kind"] == "move":
        t = anim.update()
        sprite_x = lerp(from_x, to_x, t) * TILE_SIZE
        sprite_y = lerp(from_y, to_y, t) * TILE_SIZE

      if anim.data["kind"] == "attack":
        t = anim.update()
        t = t / 6 if t < 0.5 else (1 - (t - 0.5) * 2) / 6
        sprite_x = lerp(from_x, to_x, t) * TILE_SIZE
        sprite_y = lerp(from_y, to_y, t) * TILE_SIZE

      if anim.data["kind"] == "flinch":
        anim.update()
        if actor.kind == "eye":
          sprite = sprites["eye_flinch"]
        if anim.time % 4 <= 1:
          sprite_x += 1
        else:
          sprite_x -= 1

      if anim.done:
        game.anims.remove(anim)
      break

    existing_facing = next((facing for facing in facings if facing[0] is actor), None)
    if facing is None:
      if existing_facing:
        (actor, facing) = existing_facing
    else:
      if existing_facing in facings:
        facings.remove(existing_facing)
      facings.append((actor, facing))

    is_flipped = facing == -1
    surface.blit(pygame.transform.flip(sprite, is_flipped, False), (sprite_x + camera_x, sprite_y + camera_y))


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
      handle_keydown(event.key)
    elif event.type == pygame.KEYUP:
      handle_keyup(event.key)
  render_display()
