import math
import random
import pygame
from pygame import Rect
import palette
from palette import GREEN, CYAN

import config
from config import WINDOW_SIZE, VISION_RANGE, MOVE_DURATION, RUN_DURATION, JUMP_DURATION

import keyboard
from keyboard import ARROW_DELTAS, key_times

from lib.cell import is_adjacent, manhattan, normal

from assets import load as load_assets
from filters import recolor, replace_color
from text import render as render_text
from transits.dissolve import DissolveOut

import dungeon.gen
from dungeon.fov import shadowcast
from dungeon.camera import Camera
from dungeon.stage import Stage
from dungeon.stageview import StageView

from dungeon.actors import DungeonActor
from dungeon.actors.eye import Eye
from dungeon.actors.knight import Knight
from dungeon.actors.mage import Mage
from dungeon.actors.mimic import Mimic
from dungeon.actors.npc import NPC

from dungeon.props.chest import Chest
from dungeon.props.soul import Soul
from dungeon.props.coffin import Coffin

from items import Item
from skills.weapon import Weapon

from anims.activate import ActivateAnim
from anims.attack import AttackAnim
from anims.awaken import AwakenAnim
from anims.chest import ChestAnim
from anims.item import ItemAnim
from anims.flicker import FlickerAnim
from anims.flinch import FlinchAnim
from anims.move import MoveAnim
from anims.jump import JumpAnim
from anims.pause import PauseAnim

from comps.damage import DamageValue
from comps.hud import Hud
from comps.log import Log, Message, Token
from comps.minimap import Minimap
from comps.previews import Previews
from comps.spmeter import SpMeter

from contexts import Context
from contexts.custom import CustomContext
from contexts.examine import ExamineContext
from contexts.inventory import InventoryContext
from contexts.minimap import MinimapContext
from contexts.skill import SkillContext

