import pygame
import keyboard

from assets import load as use_assets
from hud import Hud
from anims.sine import SineAnim

from contexts import Context
from contexts.inventory import InventoryContext
from contexts.dialogue import DialogueContext

from town.actors.knight import Knight
from town.actors.mage import Mage
from town.actors.genie import Genie
from town.actors.npc import Npc

from town.areas import Area, can_talk
from town.areas.central import CentralArea
from town.areas.outskirts import OutskirtsArea

from filters import stroke
import palette

import config

SPAWN_LEFT = 64
SPAWN_LEFT_FACING = 1
SPAWN_RIGHT = OutskirtsArea.TOWER_X - config.TILE_SIZE // 2
SPAWN_RIGHT_FACING = -1

class TownContext(Context):
  def __init__(town, parent, returning=False):
    super().__init__(parent)
    town.hero = Knight()
    town.ally = Mage()
    town.areas = [CentralArea(), OutskirtsArea()]
    town.area = town.areas[1]
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
    town.area.actors.append(ally)
    town.area.actors.append(hero)

  def handle_keydown(town, key):
    if town.parent.transits:
      return
    if town.child:
      return town.child.handle_keydown(key)
    if key in (pygame.K_LEFT, pygame.K_a):
      return town.handle_move(-1)
    if key in (pygame.K_RIGHT, pygame.K_d):
      return town.handle_move(1)
    if keyboard.get_pressed(key) > 1:
      return
    if key in (pygame.K_RETURN, pygame.K_SPACE):
      return town.handle_talk()
    if key == pygame.K_TAB:
      return town.handle_swap()
    if key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
      return town.handle_inventory()

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
    if (hero.x >= OutskirtsArea.TOWER_X + config.TILE_SIZE // 2
    and type(town.area) is OutskirtsArea):
      town.handle_areachange(1)

  def handle_movestop(town):
    hero = town.hero
    ally = town.ally
    hero.stop_move()
    ally.stop_move()

  def handle_areachange(town, delta):
    town.area_change = delta
    town.hud.exit()
    if type(town.area) is OutskirtsArea and delta == 1:
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
    elif delta == 1:
      hero.x = config.TILE_SIZE
    ally.x = hero.x - config.TILE_SIZE * hero.facing
    ally.stop_move()
    prev_area.actors.remove(ally)
    town.area.actors.append(ally)
    prev_area.actors.remove(hero)
    town.area.actors.append(hero)

  def handle_swap(town):
    town.hero, town.ally = town.ally, town.hero
    town.area.actors.remove(town.hero) # HACK: move hero to front
    town.area.actors.append(town.hero) # we can alleviate this by sorting actor render order instead of altering the array (which is kind of the same thing)

  def handle_inventory(town):
    town.child = InventoryContext(parent=town, inventory=town.parent.inventory)

  def use_item(town, item):
    return (False, "You can't use that here!")

  def handle_talk(town):
    hero = town.hero
    actor = next((a for a in town.area.actors if can_talk(hero, a)), None)
    if actor is None:
      return

    script = map(lambda page: (actor.name, page), actor.message)
    script = tuple(script)
    town.child = DialogueContext(parent=town, script=script)

    # TODO: actor.face method
    dist_x = hero.x - actor.x
    facing = dist_x / abs(dist_x)
    actor.facing = facing

  def draw(town, surface):
    assets = use_assets()
    sprite_talkbubble = assets.sprites["bubble_talk"]

    hero = town.hero
    ally = town.ally
    if town.area_change:
      ally.move(town.area_change)

    for sprite, pos in town.area.render(hero):
      if sprite is sprite_talkbubble and town.child:
        continue
      surface.blit(sprite, pos)

    if town.child:
      town.child.draw(surface)

    town.hud.draw(surface, town)
