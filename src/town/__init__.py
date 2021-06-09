import pygame
from pygame.transform import flip
import keyboard

from assets import load as use_assets
from hud import Hud

from contexts import Context
from contexts.inventory import InventoryContext
from contexts.dialogue import DialogueContext
from contexts.custom import CustomContext
from town.topview import BuildingContext

from transits.dissolve import DissolveOut

from cores.knight import KnightCore
from cores.mage import MageCore
from cores.rogue import RogueCore
from town.actors.knight import Knight
from town.actors.mage import Mage
from town.actors.rogue import Rogue
from town.actors.genie import Genie
from town.actors.npc import Npc

from town.graph import TownGraph
from town.areas import Area, AreaLink, can_talk, find_nearby_link
from town.areas.outskirts import OutskirtsArea
from town.areas.central import CentralArea
from town.areas.clearing import ClearingArea

from config import TILE_SIZE, KNIGHT_BUILD, MAGE_BUILD, ROGUE_BUILD
from anims import Anim

class MoveAnim(Anim): pass

SPAWN_LEFT = 64
SPAWN_LEFT_FACING = (1, 0)
SPAWN_RIGHT = OutskirtsArea.TOWER_X - TILE_SIZE // 2
SPAWN_RIGHT_FACING = (-1, 0)

def resolve_char(core):
  if type(core) is KnightCore: return Knight(core)
  if type(core) is MageCore: return Mage(core)
  if type(core) is RogueCore: return Rogue(core)

def resolve_build(core):
  if type(core) is KnightCore: return KNIGHT_BUILD
  if type(core) is MageCore: return MAGE_BUILD
  if type(core) is RogueCore: return ROGUE_BUILD