class DungeonContext(Context):
  ATTACK_DURATION = 12
  FLINCH_DURATION = 25
  FLINCH_PAUSE_DURATION = 60
  FLICKER_DURATION = 30
  PAUSE_DURATION = 15
  PAUSE_ITEM_DURATION = 30
  PAUSE_DEATH_DURATION = 45
  AWAKEN_DURATION = 45

  def __init__(game, parent):
    super().__init__(parent)
    game.hero = Knight(parent.hero)
    game.ally = Mage(parent.ally)
    game.floors = []
    game.floor = None
    game.room = None
    game.room_entrances = {}
    game.rooms_entered = []
    game.oasis_used = False
    game.memory = []
    game.anims = []
    game.vfx = []
    game.numbers = []
    game.key_requires_reset = {}
    game.seeds = []
    game.lights = False # config.DEBUG
    game.floor_view = StageView(WINDOW_SIZE)
    game.camera = Camera(WINDOW_SIZE)
    game.log = Log()
    game.hud = Hud()
    game.sp_meter = SpMeter()
    game.minimap = Minimap(parent=game)
    game.previews = Previews()
    game.create_floor()
    if config.DEBUG:
      game.handle_minimap()

  def get_floor_no(game):
    return len(game.floors) + 1

  def create_floor(game):
    floor_no = game.get_floor_no()
    floor = gen.gen_debug(seed=config.SEED)
    game.parent.seeds.append(floor.seed)
    # if floor_no == config.TOP_FLOOR:
    #   floor = gen.top_floor()
    # elif floor_no == 3:
    #   floor = gen.giant_room((19, 19))
    # elif floor_no == 1:
    #   floor = gen.dungeon(config.FLOOR_SIZE, config.SEED)
    # else:
    #   floor = gen.dungeon(config.FLOOR_SIZE)

    hero = game.hero
    ally = game.ally
    floor.spawn_elem(hero, floor.entrance)
    hero.facing = (1, 0)
    if not ally.is_dead():
      x, y = floor.entrance
      floor.spawn_elem(ally, (x - 1, y))
      ally.facing = (1, 0)

    promoted = False
    enemies = [e for e in floor.elems if isinstance(e, DungeonActor) and not hero.allied(e)]
    for monster, kills in game.parent.monster_kills.items():
      if (monster.skill is not None
      and monster.skill not in game.parent.skill_pool
      and kills >= 3):
        enemy = next((e for e in enemies if type(e) is monster), None)
        if enemy is not None:
          enemy.promote()
          promoted = True

    if floor_no == config.TOP_FLOOR:
      game.log.print("The air feels different up here.")
    elif promoted:
      game.log.print("You feel a powerful presence on this floor...")
    elif floor.find_tile(Stage.DOOR_HIDDEN):
      game.log.print("This floor seems to hold many secrets.")

    game.floor = floor
    game.floors.append(game.floor)
    game.memory.append((game.floor, []))
    game.rooms_entered.append(game.room)
    game.camera.blur()
    game.camera.update(game)
    game.refresh_fov(moving=True)
    game.redraw_tiles()

  def set_tile_at(game, cell, tile):
    floor = game.floor
    floor_view = game.floor_view
    floor.set_tile_at(cell, tile)
    floor_view.redraw_tile(floor, cell, game.get_visited_cells())

  def refresh_fov(game, moving=False):
    hero = game.hero
    floor = game.floor
    visible_cells = shadowcast(floor, hero.cell, VISION_RANGE)

    door = None
    if moving:
      rooms = [room for room in floor.rooms if hero.cell in room.get_cells() + room.get_border()]
      if len(rooms) == 1:
        room = rooms[0]
      else:
        room = next((room for room in rooms if room is not game.room), None)

      if room != game.room:
        game.oasis_used = False

      game.room = room
      if room and room not in game.room_entrances:
        game.room_entrances[room] = hero.cell
      if (room
      and room in game.room_entrances
      and room not in game.rooms_entered
      and manhattan(hero.cell, game.room_entrances[room]) == 2
      and [e for e in game.floor.elems if (
        e.cell in room.get_cells()
        and isinstance(e, DungeonActor)
        and not hero.allied(e)
      )]):
        door = game.room_entrances[room]
        game.rooms_entered.append(room)
        game.camera.focus(door, speed=8)
        game.anims.append([
          PauseAnim(90, on_end=lambda: game.set_tile_at(door, Stage.DOOR_LOCKED)),
          PauseAnim(105, on_end=game.camera.blur),
          PauseAnim(45)
        ])

    if game.room:
      visible_cells += game.room.get_cells() + game.room.get_border()
    if game.lights:
      visible_cells = floor.get_cells()
    hero.visible_cells = visible_cells

    # update visited cells
    visited_cells = next((cells for floor, cells in game.memory if floor is game.floor), None)
    for cell in visible_cells:
      if cell not in visited_cells:
        visited_cells.append(cell)

    if door is not None:
      return

    hero = game.hero
    camera = game.camera
    nearby_enemies = [e for e in game.floor.elems if (
      isinstance(e, DungeonActor)
      and not hero.allied(e)
      and manhattan(hero.cell, e.cell) <= 1
      and (type(e) is not Mimic or not e.idle)
    )]
    if nearby_enemies:
      enemy = nearby_enemies[0]
      hero_x, hero_y = hero.cell
      enemy_x, enemy_y = enemy.cell
      mid_x = (hero_x + enemy_x) / 2
      mid_y = (hero_y + enemy_y) / 2
      camera.focus((mid_x, mid_y))
    else:
      camera.blur()

  def step(game, run=False):
    if not game.ally.stepped:
      game.step_ally(game.ally)

    hero = game.hero
    actors = [e for e in game.floor.elems if isinstance(e, DungeonActor)]
    enemies = [a for a in actors if not a.allied(hero)]
    enemies.sort(key=lambda e: manhattan(e.cell, hero.cell))

    for actor in actors:
      if actor in enemies:
        game.step_enemy(actor)

      if actor.ailment == "sleep":
        actor.regen(actor.get_hp_max() / 50)

      if actor.ailment == "poison":
        damage = int(actor.get_hp_max() * DungeonActor.POISON_STRENGTH)
        game.flinch(actor, damage, delayed=True)
        if actor.ailment_turns == 0:
          actor.ailment = None
        else:
          actor.ailment_turns -= 1

      if actor.counter:
        actor.counter = max(0, actor.counter - 1)

    for actor in actors:
      actor.stepped = False

  def step_ally(game, ally, run=False, old_hero_cell=None):
    if ally.stepped or ally.is_dead() or ally.ailment == "sleep":
      return False
    hero = game.hero
    actors = [e for e in game.floor.elems if isinstance(e, DungeonActor)]
    enemies = [a for a in actors if not hero.allied(a)]
    visible_enemies = [e for e in enemies if e.cell in hero.visible_cells]
    adjacent_enemies = [e for e in enemies if is_adjacent(e.cell, ally.cell)]
    if adjacent_enemies:
      adjacent_enemies.sort(key=lambda e: e.get_hp())
      enemy = adjacent_enemies[0]
      game.attack(ally, enemy)
      ally.stepped = True
    elif old_hero_cell and (
      is_adjacent(ally.cell, old_hero_cell)
      or manhattan(ally.cell, old_hero_cell) == 2 and game.is_pit_between(ally.cell, old_hero_cell)
    ):
      ally_x, ally_y = ally.cell
      old_x, old_y = old_hero_cell
      ally_delta = (old_x - ally_x, old_y - ally_y)
      jump = game.is_pit_between(ally.cell, old_hero_cell)
      game.move(actor=ally, delta=ally_delta, run=run, jump=jump)
    elif visible_enemies and not is_adjacent(ally.cell, hero.cell):
      visible_enemies.sort(key=lambda e: e.get_hp())
      enemy = visible_enemies[0]
      ally.stepped = game.move_to(ally, enemy.cell)
    elif not is_adjacent(ally.cell, hero.cell):
      ally.stepped = game.move_to(ally, hero.cell, run)

  def is_pit_between(game, a, b):
    ax, ay = a
    nx, ny = normal(a, b)
    target_cell = (ax + nx, ay + ny)
    return game.floor.get_tile_at(target_cell) is Stage.PIT

  def step_enemy(game, enemy):
    if enemy.is_dead() or enemy.stepped or enemy.idle or enemy.ailment == "sleep":
      return False

    if not enemy.aggro:
      hero = game.hero
      ally = game.ally
      floor = game.floor
      rooms = [r for r in floor.rooms if enemy.cell in r.get_cells()]
      if rooms:
        room = rooms[0]
        if hero.cell not in room.get_cells() + room.get_border():
          return False
      elif manhattan(enemy.cell, hero.cell) <= VISION_RANGE:
        if hero.cell not in shadowcast(floor, enemy.cell, VISION_RANGE):
          return False
      else:
        return False

    enemy.aggro = True
    return enemy.step(game)

  def find_closest_enemy(game, actor):
    enemies = [e for e in game.floor.elems if (
      isinstance(e, DungeonActor)
      and not e.is_dead()
      and not e.allied(actor)
    )]
    if len(enemies) == 0:
      return None
    if len(enemies) > 1:
      enemies.sort(key=lambda e: manhattan(e.cell, actor.cell) + random.random() / 2)
    return enemies[0]

  def find_closest_visible_enemy(game, actor):
    hero = game.hero
    floor = game.floor
    visible_elems = [floor.get_elem_at(c) for c in hero.visible_cells if floor.get_elem_at(c)]
    visible_enemies = [e for e in visible_elems if isinstance(e, DungeonActor) and not e.allied(actor)]
    if len(visible_enemies) == 0:
      return None
    if len(visible_enemies) > 1:
      visible_enemies.sort(key=lambda e: manhattan(e.cell, hero.cell))
    return visible_enemies[0]

  def find_room_enemies(game):
    floor = game.floor
    hero = game.hero
    room = game.room
    if room is None:
      return []
    room_cells = room.get_cells()
    return [e for e in game.floor.elems if (
      e.cell in room_cells
      and isinstance(e, DungeonActor)
      and not hero.allied(e)
    )]

  def handle_keyup(game, key):
    game.key_requires_reset[key] = False

  def handle_keydown(game, key):
    if not config.DEBUG and (game.anims or game.log.anim or game.hud.anims):
      return False

    # debug functionality
    ctrl = keyboard.get_pressed(pygame.K_LCTRL) or keyboard.get_pressed(pygame.K_RCTRL)
    shift = keyboard.get_pressed(pygame.K_LSHIFT) or keyboard.get_pressed(pygame.K_RSHIFT)
    if keyboard.get_pressed(key) == 1 and ctrl:
      game.key_requires_reset[key] = True
      if key == pygame.K_ESCAPE:
        return game.toggle_lights()
      if key == pygame.K_s and shift:
        return print(game.parent.seeds)
      if key == pygame.K_s:
        return print(game.floor.seed)
      if key == pygame.K_d:
        return game.handle_debug()

    if game.child:
      return game.child.handle_keydown(key)

    key_requires_reset = key in game.key_requires_reset and game.key_requires_reset[key]
    if key in ARROW_DELTAS and not key_requires_reset:
      delta = ARROW_DELTAS[key]
      run = pygame.K_RSHIFT in key_times and key_times[pygame.K_RSHIFT] > 0
      run = run or pygame.K_LSHIFT in key_times and key_times[pygame.K_LSHIFT] > 0
      moved = game.handle_move(delta, run)
      if not moved:
        game.key_requires_reset[key] = True
      return moved

    if key not in key_times or key_times[key] != 1:
      return False

    if key == pygame.K_TAB:
      return game.handle_swap()

    if key == pygame.K_f:
      return game.handle_examine()

    if key == pygame.K_b:
      return game.handle_custom()

    if key == pygame.K_m:
      return game.handle_minimap()

    if game.hero.is_dead() or game.hero.ailment == "sleep":
      return False

    if key == pygame.K_ESCAPE or key == pygame.K_BACKSPACE:
      return game.handle_inventory()

    if key == pygame.K_BACKSLASH or key == pygame.K_BACKQUOTE:
      return game.handle_wait()

    if key == pygame.K_RETURN or key == pygame.K_SPACE:
      if game.floor.get_tile_at(game.hero.cell) is Stage.STAIRS_UP:
        return game.handle_ascend()
      elif game.floor.get_tile_at(game.hero.cell) is Stage.STAIRS_DOWN:
        return game.handle_descend()
      else:
        return game.handle_skill()

    return False

  def handle_move(game, delta, run=False):
    hero = game.hero
    ally = game.ally
    floor = game.floor
    if hero.is_dead() or hero.ailment == "sleep":
      return False
    old_cell = hero.cell
    hero_x, hero_y = old_cell
    delta_x, delta_y = delta
    acted = False
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_tile = floor.get_tile_at(target_cell)
    target_elem = floor.get_elem_at(target_cell)

    def end_move():
      game.step()
      game.refresh_fov(moving=True)

    def on_move():
      if not moved:
        return False

      if target_elem and not target_elem.solid:
        target_elem.effect(game)
      if target_tile is Stage.OASIS:
        game.use_oasis()
      elif target_tile is Stage.STAIRS_UP:
        game.log.print("There's a staircase going up here.")
      elif target_tile is Stage.STAIRS_DOWN:
        if game.floors.index(floor):
          game.log.print("There's a staircase going down here.")
        else:
          game.log.print("You can return to the town from here.")
      elif target_tile is Stage.MONSTER_DEN and not floor.trap_sprung:
        floor.trap_sprung = True

        def spawn():
          monsters = 15
          cells = [c for c in game.room.get_cells() if (
            not floor.get_elem_at(c)
            and floor.get_tile_at(c) is Stage.FLOOR
            and manhattan(c, hero.cell) > 2
          )]
          for i in range(monsters):
            cell = random.choice(cells)
            enemy = Eye()
            floor.spawn_elem(enemy, cell)
            cells.remove(cell)
            if random.randint(0, 9):
              enemy.ailment = "sleep"

        game.anims.append([
          PauseAnim(
            duration=45,
            on_end=lambda: (
              floor.set_tile_at((hero_x - 1, hero_y), Stage.DOOR_LOCKED),
              game.log.clear(),
              game.log.print("Stepped into a monster den!"),
              spawn()
            )
          )
        ])

      # if not make_sound(1 / 10)
      is_waking_up = False
      if game.room:
        room = game.room
        room_elems = [a for a in [floor.get_elem_at(cell) for cell in room.get_cells()] if a]
        enemies = [e for e in room_elems if isinstance(e, DungeonActor) and not hero.allied(e)]
        enemy = next((e for e in enemies if e.ailment == "sleep" and random.randint(1, 10) == 1), None)
        if enemy:
          enemy.wake_up()
          if game.camera.is_cell_visible(enemy.cell):
            is_waking_up = True
            game.anims.append([
              AwakenAnim(
                duration=DungeonContext.AWAKEN_DURATION,
                target=enemy,
                on_end=lambda: (
                  game.log.print(enemy.token(), " woke up!"),
                  game.anims[0].append(PauseAnim(
                    duration=DungeonContext.PAUSE_DURATION,
                    on_end=end_move
                  ))
                )
              )
            ])
      if not is_waking_up:
        end_move()

      # regen hp
      if game.parent.sp:
        if not hero.is_dead() and not hero.ailment == "sleep":
          hero.regen()
        if not ally.is_dead() and not ally.ailment == "sleep":
          ally.regen()

      # deplete sp
      if target_tile is not Stage.OASIS:
        game.parent.deplete_sp(1 / 100)

    moved = game.move(actor=hero, delta=delta, run=run, on_end=on_move)
    if moved:
      game.step_ally(game.ally, run, old_cell)
      acted = True
    elif isinstance(target_elem, DungeonActor) and not hero.allied(target_elem):
      acted = game.handle_attack(target_elem)
    elif target_tile is Stage.PIT:
      moved = game.jump_pit(hero, run, on_move)
    else:
      game.anims.append([
        AttackAnim(
          duration=DungeonContext.ATTACK_DURATION,
          target=hero,
          src_cell=hero.cell,
          dest_cell=target_cell
        )
      ])
      if type(target_elem) is NPC:
        npc = target_elem
        game.log.clear()
        message = npc.message
        game.log.print(npc.name + ": " + message[0])
        for i in range(1, len(message)):
          game.log.print(message[i])
        if npc.message == npc.messages[0]:
          npc.message = npc.messages[1]
        else:
          npc.message = npc.messages[0]

        npc = target_elem
        game.log.clear()
        message = npc.message
        game.log.print(npc.name + ": " + message[0])
        for i in range(1, len(message)):
          game.log.print(message[i])
        if npc.message == npc.messages[0]:
          npc.message = npc.messages[1]
        else:
          npc.message = npc.messages[0]
      elif type(target_elem) is Coffin:
        target_elem.effect(game)
      elif type(target_elem) is Chest:
        chest = target_elem
        item = chest.contents
        if item:
          if not game.parent.inventory.is_full():
            game.anims.append([
              ChestAnim(
                duration=30,
                target=chest,
                item=item,
                on_end=chest.open
              )
            ])
            game.log.print("You open the lamp")
            if not isinstance(item, Item) and issubclass(item, Weapon):
              game.learn_skill(item)
              game.log.print("Obtained ", item().token(), ".")
            else:
              game.parent.inventory.append(item)
              game.log.print("Obtained ", item.token(), ".")
            acted = True
          else:
            game.log.print("Your inventory is already full!")
        else:
          game.log.print("There's nothing left to take...")
        game.step(run)
        game.refresh_fov()
      elif isinstance(target_elem, DungeonActor) and target_elem.ailment == "sleep" and hero.allied(target_elem):
        game.log.exit()
        game.anims[0].append(PauseAnim(
          duration=60,
          on_end=lambda: (
            target_elem.wake_up(),
            game.log.print(target_elem.token(), " woke up!"),
            game.anims[0].append(FlinchAnim(
              duration=DungeonContext.FLINCH_DURATION,
              target=target_elem,
            ))
          )
        ))
      elif (target_tile is Stage.DOOR
      or target_tile is Stage.DOOR_HIDDEN
      or target_tile is Stage.DOOR_LOCKED):
        if game.open_door(target_cell):
          game.step(run)
          game.refresh_fov()
    return moved

  def jump_pit(game, actor, run=False, on_end=None):
    facing_x, facing_y = actor.facing
    delta = (facing_x * 2, facing_y * 2)
    old_cell = actor.cell
    moved = game.move(actor=actor, delta=delta, run=run, jump=True, on_end=on_end)
    if moved and actor is game.hero:
      game.step_ally(game.ally, run, old_cell)
    return moved

  def handle_attack(game, target):
    hero = game.hero
    if target.idle:
      game.anims.append([
        AttackAnim(
          duration=DungeonContext.ATTACK_DURATION,
          target=hero,
          src_cell=hero.cell,
          dest_cell=target.cell
        ),
        PauseAnim(duration=15, on_end=lambda: (
          game.anims[0].append(ActivateAnim(
            duration=45,
            target=target,
            on_end=lambda: (
              target.activate(),
              game.log.print("The lamp was ", target.token(), "!"),
              game.anims[0].append(PauseAnim(duration=15, on_end=lambda: (
                game.step(),
                game.refresh_fov()
              )))
            )
          ))
        ))
      ])
      game.log.print("You open the lamp")
      return True
    elif hero.weapon:
      game.parent.deplete_sp(hero.weapon.cost)
      return game.attack(hero, target, on_end=lambda: (
        game.step(),
        game.refresh_fov()
      ))

  def handle_wait(game):
    game.step()

  def handle_swap(game):
    if game.ally.is_dead():
      return False
    game.hero, game.ally = (game.ally, game.hero)
    game.refresh_fov(moving=True)
    return True

  def handle_ascend(game):
    if game.floor.get_tile_at(game.hero.cell) is not Stage.STAIRS_UP:
      return game.log.print("There's nowhere to go up here!")
    game.ascend()

  def handle_descend(game):
    if game.floor.get_tile_at(game.hero.cell) is not Stage.STAIRS_DOWN:
      return game.log.print("There's nowhere to go down here!")
    if game.floors.index(game.floor) == 0:
      return game.leave_dungeon()
    game.descend()

  def handle_floorchange(game, direction):
    game.log.exit()
    game.hud.exit()
    game.parent.dissolve(
      on_clear=lambda: (
        game.camera.reset(),
        game.change_floors(direction)
      ),
      on_end=game.hud.enter
    )

  def handle_skill(game):
    if game.child is None:
      game.log.exit()
      game.child = SkillContext(
        parent=game,
        actor=game.hero,
        selected_skill=game.parent.get_skill(game.hero.core),
        on_close=lambda skill: (
          skill and game.parent.set_skill(game.hero.core, skill),
          game.use_skill(game.hero, skill) if skill else game.refresh_fov()
        )
      )

  def handle_inventory(game):
    if game.child is None:
      game.log.exit()
      game.child = InventoryContext(
        parent=game,
        inventory=game.parent.inventory
      )

  def handle_custom(game):
    if game.child is None:
      game.log.exit()
      game.hud.exit()
      game.sp_meter.exit()
      game.previews.exit()
      game.minimap.exit()
      game.child = CustomContext(
        parent=game,
        pool=game.parent.skill_pool,
        new_skills=game.parent.new_skills,
        builds=game.parent.skill_builds,
        chars=(game.hero.core, game.ally.core),
        on_close=lambda _: (
          game.update_skills(),
          game.hud.enter(),
          game.sp_meter.enter(),
          game.previews.enter(),
          game.minimap.enter()
        )
      )

  def handle_examine(game):
    if game.child is None:
      game.log.exit()
      game.hud.exit()
      game.sp_meter.exit()
      game.child = ExamineContext(
        parent=game,
        on_close=lambda _: (
          game.hud.enter(),
          game.sp_meter.enter(),
          game.refresh_fov()
        )
      )

  def handle_minimap(game):
    if game.child is None:
      game.log.exit()
      game.hud.exit()
      game.previews.exit()
      game.sp_meter.exit()
      game.child = MinimapContext(
        parent=game,
        minimap=game.minimap,
        on_close=lambda _: (
          game.hud.enter(),
          game.previews.enter(),
          game.sp_meter.enter(),
          game.refresh_fov()
        )
      )

  def handle_debug(game):
    config.DEBUG = not config.DEBUG
    if config.DEBUG:
      game.handle_minimap()
    elif type(game.child) is MinimapContext:
      game.child.exit()
    print("Debug mode switched {}".format("on" if config.DEBUG else "off"))

  def move(game, actor, delta, run=False, jump=False, on_end=None):
    actor_x, actor_y = actor.cell
    delta_x, delta_y = delta
    target_cell = (actor_x + delta_x, actor_y + delta_y)
    target_tile = game.floor.get_tile_at(target_cell)
    target_elem = game.floor.get_elem_at(target_cell)
    origin_tile = game.floor.get_tile_at(actor.cell)
    origin_elev = origin_tile.elev
    facing_x = -1 if delta_x < 0 else 1 if delta_x > 0 else 0
    facing_y = -1 if delta_y < 0 else 1 if delta_y > 0 else 0
    actor.facing = (facing_x, facing_y)
    if (target_tile and not target_tile.solid
    and abs(target_tile.elev - origin_tile.elev) < 1
    and (target_elem is None
      or not target_elem.solid
      or actor is game.hero and target_elem is game.ally and not game.ally.ailment == "sleep"
    )):
      duration = RUN_DURATION if run else MOVE_DURATION
      anim_kind = JumpAnim if jump else MoveAnim
      move_anim = anim_kind(
        duration=duration,
        target=actor,
        src_cell=actor.cell,
        dest_cell=target_cell,
        on_end=on_end
      )
      move_group = game.find_move_group()
      if move_group:
        move_group.append(move_anim)
      else:
        game.anims.append([move_anim])
      actor.cell = target_cell
      return True
    else:
      return False

  def find_move_group(game):
    for group in game.anims:
      for anim in group:
        if (isinstance(anim, MoveAnim)
        # and actor.allied(anim.target)
        and isinstance(anim.target, DungeonActor)):
          return group

  def move_to(game, actor, cell, run=False):
    if actor.cell == cell:
      return False

    delta_x, delta_y = (0, 0)
    actor_x, actor_y = actor.cell
    target_x, target_y = cell
    floor = game.floor

    def is_empty(cell):
      target_tile = floor.get_tile_at(cell)
      target_elem = floor.get_elem_at(cell)
      return not target_tile.solid and (not target_elem or not target_elem.solid)

    def select_x():
      if target_x < actor_x and is_empty((actor_x - 1, actor_y)):
        return -1
      elif target_x > actor_x and is_empty((actor_x + 1, actor_y)):
        return 1
      else:
        return 0

    def select_y():
      if target_y < actor_y and is_empty((actor_x, actor_y - 1)):
        return -1
      elif target_y > actor_y and is_empty((actor_x, actor_y + 1)):
        return 1
      else:
        return 0

    if random.randint(0, 1):
      delta_x = select_x()
      if not delta_x:
        delta_y = select_y()
    else:
      delta_y = select_y()
      if not delta_y:
        delta_x = select_x()

    if delta_x or delta_y:
      return game.move(actor=actor, delta=(delta_x, delta_y), run=run, on_end=game.refresh_fov)
    else:
      return False

  def open_door(game, cell):
    floor = game.floor
    tile = floor.get_tile_at(cell)

    opened = False

    if tile is Stage.DOOR:
      opened = True
    elif tile is Stage.DOOR_HIDDEN:
      game.log.print("Discovered a hidden door!")
      opened = True
    elif tile is Stage.DOOR_LOCKED:
      game.log.print("The door is locked...")

    if opened:
      game.floor.set_tile_at(cell, Stage.DOOR_OPEN)
      game.redraw_tiles()
    return opened

  def redraw_tiles(game):
    game.floor_view.redraw_tiles(game.floor, game.camera, game.get_visible_cells(), game.get_visited_cells())

  def attack(game, actor, target, damage=None, on_connect=None, on_end=None):
    if actor.weapon is None:
      return False
    if damage is None:
      modifier = actor.weapon.st if actor.weapon else 0
      damage = DungeonActor.find_damage(actor, target, modifier)
      game.log.print(actor.token(), " uses ", actor.weapon().token())
    def connect():
      if on_connect:
        on_connect()
      real_target = actor if target.counter else target
      real_damage = damage
      if target.counter:
        game.log.print(target.token(), " reflected the attack!")
        # target.counter = False
        real_target = actor
        real_damage = DungeonActor.find_damage(actor, actor)
      game.flinch(
        target=real_target,
        damage=real_damage,
        direction=actor.facing,
        on_end=on_end
      )
    actor.face(target.cell)
    game.anims.append([
      AttackAnim(
        duration=DungeonContext.ATTACK_DURATION,
        target=actor,
        src_cell=actor.cell,
        dest_cell=target.cell,
        on_connect=connect
      )
    ])

  def kill(game, target, on_end=None):
    hero = game.hero
    def remove():
      if not hero.allied(target) and type(target).skill:
        game.parent.record_kill(target)
        if target.rare:
          skill = type(target).skill
          if skill not in game.parent.skill_pool:
            game.floor.spawn_elem(Soul(skill), target.cell)
      target.kill()
      game.floor.elems.remove(target)
      if target is hero:
        game.anims[0].append(PauseAnim(
          duration=DungeonContext.PAUSE_DEATH_DURATION,
          on_end=lambda: (
            game.handle_swap(),
            on_end and on_end()
          )
        ))
      elif game.floor.find_tile(Stage.MONSTER_DEN):
        trap = game.floor.find_tile(Stage.MONSTER_DEN)
        if trap and not [e for e in game.floor.elems if isinstance(e, DungeonActor) and hero.allied(e)]:
          trap_x, trap_y = trap
          game.floor.set_tile_at((trap_x - 2, trap_y), Stage.DOOR_OPEN)
        if on_end:
          on_end()
      elif game.room and game.room in game.rooms_entered and not game.find_room_enemies():
        game.floor.set_tile_at(game.room_entrances[game.room], Stage.DOOR_OPEN)
        if on_end:
          on_end()

    if not hero.allied(target):
      game.log.print("Defeated ", target.token(), ".")
    else:
      game.log.print(target.token(), " is defeated.")
    game.anims[0].append(FlickerAnim(
      duration=DungeonContext.FLICKER_DURATION,
      target=target,
      on_end=remove
    ))

  def flinch(game, target, damage, direction=None, delayed=False, on_end=None):
    was_asleep = target.ailment == "sleep"
    end = lambda: on_end and on_end()
    if target.is_dead(): end()

    def awaken():
      game.log.print(target.token(), " woke up!")
      game.anims[0].append(PauseAnim(duration=DungeonContext.PAUSE_DURATION))

    def respond():
      if target.is_dead() or game.floor.get_tile_at(target.cell) is Stage.PIT:
        game.kill(target, on_end)
      elif is_adjacent(target.cell, target.cell):
        # pause before performing step
        return game.anims[0].append(PauseAnim(duration=DungeonContext.PAUSE_DURATION, on_end=end))
      else:
        end()

    flinch = FlinchAnim(
      duration=DungeonContext.FLINCH_DURATION,
      target=target,
      direction=direction,
      on_start=lambda:(
        target.damage(damage),
        game.numbers.append(DamageValue(str(damage), target.cell)),
        game.log.print(target.token(), " {} {} damage.".format(
          "receives" if not game.hero.allied(target) else "suffers",
          damage
        ))
      )
    )

    pause = PauseAnim(duration=DungeonContext.FLINCH_PAUSE_DURATION, on_end=respond)

    if delayed:
      game.anims.append([flinch, pause])
    else:
      game.anims[0].extend([flinch, pause])
    if was_asleep and not target.ailment == "sleep" and not target.is_dead():
      game.anims[0].append(AwakenAnim(
        duration=DungeonContext.AWAKEN_DURATION,
        target=target,
        on_end=awaken
      ))

  def use_item(game, item):
    success, message = item.use(game)
    if success:
      game.log.print("Used ", item.token())
      game.log.print(message)
      game.parent.inventory.items.remove(item)
      game.anims.append([
        ItemAnim(
          duration=30,
          target=game.hero,
          item=item
        ),
        PauseAnim(
          duration=60,
          on_end=game.step
        ),
      ])
      return True, None
    else:
      return False, message

  def use_skill(game, actor, skill):
    camera = game.camera
    if actor.get_faction() == "player":
      game.parent.deplete_sp(skill.cost)
    if skill.kind == "weapon":
      actor_x, actor_y = actor.cell
      facing_x, facing_y = actor.facing
      target_cell = (actor_x + facing_x, actor_y + facing_y)
      target = next((e for e in game.floor.elems if (
        isinstance(e, DungeonActor)
        and e.cell == target_cell
      )), None)
      if target:
        game.attack(
          actor=actor,
          target=target,
          on_end=lambda: (
            game.step(),
            game.refresh_fov()
          )
        )
      else:
        game.log.print("But nothing happened...")
    else:
      game.log.print(actor.token(), " uses ", skill().token())
      target_cell = skill.effect(actor, game, on_end=lambda: (
        camera.blur(),
        actor is game.hero and game.step(),
        game.refresh_fov()
      ))
      if target_cell:
        camera.focus(target_cell)

  def learn_skill(game, skill):
    game.parent.learn_skill(skill)

  def update_skills(game):
    game.parent.update_skills()
    game.hero.weapon = game.hero.load_weapon()
    game.ally.weapon = game.ally.load_weapon()

  def ascend(game):
    game.handle_floorchange(1)

  def descend(game):
    game.handle_floorchange(-1)

  def change_floors(game, direction):
    exit_tile = Stage.STAIRS_UP if direction == 1 else Stage.STAIRS_DOWN
    entry_tile = Stage.STAIRS_DOWN if direction == 1 else Stage.STAIRS_UP

    if direction not in (1, -1):
      return False

    old_floor = game.floor
    old_floor.remove_elem(game.hero)
    old_floor.remove_elem(game.ally)

    index = game.floors.index(game.floor) + direction
    if index >= len(game.floors):
      # create a new floor if out of bounds
      game.log.print("You go upstairs.")
      game.create_floor()
    elif index >= 0:
      # go back to old floor if within bounds
      new_floor = game.floors[index]
      stairs_x, stairs_y = new_floor.find_tile(entry_tile)
      new_floor.spawn_elem(game.hero, (stairs_x, stairs_y))
      if not game.ally.is_dead():
        new_floor.spawn_elem(game.ally, (stairs_x - 1, stairs_y))
      game.floor = new_floor
      game.refresh_fov(moving=True)
      game.log.print("You go back upstairs." if direction == 1 else "You go back downstairs.")

    return True

  def leave_dungeon(game):
    game.log.exit()
    game.hud.exit()
    game.sp_meter.exit()
    game.minimap.exit()
    game.parent.dissolve(on_clear=lambda: game.parent.goto_town(returning=True))

  def toggle_lights(game):
    game.lights = not game.lights
    game.refresh_fov()

  def use_oasis(game):
    if game.oasis_used:
      return
    game.oasis_used = True

    def offset_y(cell, delta):
      x, y = cell
      return (x, y + delta)

    hero = game.hero
    game.numbers.append(DamageValue(hero.get_hp_max(), offset_y(hero.cell, -0.25), GREEN))
    game.numbers.append(DamageValue(game.get_sp_max(), hero.cell, CYAN))

    ally = game.ally
    game.numbers.append(DamageValue(ally.get_hp_max(), offset_y(ally.cell, -0.25), GREEN))
    game.numbers.append(DamageValue(game.get_sp_max(), ally.cell, CYAN))

    hero.regen(hero.get_hp_max())
    ally.regen(ally.get_hp_max())
    game.parent.regen_sp()
    game.log.print("You use the oasis")
    game.log.print("The party's HP and SP has been restored.")
    game.anims.append([PauseAnim(duration=240)])

  def get_sp(game):
    return game.parent.get_sp()

  def get_sp_max(game):
    return game.parent.get_sp_max()

  def get_visible_cells(game, actor=None):
    return (actor or game.hero).visible_cells

  def get_visited_cells(game, floor=None):
    floor = floor or game.floor
    return next((cells for f, cells in game.memory if f is floor), None)

  def update_camera(game):
    old_x, old_y = game.camera.get_pos()
    game.camera.update(game)
    new_x, new_y = game.camera.get_pos()
    if round(new_x - old_x) or round(new_y - old_y):
      game.redraw_tiles()

  def draw(game, surface):
    assets = load_assets()
    surface.fill(0)
    window_width = surface.get_width()
    window_height = surface.get_height()

    game.update_camera()

    if not config.DEBUG and not game.minimap.is_focused():
      game.tile_surface = game.floor_view.draw(surface, game)

    for group in game.anims:
      for anim in group:
        if type(anim) is PauseAnim:
          anim.update()
          if anim.done:
            group.remove(anim)
      if len(group) == 0:
        game.anims.remove(group)

    if not config.DEBUG and (not game.child or game.log.anim and not game.log.active):
      game.log.draw(surface)

    animating = (
      game.log.anim and not game.log.active
      or game.hud.anims
      or game.previews.anims
    )
    if game.child and not animating:
      game.child.draw(surface)

    if config.DEBUG:
      game.minimap.anims = []
    else:
      game.hud.draw(surface, game)
      game.sp_meter.draw(surface, game.parent)
      game.previews.draw(surface, game)
    game.minimap.draw(surface)
