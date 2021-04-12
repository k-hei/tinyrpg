import math
import json
import pygame
from pygame import Surface, PixelArray, Rect
from game import Game
from stage import Stage
from text import Font, render as render_text
from log import Log
from filters import recolor
from anims import AttackAnim, FlickerAnim, MoveAnim, ShakeAnim, PauseAnim
from actors import Knight, Mage, Eye, Chest

TILE_SIZE = 32
WINDOW_SIZE = (256, 224)
WINDOW_SCALE = 3
(WINDOW_WIDTH, WINDOW_HEIGHT) = WINDOW_SIZE
WINDOW_SIZE_SCALED = (WINDOW_WIDTH * WINDOW_SCALE, WINDOW_HEIGHT * WINDOW_SCALE)
WINDOW_FLAGS = 0

WHITE = (0xFF, 0xFF, 0xFF)
GRAY = (0x7F, 0x7F, 0x7F)
RED = (0xE6, 0x46, 0x46)
PURPLE = (0x82, 0x20, 0x75)

def init_display(window_title: str, window_size: (int, int)) -> Surface:
  pygame.display.init()
  pygame.display.set_caption(window_title)
  return pygame.display.set_mode(window_size, WINDOW_FLAGS)

display = init_display("hello", WINDOW_SIZE_SCALED)
surface = Surface(WINDOW_SIZE)
pygame.key.set_repeat(1)

# asset loading
meta_standard = json.loads(open("assets/fonts/standard/metadata.json", "r").read())
meta_smallcaps = json.loads(open("assets/fonts/smallcaps/metadata.json", "r").read())
sprites = {
  "font_standard": pygame.image.load("assets/fonts/standard/typeface.png").convert_alpha(),
  "font_smallcaps": pygame.image.load("assets/fonts/smallcaps/typeface.png").convert_alpha(),
  "knight": pygame.image.load("assets/knight.png").convert_alpha(),
  "knight_flinch": pygame.image.load("assets/knight-flinch.png").convert_alpha(),
  "mage": pygame.image.load("assets/mage.png").convert_alpha(),
  "bat": pygame.image.load("assets/bat.png").convert_alpha(),
  "rat": pygame.image.load("assets/rat.png").convert_alpha(),
  "floor": pygame.image.load("assets/floor.png").convert_alpha(),
  "wall": pygame.image.load("assets/wall.png").convert_alpha(),
  "wall_base": pygame.image.load("assets/wall-base.png").convert_alpha(),
  "chest": pygame.image.load("assets/chest.png").convert_alpha(),
  "chest_open": pygame.image.load("assets/chest-open.png").convert_alpha(),
  "stairs_up": pygame.image.load("assets/stairs-up.png").convert_alpha(),
  "stairs_down": pygame.image.load("assets/stairs-down.png").convert_alpha(),
  "door": pygame.image.load("assets/door.png").convert_alpha(),
  "door_open": pygame.image.load("assets/door-open.png").convert_alpha(),
  "eye": pygame.image.load("assets/eye.png").convert_alpha(),
  "eye_flinch": pygame.image.load("assets/eye-flinch.png").convert_alpha(),
  "eye_attack": pygame.image.load("assets/eye-attack.png").convert_alpha(),
  "tag_hp": pygame.image.load("assets/hp.png").convert_alpha(),
  "tag_sp": pygame.image.load("assets/sp.png").convert_alpha(),
  "tag_floor": pygame.image.load("assets/icon-floor.png").convert_alpha(),
  "log": pygame.image.load("assets/log.png").convert_alpha(),
  "portrait_knight": pygame.image.load("assets/portrait-knight.png").convert_alpha(),
  "portrait_mage": pygame.image.load("assets/portrait-mage.png").convert_alpha(),
  "icon_shield": pygame.image.load("assets/icon-shield.png").convert_alpha(),
  "icon_skill": pygame.image.load("assets/icon-skill.png").convert_alpha(),
  "icon_potion": pygame.image.load("assets/icon-potion.png").convert_alpha(),
  "icon_bread": pygame.image.load("assets/icon-bread.png").convert_alpha(),
  "icon_crystal": pygame.image.load("assets/icon-crystal.png").convert_alpha(),
  "icon_ankh": pygame.image.load("assets/icon-ankh.png").convert_alpha(),
  "skill": pygame.image.load("assets/skill.png").convert_alpha(),
  "box": pygame.image.load("assets/box.png").convert_alpha(),
  "bar": pygame.image.load("assets/bar.png").convert_alpha(),
  "hud": pygame.image.load("assets/hud.png").convert_alpha()
}
font_standard = Font(sprites["font_standard"], **meta_standard)
font_smallcaps = Font(sprites["font_smallcaps"], **meta_smallcaps)