class TownContext(Context):
  def __init__(town, returning=False):
    super().__init__()
    town.returning = returning
    town.hero = None
    town.ally = None
    town.graph = TownGraph(
      nodes=[OutskirtsArea, CentralArea, ClearingArea],
      edges=[
        (OutskirtsArea.links["left"], CentralArea.links["right"]),
        (CentralArea.links["alley"], ClearingArea.links["alley"]),
        (CentralArea.links["door_heart"], BuildingContext),
      ]
    )
    town.area = OutskirtsArea()
    town.area_change = None
    town.area_link = None
    town.talkee = None
    town.hud = Hud()
    town.comps = [town.hud]
    town.anims = []

  def init(town):
    parent = town.parent
    town.hero = resolve_char(parent.hero)
    town.ally = resolve_char(parent.ally)
    town.spawn(town.returning)
    transit = next((t for t in parent.transits if type(t) is DissolveOut), None)
    if transit:
      town.hud.anims = []
      town.hud.active = False

  def spawn(town, returning):
    town.area.init(town)

    hero = town.hero
    if returning:
      hero.x = SPAWN_RIGHT
      hero.face(SPAWN_RIGHT_FACING)
    else:
      hero.x = SPAWN_LEFT
      hero.face(SPAWN_LEFT_FACING)

    ally = town.ally
    if ally:
      if returning:
        ally.x = hero.x
      else:
        ally.x = hero.x - TILE_SIZE
      ally.face(hero.facing)
      town.area.actors.append(ally)
    town.area.actors.append(hero)

  def handle_keydown(town, key):
    if town.get_root().transits or town.anims or town.area_change or town.area_link:
      return
    if town.child:
      return town.child.handle_keydown(key)
    if key in (pygame.K_LEFT, pygame.K_a):
      return town.handle_move((-1, 0))
    if key in (pygame.K_RIGHT, pygame.K_d):
      return town.handle_move((1, 0))
    if key in (pygame.K_UP, pygame.K_w):
      return town.handle_zmove((0, -1))
    if key in (pygame.K_DOWN, pygame.K_s):
      return town.handle_zmove((0, 1))
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
    old_x = hero.x
    hero.move(delta)
    for link in town.area.links.values():
      if (old_x < link.x and hero.x >= link.x and link.direction == (1, 0)
      or old_x > link.x and hero.x <= link.x and link.direction == (-1, 0)):
        town.handle_areachange(link)
        break
    else:
      facing_x, _ = hero.facing
      if hero.x < 0 and facing_x < 0:
        hero.x = 0
      if hero.x > town.area.width and facing_x > 0:
        hero.x = town.area.width
    ally = town.ally
    if ally:
      ally.follow(hero)
    return True

  def handle_zmove(town, delta):
    link = find_nearby_link(town.hero, town.area.links)
    if link is None or link.direction != delta or town.graph.tail(link) is None:
      return False
    town.area_link = link
    return True

  def handle_movestop(town):
    hero = town.hero
    hero.stop_move()
    ally = town.ally
    if ally:
      ally.stop_move()

  def handle_areachange(town, link):
    town.area_change = link.direction
    town.get_root().dissolve(on_clear=lambda: town.follow_link(link))

  def follow_link(town, link):
    dest_item = town.graph.tail(head=link)
    if dest_item:
      if not isinstance(dest_item, AreaLink) and issubclass(dest_item, Context):
        town.open(dest_item())
        town.area_change = None
        town.area_link = None
        town.hero.stop_move()
        town.hero.face((0, 1))
        town.hero.y = 0
        town.hero.indoors = False
      else:
        dest_area = town.graph.link_area(link=dest_item)
        town.change_areas(area=dest_area, link=dest_item)

  def change_areas(town, area, link):
    prev_area = town.area
    town.area = area()
    town.area.init(town)
    town.area_change = None
    town.area_link = None
    hero = town.hero
    hero.stop_move()
    hero.x = link.x
    hero.y = 0
    hero.face((-1 if hero.x > town.area.width // 2 else 1, 0))
    ally = town.ally
    if ally:
      ally.x = hero.x - TILE_SIZE * facing_x
      ally.y = 0
      ally.face(hero.facing)
      ally.stop_move()
      prev_area.actors.remove(ally)
      town.area.actors.append(ally)
    prev_area.actors.remove(hero)
    town.area.actors.append(hero)

  def handle_swap(town):
    if not town.ally:
      return False
    town.hero, town.ally = town.ally, town.hero
    town.parent.hero, town.parent.ally = town.parent.ally, town.parent.hero
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

    old_facing = actor.facing
    actor.face(hero)

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
        game.update_skills()
      )
    ))

  def recruit(town, actor):
    if town.ally:
      town.ally.core.faction = "ally"
      town.anims.append(MoveAnim(target=(town.ally, (actor.x, actor.y))))
    game = town.parent
    game.ally = actor.core
    town.ally = actor
    town.ally.core.faction = "player"
    if actor.core not in town.parent.skill_builds:
      town.parent.skill_builds[actor.core] = resolve_build(actor.core)
    town.anims.append(MoveAnim(target=(town.ally, town.hero.get_follow_pos())))

  def update(town):
    super().update()
    hero = town.hero
    ally = town.ally
    for actor in town.area.actors:
      actor.update()
    for anim in town.anims:
      if type(anim) is MoveAnim:
        actor, dest = anim.target
        done = actor.move_to(dest)
        if done:
          actor.stop_move()
          if dest == town.hero.get_follow_pos():
            actor.face(town.hero)
          town.anims.remove(anim)
    if town.anims:
      return
    if town.area_link:
      link = town.area_link
      if hero.x != link.x:
        hero.move_to((link.x, hero.y))
      else:
        if link.direction == (0, -1):
          TARGET_HORIZON = Area.HORIZON_NORTH
          EVENT_HORIZON = Area.TRANSIT_NORTH
        elif link.direction == (0, 1):
          TARGET_HORIZON = Area.HORIZON_SOUTH
          EVENT_HORIZON = Area.TRANSIT_SOUTH
        if abs(hero.y) >= abs(EVENT_HORIZON) and not town.get_root().transits:
          town.handle_areachange(link=town.area_link)
          tail = town.graph.tail(town.area_link)
          if not isinstance(tail, AreaLink) and issubclass(tail, Context):
            town.hero.indoors = True
        if hero.y != TARGET_HORIZON:
          hero.move_to((link.x, TARGET_HORIZON))
      if ally: ally.follow(hero)
    elif town.area_change:
      hero.move(town.area_change)
      if ally: ally.move(town.area_change)

  def draw(town, surface):
    can_mark = (not town.child
    and not town.anims
    and not town.area_link
    and not town.get_root().transits)
    for sprite in town.area.render(town.hero, can_mark):
      sprite.draw(surface)

    if can_mark:
      if not town.hud.active:
        town.hud.enter()
    else:
      if town.hud.active:
        town.hud.exit()

    if town.child:
      town.child.draw(surface)
    town.hud.draw(surface, town)
