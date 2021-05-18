import pygame
import keyboard

from assets import load as use_assets
from hud import Hud

from contexts import Context
from contexts.inventory import InventoryContext
from contexts.dialogue import DialogueContext
from contexts.custom import CustomContext

from transits.dissolve import DissolveOut

from cores.knight import KnightCore
from cores.mage import MageCore
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
  def __init__(town, returning=False):
    super().__init__()
    town.returning = returning
    town.hero = None
    town.ally = None
    town.areas = [CentralArea(), OutskirtsArea()]
    town.area = town.areas[1]
    town.area_change = 0
    town.talkee = None
    town.hud = Hud()
    town.comps = [town.hud]
    town.hud.anims = []

  def init(town):
    parent = town.parent
    town.hero = manifest(parent.hero)
    town.ally = manifest(parent.ally)
    town.spawn(town.returning)
    transit = next((t for t in parent.transits if type(t) is DissolveOut), None)
    if transit:
      town.hud.active = False
      transit.on_end = town.hud.enter
    for area in town.areas:
      area.init(town)

  def spawn(town, returning):
    hero = town.hero
    if returning:
      hero.x = SPAWN_RIGHT
      hero.facing = SPAWN_RIGHT_FACING
    else:
      hero.x = SPAWN_LEFT
      hero.facing = SPAWN_LEFT_FACING
    town.area.actors.append(hero)

    ally = town.ally
    if ally is None:
      return
    if returning:
      ally.x = hero.x
      ally.facing = hero.facing
    else:
      ally.x = hero.x - config.TILE_SIZE
      ally.facing = hero.facing
    town.area.actors.append(ally)

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
    if key == pygame.K_b:
      return town.handle_custom()

  def handle_keyup(town, key):
    if town.child:
      return town.child.handle_keyup(key)
    if key == pygame.K_LEFT or key == pygame.K_a:
      town.handle_movestop()
    elif key == pygame.K_RIGHT or key == pygame.K_d:
      town.handle_movestop()

  def handle_move(town, delta):
    hero = town.hero
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
    ally = town.ally
    if ally:
      ally.follow(hero)
    return True

  def handle_movestop(town):
    hero = town.hero
    hero.stop_move()
    ally = town.ally
    if ally:
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
    if delta == -1:
      hero.x = config.WINDOW_WIDTH - config.TILE_SIZE
    elif delta == 1:
      hero.x = config.TILE_SIZE
    ally = town.ally
    if ally:
      ally.x = hero.x - config.TILE_SIZE * hero.facing
      ally.stop_move()
      prev_area.actors.remove(ally)
      town.area.actors.append(ally)
    prev_area.actors.remove(hero)
    town.area.actors.append(hero)

  def handle_swap(town):
    if not town.ally:
      return False
    town.hero, town.ally = town.ally, town.hero
    town.area.actors.remove(town.hero) # HACK: move hero to front
    town.area.actors.append(town.hero) # we can alleviate this by sorting actor render order instead of altering the array (which is kind of the same thing)
    return True

  def handle_inventory(town):
    town.open(InventoryContext(inventory=town.parent.inventory))

  def use_item(town, item):
    return (False, "You can't use that here!")

  def handle_talk(town):
    hero = town.hero
    actor = next((a for a in town.area.actors if can_talk(hero, a)), None)
    if actor is None:
      return
    town.talkee = actor

    hero.stop_move()
    ally = town.ally
    if ally:
      ally.stop_move()

    # TODO: actor.face method
    old_facing = actor.facing
    new_facing = (hero.x - actor.x) / abs(hero.x - actor.x)
    actor.face(new_facing)

    messages = actor.messages
    message = messages[actor.message_index]
    actor.message_index = (actor.message_index + 1) % len(messages)
    if callable(message):
      message = message(town)
    def stop_talk():
      actor.face(old_facing)
      town.talkee = None
    town.open(DialogueContext(script=message, on_close=stop_talk))
    return True

  def handle_custom(town):
    town.hud.exit()
    game = town.parent
    chars = [game.hero]
    if game.ally:
      chars.append(game.ally)
    town.open(CustomContext(
      pool=game.skill_pool,
      new_skills=game.new_skills,
      builds=game.skill_builds,
      chars=chars,
      on_close=lambda: (
        game.update_skills(),
        town.hud.enter()
      )
    ))

  def recruit(town, actor):
    game = town.parent
    game.ally = actor.core
    town.ally = manifest(actor.core)
    if actor in town.area.actors:
      town.area.actors.remove(actor)
    town.ally.x = actor.x
    town.ally.y = actor.y
    town.ally.facing = actor.facing
    town.ally.core.faction = "player"
    town.area.actors.insert(town.area.actors.index(town.hero), town.ally)

  def draw(town, surface):
    assets = use_assets()
    sprite_talkbubble = assets.sprites["bubble_talk"]

    hero = town.hero
    ally = town.ally
    if ally and town.area_change:
      ally.move(town.area_change)

    for sprite in town.area.render(hero):
      if sprite.image is sprite_talkbubble and town.child:
        continue
      surface.blit(sprite.image, sprite.pos)

    if town.child:
      if town.child.child and town.hud.active:
        town.hud.exit()
      town.child.draw(surface)
    town.hud.draw(surface, town)

def manifest(core):
  if type(core) is KnightCore:
    return Knight(core)
  elif type(core) is MageCore:
    return Mage(core)
  else:
    return None