def lerp(a, b, t):
  return a * (1 - t) + b * t

game = Game()

is_key_invalid = {
  pygame.K_LEFT: False,
  pygame.K_RIGHT: False,
  pygame.K_UP: False,
  pygame.K_DOWN: False,
  pygame.K_COMMA: False,
  pygame.K_PERIOD: False,
  pygame.K_SPACE: False,
  pygame.K_TAB: False,
  pygame.K_q: False
}

def handle_keydown(key):
  global visited_cells, camera
  if len(game.anims) > 0:
    return

  if key == pygame.K_q and not is_key_invalid[key]:
    is_key_invalid[key] = True
    game.use_item()

  if key == pygame.K_TAB and not is_key_invalid[key]:
    is_key_invalid[key] = True
    game.swap()

  if key == pygame.K_SPACE and not is_key_invalid[key]:
    is_key_invalid[key] = True
    game.special()

  if pygame.key.get_mods() & pygame.KMOD_SHIFT and key == pygame.K_COMMA and not is_key_invalid[key]:
    is_key_invalid[key] = True
    camera = None
    game.change_floors(1)
    return

  if pygame.key.get_mods() & pygame.KMOD_SHIFT and key == pygame.K_PERIOD and not is_key_invalid[key]:
    is_key_invalid[key] = True
    camera = None
    game.change_floors(-1)
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

  moved = game.handle_move((delta_x, delta_y))
  if not moved:
    is_key_invalid[key] = True

def handle_keyup(key):
  is_key_invalid[key] = False

facings = []
vision_range = 3.5
visited_cells = []
camera = None

