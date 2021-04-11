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
  "stairs": pygame.image.load("assets/stairs-up.png").convert_alpha(),
  "door": pygame.image.load("assets/door.png").convert_alpha(),
  "door_open": pygame.image.load("assets/door-open.png").convert_alpha(),
  "eye": pygame.image.load("assets/eye.png").convert_alpha(),
  "eye_flinch": pygame.image.load("assets/eye-flinch.png").convert_alpha(),
  "eye_attack": pygame.image.load("assets/eye-attack.png").convert_alpha(),
  "tag_hp": pygame.image.load("assets/hp.png").convert_alpha(),
  "tag_sp": pygame.image.load("assets/sp.png").convert_alpha(),
  "log": pygame.image.load("assets/log.png").convert_alpha(),
  "portrait_knight": pygame.image.load("assets/portrait-knight.png").convert_alpha(),
  "portrait_mage": pygame.image.load("assets/portrait-mage.png").convert_alpha(),
  "icon_shield": pygame.image.load("assets/icon-shield.png").convert_alpha(),
  "icon_skill": pygame.image.load("assets/icon-skill.png").convert_alpha(),
  "icon_potion": pygame.image.load("assets/icon-potion.png").convert_alpha(),
  "icon_crystal": pygame.image.load("assets/icon-crystal.png").convert_alpha(),
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
  pygame.K_SPACE: False,
  pygame.K_TAB: False
}

def handle_keydown(key):
  global visited_cells, camera
  if len(game.anims) > 0:
    return

  if key == pygame.K_TAB and not is_key_invalid[key]:
    is_key_invalid[key] = True
    game.swap()

  if key == pygame.K_SPACE and not is_key_invalid[key]:
    is_key_invalid[key] = True
    game.special()

  if pygame.key.get_mods() & pygame.KMOD_SHIFT and key == pygame.K_COMMA and not is_key_invalid[key]:
    is_key_invalid[key] = True
    camera = None
    moved = game.ascend()
    if moved:
      visited_cells = []
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
camera = None

def render_game(surface, game):
  global camera
  window_width, window_height = WINDOW_SIZE
  visible_cells = game.p1.visible_cells
  for cell in visible_cells:
    if cell not in visited_cells:
      visited_cells.append(cell)

  hero_x, hero_y = game.p1.cell
  CAMERA_SPEED = 8
  if game.room:
    focus_x, focus_y = game.room.get_center()
    CAMERA_SPEED = 16
  else:
    for anim in game.anims:
      if anim.target is game.p1 and type(anim) is MoveAnim:
        focus_x, focus_y = anim.cur_cell
        break
    else:
      focus_x, focus_y = game.p1.cell

  camera_x = -((focus_x + 0.5) * TILE_SIZE - window_width / 2)
  camera_y = -((focus_y + 0.5) * TILE_SIZE - window_height / 2)
  if camera is not None:
    old_camera_x, old_camera_y = camera
    camera_x = old_camera_x + (camera_x - old_camera_x) / CAMERA_SPEED
    camera_y = old_camera_y + (camera_y - old_camera_y) / CAMERA_SPEED
  camera = (camera_x, camera_y)

  (stage_width, stage_height) = game.stage.size
  surface.fill((0, 0, 0))
  for x, y in visited_cells:
    tile = game.stage.get_tile_at((x, y))
    sprite = None
    if tile is Stage.WALL or tile is Stage.DOOR_HIDDEN:
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
  game.stage.actors.sort(key=get_actor_y)

  for actor in game.stage.actors:
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

    anim = None
    for anim in game.anims:
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

      if type(anim) is FlickerAnim and len([anim for anim in game.anims if anim.target is actor]) == 1:
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
        game.anims.remove(anim)

    existing_facing = next((facing for facing in facings if facing[0] is actor), None)
    if facing is None:
      if existing_facing:
        actor, facing = existing_facing
    else:
      if existing_facing in facings:
        facings.remove(existing_facing)
      facings.append((actor, facing))

    is_flipped = facing == -1
    if sprite:
      surface.blit(pygame.transform.flip(sprite, is_flipped, False), (sprite_x + camera_x, sprite_y + camera_y))

  portrait_knight = sprites["portrait_knight"]
  portrait_mage = sprites["portrait_mage"]
  if type(game.p1) is Knight:
    portrait_mage = portrait_mage.copy()
    pixels = PixelArray(portrait_mage)
  elif type(game.p1) is Mage:
    portrait_knight = portrait_knight.copy()
    pixels = PixelArray(portrait_knight)
  pixels.replace((0xFF, 0xFF, 0xFF), (0x7F, 0x7F, 0x7F))
  pixels.close()
  surface.blit(portrait_knight, (8, 6))
  surface.blit(portrait_mage, (36, 6))
  surface.blit(sprites["hud"], (64, 6))

  hp_y = 16
  surface.blit(sprites["tag_hp"], (74, hp_y))
  surface.blit(sprites["bar"], (93, hp_y + 7))
  pygame.draw.rect(surface, 0xFFFFFF, Rect(96, hp_y + 8, math.floor(50 * game.p1.hp / game.p1.hp_max), 2))
  hp_text = str(math.floor(game.p1.hp)) + "/" + str(game.p1.hp_max)
  surface.blit(recolor(render_text("0" + str(math.floor(game.p1.hp)) + "/" + "0" + str(game.p1.hp_max), font_smallcaps), (0x7F, 0x7F, 0x7F)), (93, hp_y + 1))
  surface.blit(render_text("  " + str(math.floor(game.p1.hp)) + "/  " + str(game.p1.hp_max), font_smallcaps), (93, hp_y + 1))

  sp_y = 30
  surface.blit(sprites["tag_sp"], (74, sp_y))
  surface.blit(sprites["bar"], (93, sp_y + 7))
  pygame.draw.rect(surface, 0xFFFFFF, Rect(96, sp_y + 8, math.floor(50 * game.sp / game.sp_max), 2))
  hp_text = str(math.floor(game.sp)) + "/" + str(game.sp_max)
  surface.blit(recolor(render_text(str(math.floor(game.sp)) + "/" + str(game.sp_max), font_smallcaps), (0x7F, 0x7F, 0x7F)), (93, sp_y + 1))
  surface.blit(render_text(str(math.floor(game.sp)) + "/" + str(game.sp_max), font_smallcaps), (93, sp_y + 1))

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
        elif item == "Warp Crystal":
          sprite = sprites["icon_crystal"]
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
