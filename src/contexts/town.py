import pygame

import keyboard

from assets import load as use_assets
from contexts import Context
from contexts.inventory import InventoryContext
from hud import Hud
from actors.town.knight import Knight
from actors.town.mage import Mage
from actors.town.genie import Genie
from anims.sine import SineAnim

from filters import stroke
import palette

import config

TOWER_X = 224
ACTOR_Y = 128
SPAWN_LEFT = 64
SPAWN_LEFT_FACING = 1
SPAWN_RIGHT = TOWER_X - config.TILE_SIZE // 2
SPAWN_RIGHT_FACING = -1

class TownContext(Context):
  def __init__(town, parent, returning=False):
    super().__init__(parent)
    town.hero = Knight()
    town.ally = Mage()
    town.actors = [town.ally, town.hero]
    town.areas = ["central", "outskirts"]
    town.area = "outskirts"
    town.area_change = 0
    town.genie_anim = SineAnim(90)
    town.hud = Hud()
    town.spawn(returning)

  def spawn(town, returning):
    hero = town.hero
    ally = town.ally
    if returning:
      hero.x = SPAWN_RIGHT
      hero.facing = SPAWN_RIGHT_FACING
      ally.x = hero.x
      ally.facing = hero.facing
    else:
      hero.x = SPAWN_LEFT
      hero.facing = SPAWN_LEFT_FACING
      ally.x = hero.x - config.TILE_SIZE
      ally.facing = hero.facing

  def handle_keydown(town, key):
    if town.parent.transits:
      return
    if town.child:
      return town.child.handle_keydown(key)
    if key == pygame.K_LEFT or key == pygame.K_a:
      town.handle_move(-1)
    elif key == pygame.K_RIGHT or key == pygame.K_d:
      town.handle_move(1)
    if keyboard.get_pressed(key) > 1:
      return
    if key == pygame.K_TAB:
      town.handle_swap()
    if key == pygame.K_ESCAPE or key == pygame.K_BACKSPACE:
      town.handle_inventory()

  def handle_keyup(town, key):
    if town.child:
      return town.child.handle_keyup(key)
    if key == pygame.K_LEFT or key == pygame.K_a:
      town.handle_movestop()
    elif key == pygame.K_RIGHT or key == pygame.K_d:
      town.handle_movestop()

  def handle_move(town, delta):
    hero = town.hero
    ally = town.ally
    ally.follow(hero)
    hero.move(delta)
    if (hero.x <= -config.TILE_SIZE // 2
    and town.areas.index(town.area) - 1 >= 0):
      town.handle_areachange(-1)
    if (hero.x >= config.WINDOW_WIDTH + config.TILE_SIZE // 2
    and town.areas.index(town.area) + 1 < len(town.areas)):
      town.handle_areachange(1)
    if hero.x >= TOWER_X + config.TILE_SIZE // 2 and town.area == "outskirts":
      town.handle_areachange(1)

  def handle_movestop(town):
    hero = town.hero
    ally = town.ally
    hero.stop_move()
    ally.stop_move()

  def handle_areachange(town, delta):
    town.area_change = delta
    town.hud.exit()
    if town.area == "outskirts" and delta == 1:
      town.parent.dissolve(on_clear=town.parent.goto_dungeon)
    else:
      town.parent.dissolve(
        on_clear=lambda: town.change_areas(delta),
        on_end=town.hud.enter
      )

  def change_areas(town, delta):
    prev_area = town.area
    town.area_change = 0
    town.area = town.areas[town.areas.index(town.area) + delta]
    hero = town.hero
    ally = town.ally
    if delta == -1:
      hero.x = config.WINDOW_WIDTH - config.TILE_SIZE
      ally.x = hero.x + config.TILE_SIZE
    elif delta == 1:
      hero.x = config.TILE_SIZE
      ally.x = hero.x - config.TILE_SIZE
    ally.stop_move()
    if town.area == "central":
      genie = Genie()
      genie.x = 112
      town.actors.insert(0, genie)
    elif prev_area == "central":
      town.actors.pop(0)

  def handle_swap(town):
    town.hero, town.ally = town.ally, town.hero
    town.actors.remove(town.hero) # HACK: move hero to front
    town.actors.append(town.hero)

  def handle_inventory(town):
    if town.child is None:
      town.child = InventoryContext(parent=town, inventory=town.parent.inventory)

  def use_item(town, item):
    return (False, "You can't use this here!")

  def draw(town, surface):
    assets = use_assets()
    sprite_bg = assets.sprites["town_" + town.area]
    sprite_tower = assets.sprites["tower"]
    sprite_talkbubble = assets.sprites["bubble_talk"]
    surface.blit(sprite_bg, (0, 0))
    if town.area_change:
      town.ally.move(town.area_change)
    bubbles = []
    for actor in town.actors:
      sprite = actor.render()
      sprite = stroke(sprite, palette.WHITE)
      x = actor.x - config.TILE_SIZE // 2
      y = ACTOR_Y - 1
      if town.area == "central":
        y -= config.TILE_SIZE // 4
      if type(actor) is Genie:
        y -= config.TILE_SIZE // 2 + round(town.genie_anim.update() * 2)
        if abs(actor.x - town.hero.x) < config.TILE_SIZE:
          bubbles.append((sprite_talkbubble, (x + config.TILE_SIZE * 0.75, y - config.TILE_SIZE // 3)))
      surface.blit(sprite, (x, y))
    if town.area == "outskirts":
      surface.blit(sprite_tower, (TOWER_X, ACTOR_Y - 16))
    if town.child:
      town.child.draw(surface)
    else:
      for sprite, pos in bubbles:
        surface.blit(sprite, pos)
    town.hud.draw(surface, town)