def render_game(surface, game):
  global camera
  window_width, window_height = WINDOW_SIZE
  hero = game.p1

  visible_cells = hero.visible_cells
  visited_cells = next((cells for floor, cells in game.memory if floor is game.floor), None)

  anim_group = None
  if len(game.anims) > 0:
    anim_group = game.anims[0]
    # print_group = lambda group: list(map(
    #   lambda anim: type(anim).__name__,
    #   group
    # ))
    # print(list(map(print_group, game.anims)))

  hero_x, hero_y = hero.cell
  focus_x, focus_y = hero.cell
  CAMERA_SPEED = 8
  if game.room:
    focus_x, focus_y = game.room.get_center()
    CAMERA_SPEED = 16
  elif anim_group:
    for anim in anim_group:
      if anim.target is hero and type(anim) is MoveAnim:
        focus_x, focus_y = anim.cur_cell
        break

  camera_x = -((focus_x + 0.5) * TILE_SIZE - window_width / 2)
  camera_y = -((focus_y + 0.5) * TILE_SIZE - window_height / 2)
  if camera is not None:
    old_camera_x, old_camera_y = camera
    camera_x = old_camera_x + (camera_x - old_camera_x) / CAMERA_SPEED
    camera_y = old_camera_y + (camera_y - old_camera_y) / CAMERA_SPEED
  camera = (camera_x, camera_y)

  (floor_width, floor_height) = game.floor.size
  surface.fill((0, 0, 0))
  for x, y in visited_cells:
    tile = game.floor.get_tile_at((x, y))
    sprite = None
    if tile is Stage.WALL or tile is Stage.DOOR_HIDDEN:
      if game.floor.get_tile_at((x, y + 1)) is Stage.FLOOR:
        sprite = sprites["wall_base"]
      else:
        sprite = sprites["wall"]
    elif tile is Stage.STAIRS_UP:
      sprite = sprites["stairs_up"]
    elif tile is Stage.STAIRS_DOWN:
      sprite = sprites["stairs_down"]
    elif tile is Stage.DOOR:
      sprite = sprites["door"]
    elif tile is Stage.DOOR_OPEN:
      sprite = sprites["door_open"]
    elif tile is Stage.FLOOR:
      sprite = sprites["floor"]
    if sprite:
      opacity = 255
      if (x, y) not in visible_cells:
        distance = math.sqrt(math.pow(x - hero_x, 2) + math.pow(y - hero_y, 2))
        opacity = (1 - distance / 8) * 128
      sprite.set_alpha(opacity)
      surface.blit(sprite, (round(x * TILE_SIZE + camera_x), round(y * TILE_SIZE + camera_y)))
      sprite.set_alpha(None)

  # depth sorting
  def get_actor_y(actor):
    return actor.cell[1]
  game.floor.actors.sort(key=get_actor_y)

  is_drawing_knight = False
  is_drawing_mage = False

  for actor in game.floor.actors:
    if actor.cell not in visible_cells:
      continue

    (col, row) = actor.cell
    sprite_x = col * TILE_SIZE
    sprite_y = row * TILE_SIZE

    sprite = None
    if type(actor) is Knight:
      sprite = sprites["knight"]
    elif type(actor) is Mage:
      sprite = sprites["mage"]
    elif type(actor) is Eye:
      sprite = sprites["eye"]
    elif type(actor) is Chest:
      if actor.opened:
        sprite = sprites["chest_open"]
      else:
        sprite = sprites["chest"]

    facing = None
    if anim_group:
      for anim in anim_group:
        if anim.target is not actor:
          continue

        if type(anim) is PauseAnim:
          anim.update()

        if type(anim) is ShakeAnim:
          sprite_x += anim.update()
          if type(actor) is Eye:
            sprite = sprites["eye_flinch"]
          elif type(actor) is Knight:
            sprite = sprites["knight_flinch"]

        if type(anim) is FlickerAnim:
          visible = anim.update()
          if not visible:
            sprite = None
          elif type(actor) is Eye:
            sprite = sprites["eye_flinch"]

        if type(anim) is AttackAnim:
          if type(actor) is Eye:
            sprite = sprites["eye_attack"]

        if type(anim) in (AttackAnim, MoveAnim):
          src_x, src_y = anim.src_cell
          dest_x, dest_y = anim.dest_cell
          if dest_x < src_x:
            facing = -1
          elif dest_x > src_x:
            facing = 1
          col, row = anim.update()
          sprite_x = col * TILE_SIZE
          sprite_y = row * TILE_SIZE

        if anim.done:
          anim_group.remove(anim)
          if len(anim_group) == 0:
            game.anims.remove(anim_group)

    if type(actor) is Eye and actor.asleep and sprite:
      sprite = sprite.copy()
      pixels = PixelArray(sprite)
      pixels.replace(RED, PURPLE)
      pixels.close()

    for group in game.anims:
      for anim in group:
        if anim.target is actor and type(anim) is MoveAnim and group is not anim_group:
          col, row = anim.src_cell
          sprite_x = col * TILE_SIZE
          sprite_y = row * TILE_SIZE

    existing_facing = next((facing for facing in facings if facing[0] is actor), None)
    if facing is None:
      if existing_facing:
        actor, facing = existing_facing
    else:
      if existing_facing in facings:
        facings.remove(existing_facing)
      facings.append((actor, facing))

    if sprite and type(actor) is Knight:
      is_drawing_knight = True

    if sprite and type(actor) is Mage:
      is_drawing_mage = True

    is_flipped = facing == -1
    if sprite:
      surface.blit(pygame.transform.flip(sprite, is_flipped, False), (sprite_x + camera_x, sprite_y + camera_y))

  portrait_knight = sprites["portrait_knight"].copy()
  portrait_mage = sprites["portrait_mage"].copy()
  pixels_knight = PixelArray(portrait_knight)
  pixels_mage = PixelArray(portrait_mage)

  hero_anim = None
  for group in game.anims:
    for anim in group:
      if anim.target is hero:
        hero_anim = anim
        break

  knight = game.p1 if type(hero) is Knight else game.p2
  mage = game.p1 if type(hero) is Mage else game.p2

  if knight.dead and not is_drawing_knight:
    pixels_knight.replace(WHITE, RED)
  elif type(hero) is not Knight:
    pixels_knight.replace(WHITE, GRAY)
  pixels_knight.close()

  if mage.dead and not is_drawing_mage:
    pixels_mage.replace(WHITE, RED)
  elif type(hero) is not Mage:
    pixels_mage.replace(WHITE, GRAY)
  pixels_mage.close()

  surface.blit(portrait_knight, (8, 6))
  surface.blit(portrait_mage, (36, 6))
  surface.blit(sprites["hud"], (64, 6))

  x = 74

  hp_y = 11
  surface.blit(sprites["tag_hp"], (x, hp_y))
  surface.blit(sprites["bar"], (x + 19, hp_y + 7))
  pygame.draw.rect(surface, 0xFFFFFF, Rect(x + 22, hp_y + 8, math.floor(50 * game.p1.hp / game.p1.hp_max), 2))
  hp_text = str(math.floor(game.p1.hp)) + "/" + str(game.p1.hp_max)
  surface.blit(recolor(render_text("0" + str(math.floor(game.p1.hp)) + "/" + "0" + str(game.p1.hp_max), font_smallcaps), (0x7F, 0x7F, 0x7F)), (x + 19, hp_y + 1))
  surface.blit(render_text("  " + str(math.floor(game.p1.hp)) + "/  " + str(game.p1.hp_max), font_smallcaps), (x + 19, hp_y + 1))

  sp_y = 24
  surface.blit(sprites["tag_sp"], (x, sp_y))
  surface.blit(sprites["bar"], (x + 19, sp_y + 7))
  pygame.draw.rect(surface, 0xFFFFFF, Rect(x + 22, sp_y + 8, math.floor(50 * game.sp / game.sp_max), 2))
  hp_text = str(math.floor(game.sp)) + "/" + str(game.sp_max)
  surface.blit(recolor(render_text(str(math.floor(game.sp)) + "/" + str(game.sp_max), font_smallcaps), (0x7F, 0x7F, 0x7F)), (x + 19, sp_y + 1))
  surface.blit(render_text(str(math.floor(game.sp)) + "/" + str(game.sp_max), font_smallcaps), (x + 19, sp_y + 1))

  floor_y = 38
  floor = game.floors.index(game.floor) + 1
  surface.blit(sprites["tag_floor"], (x, floor_y))
  surface.blit(render_text(str(floor) + "F", font_smallcaps), (x + 13, floor_y + 3))

  box = sprites["box"]
  cols = game.inventory.cols
  rows = game.inventory.rows
  margin_x = 8
  margin_y = 6
  spacing = 2
  start_x = window_width - (box.get_width() + spacing) * cols - margin_x
  for row in range(rows):
    for col in range(cols):
      index = row * cols + col
      x = start_x + (box.get_width() + spacing) * col
      y = margin_y + (box.get_height() + spacing) * row
      surface.blit(box, (x, y))
      if index < len(game.inventory.items):
        item = game.inventory.items[index]
        if item == "Potion":
          sprite = sprites["icon_potion"]
        elif item == "Bread":
          sprite = sprites["icon_bread"]
        elif item == "Warp Crystal":
          sprite = sprites["icon_crystal"]
        elif item == "Ankh":
          sprite = sprites["ankh"]
        if sprite:
          surface.blit(sprite, (x + 8, y + 8))

  log = game.log.render(sprites["log"], font_standard)
  surface.blit(log, (
    window_width / 2 - log.get_width() / 2,
    window_height + game.log.y
  ))

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
