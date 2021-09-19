import math
from math import inf
from random import random, randint, choice
import pygame
from pygame import Rect
from copy import deepcopy
from dataclasses import dataclass
import json

import config
from config import (
  DEBUG_GEN,
  WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_SIZE,
  MOVE_DURATION, RUN_DURATION, JUMP_DURATION, PUSH_DURATION, NUDGE_DURATION, FLICKER_DURATION,
  LABEL_FRAMES,
  VISION_RANGE,
  MAX_SP,
  TILE_SIZE,
  ENABLED_COMBAT_LOG,
)

import lib.gamepad as gamepad
import lib.keyboard as keyboard
from lib.keyboard import ARROW_DELTAS, key_times

import debug

from lib.cell import add as add_vector, subtract as subtract_vector, is_adjacent, manhattan, normal, neighborhood
from lib.direction import invert as invert_direction, normalize as normalize_direction
from lib.compose import compose

import assets
from assets import load as load_assets
from sprite import Sprite
from filters import recolor, replace_color, outline
from colors.palette import BLACK, WHITE, RED, GREEN, BLUE, GOLD, CYAN, PURPLE
from text import render as render_text
from transits.dissolve import DissolveIn, DissolveOut

import dungeon.gen as gen
from dungeon.fov import shadowcast
from dungeon.camera import Camera
from dungeon.stage import Stage, Tile
from dungeon.stageview import StageView

from dungeon.actors import DungeonActor
from dungeon.actors.eyeball import Eyeball
from dungeon.actors.knight import Knight as KnightActor
from dungeon.actors.mage import Mage as MageActor
from dungeon.actors.mimic import Mimic
from dungeon.actors.npc import Npc

from cores import Core
from cores.knight import Knight
from cores.mage import Mage

from dungeon.props import Prop
from dungeon.props.door import Door
from dungeon.props.chest import Chest
from dungeon.props.bag import Bag
from dungeon.props.soul import Soul
from dungeon.props.coffin import Coffin
from dungeon.props.palm import Palm
from dungeon.props.itemdrop import ItemDrop
from dungeon.props.poisonpuff import PoisonPuff

from inventory import Inventory
from items import Item
from items.gold import Gold
from items.materials import MaterialItem
from skills import Skill
from skills.weapon import Weapon

from anims.activate import ActivateAnim
from anims.attack import AttackAnim
from anims.awaken import AwakenAnim
from anims.item import ItemAnim
from anims.flicker import FlickerAnim
from anims.flinch import FlinchAnim
from anims.shake import ShakeAnim
from anims.move import MoveAnim
from anims.jump import JumpAnim
from anims.pause import PauseAnim
from anims.path import PathAnim

from comps.damage import DamageValue
from comps.hud import Hud
from comps.log import Log, Message, Token
from comps.minimap import Minimap
from comps.spmeter import SpMeter
from comps.floorno import FloorNo
from comps.skillbanner import SkillBanner
from vfx.flash import FlashVfx
from vfx.talkbubble import TalkBubble

from contexts import Context
from contexts.custom import CustomContext
from contexts.examine import ExamineContext
from contexts.inventory import InventoryContext
from contexts.minimap import MinimapContext
from contexts.skill import SkillContext
from contexts.dialogue import DialogueContext
from contexts.prompt import PromptContext, Choice
from contexts.gameover import GameOverContext

from dungeon.floors.floor1 import Floor1
from dungeon.floors.floor2 import Floor2
from dungeon.floors.floor3 import Floor3
from dungeon.floors.debugfloor import DebugFloor

from dungeon.data import DungeonData
from dungeon.command import MoveCommand, MoveToCommand, PushCommand, SkillCommand

def manifest(core):
  if type(core) is Knight: return KnightActor(core=core)
  if type(core) is Mage: return MageActor(core=core)

class DungeonContext(Context):
  ATTACK_DURATION = 12
  FLINCH_DURATION = 25
  FLINCH_PAUSE_DURATION = 15
  PAUSE_DURATION = 15
  PAUSE_ITEM_DURATION = 30
  PAUSE_DEATH_DURATION = 45
  AWAKEN_DURATION = 45
  FLOORS = [Floor1, Floor2, Floor3]

  def __init__(game, store, floors=[], floor_index=0, memory=None):
    super().__init__()
    game.store = store
    game.hero = manifest(store.party[0])
    game.ally = manifest(store.party[1]) if len(store.party) == 2 else None
    game.party = [game.hero, game.ally] if game.ally else [game.hero]
    game.floors = floors
    game.floor = floors[floor_index] if floors else None
    game.floor_view = None
    game.floor_cells = None
    game.memory = memory or []
    game.room = None
    game.room_within = None
    game.room_entrances = {}
    game.rooms_entered = []
    game.is_hero_sleeping = False
    game.is_hero_running = False
    game.old_hero_cell = None
    game.oasis_used = False
    game.anims = []
    game.commands = []
    game.vfx = []
    game.numbers = []
    game.buttons_rejected = {}
    game.seeds = []
    game.lights = False
    game.god_mode = False
    game.camera = Camera(WINDOW_SIZE)
    game.log = None
    game.minimap = None
    game.comps = []
    game.debug = DEBUG_GEN
    game.time = 0
    game.talkbubble = None

  def init(game):
    if game.floor:
      game.use_floor(game.floor)
    else:
      game.create_floor()
    game.log = Log(align="left")
    game.minimap = Minimap(parent=game)
    game.comps = [
      game.log,
      game.minimap,
      Hud(party=game.store.party, hp=True),
      FloorNo(parent=game),
      SpMeter(store=game.store)
    ]
    for comp in game.comps:
      comp.active = False
      comp.anims = []
    if game.debug:
      game.lights = True
      game.floor_cells = game.floor.get_visible_cells()
      game.parent.transits = []
      game.handle_minimap(lock=True)
      game.refresh_fov()

  def open(game, *args, **kwargs):
    super().open(*args, **kwargs)
    if game.log:
      game.log.exit()

  def close(game):
    debug_file = open("debug.json", "w")
    debug_file.write(json.dumps(
      obj={ "dungeon": game.save() },
      cls=DungeonData.Encoder,
      separators=(',', ':')
    ))
    debug_file.close()
    super().close()

  def get_floor_no(game):
    gen_index = next((i for i, g in enumerate(DungeonContext.FLOORS) if g.__name__ == game.floor.generator), None)
    return gen_index + 1 if gen_index is not None else len(game.floors)

  def get_hero(game):
    return game.hero

  def save(game):
    return DungeonData(
      floor_index=game.floors.index(game.floor),
      floors=deepcopy(game.floors),
      memory=deepcopy(game.memory)
    )

  def use_floor(game, floor, direction=1, generator=None):
    debug.log(f"Using floor with seed {floor.seed}")
    floor.generator = floor.generator or generator and generator.__name__
    if floor not in game.floors:
      new_index = next((i for i, g in enumerate(DungeonContext.FLOORS) if g.__name__ == floor.generator), None)
      old_index = next((i for i, g in enumerate(DungeonContext.FLOORS) if g.__name__ == game.floor.generator), None)
      if new_index is not None and old_index is not None and new_index < old_index:
        debug.log("Prepend new floor")
        game.floors.insert(0, floor)
      else:
        debug.log("Append new floor")
        game.floors.append(floor)
    game.floor = floor
    if len(game.memory) < len(game.floors):
      game.memory.append([])
    game.parent.save()

    floor_no = game.get_floor_no()

    hero = next((e for e in game.floor.elems if (
      isinstance(e, DungeonActor)
      and e.faction == "player"
      and type(e.core) is type(game.store.party[0])
    )), None)
    if hero:
      game.hero = hero
      hero.core = game.store.party[0]
    else:
      hero = game.hero
      hero.facing = (1, 0)
      floor.spawn_elem_at(direction == 1 and floor.entrance or floor.exit, hero)

      ally = game.ally
      if ally and not ally.is_dead():
        floor.spawn_elem_at(floor.entrance, ally)
        floor.elems.reverse()

    enemies = [e for e in floor.elems if isinstance(e, DungeonActor) and not hero.allied(e)]
    for Enemy, kills in game.store.kills.items():
      spawned_enemies = [e for e in enemies if type(e) is Enemy]
      if Enemy.skill and Enemy.skill not in game.store.skills and kills >= 5 and spawned_enemies:
        enemy = choice(spawned_enemies)
        enemy.promote()

    game.room = None
    game.anims = []
    game.commands = []
    game.rooms_entered.append(game.room)
    game.floor_view = StageView(WINDOW_SIZE)
    game.camera.reset()
    game.camera.update(game)
    game.refresh_fov(moving=True)
    game.camera.reset()
    game.time = 0

  def create_floor(game):
    floor = gen.gen_floor(seed=config.SEED)
    game.parent.seeds.append(floor.seed)
    game.use_floor(floor)

  def set_tile_at(game, cell, tile):
    floor = game.floor
    floor_view = game.floor_view
    floor.set_tile_at(cell, tile)
    floor_view.redraw_tile(floor, cell, game.get_visited_cells())

  def refresh_fov(game, moving=False):
    if game.floor is None:
      return

    hero = game.hero
    floor = game.floor
    visible_cells = []

    def is_within_room(room, cell):
      _, room_y = room.cell
      room_cells = room.get_cells() + room.get_edges()
      return hero.cell in [(x, y) for (x, y) in room_cells if (
        y != room_y + room.get_height() + 1
        and y != room_y - 2
      )]

    door = None
    new_room = None
    hallway = None
    path_anim = game.anims and next((a for g in game.anims for a in g if type(a) is PathAnim and not a.done), None)

    if moving and not path_anim:
      rooms = [room for room in floor.rooms if is_within_room(room, hero.cell)]
      room_within = next((r for r in floor.rooms if hero.cell in r.get_cells() + r.get_edges()), None)
      if len(rooms) == 1:
        room = rooms[0]
      else:
        room = next((room for room in rooms if room is not game.room), None)

      if room is not game.room:
        game.oasis_used = False
        if room:
          room.on_focus(game)
        if game.room:
          game.room.on_focus(game)

      if room_within is not game.room_within:
        new_room = room_within

      if room and room not in game.room_entrances:
        already_illuminated_once_this_floor = next((r for r in game.floor.rooms if r in game.room_entrances), None)
        game.room_entrances[room] = hero.cell
        if already_illuminated_once_this_floor:
          room_cellset = set(room.get_cells() + room.get_outline())
          visible_cellset = room_cellset & set(hero.visible_cells)
          anim_cells = list(room_cellset - visible_cellset)
          visible_cells = list(visible_cellset) + neighborhood(hero.cell)
          room_cells = list(room_cellset)

          tween_duration = game.camera.illuminate(room, actor=game.hero)
          if tween_duration:
            not game.anims and game.anims.append([])
            game.anims[0].append(PauseAnim(duration=tween_duration))

          game.log.exit()
          game.anims += [
            [StageView.FadeAnim(
              target=anim_cells,
              duration=15,
              on_start=lambda: game.update_visited_cells(anim_cells),
              on_end=lambda: (
                game.redraw_tiles(force=True),
                setattr(hero, "visible_cells", room_cells),
              )
            )],
            [PauseAnim(duration=15)]
          ]
      game.room = room
      game.room_within = room_within

    if game.lights:
      if not game.floor_cells:
        game.floor_cells = game.floor.get_visible_cells()
      visible_cells = game.floor_cells
    elif path_anim:
      hallway = [c for c in path_anim.path if not next((e for e in game.floor.get_elems_at(c) if isinstance(e, Door)), None)]
      visible_cells = list(set([n for c in hallway for n in (
        neighborhood(c, inclusive=True, diagonals=True)
        + neighborhood(add_vector(c, (0, -1)), inclusive=True, diagonals=True)
      ) if game.floor.get_tile_at(n) is Stage.WALL or game.floor.get_tile_at(n) is Stage.HALLWAY]))
    elif not game.camera.anims and not next((a for g in game.anims for a in g if type(a) is StageView.FadeAnim), None):
      visible_cells = shadowcast(floor, hero.cell, VISION_RANGE)
      def is_cell_within_visited_room(cell):
        room = next((r for r in game.floor.rooms if cell in r.get_cells()), None)
        return room is None or room in game.room_entrances
      visible_cells = [c for c in visible_cells if is_cell_within_visited_room(c)]
      if game.room:
        visible_cells += game.room.get_cells() + game.room.get_outline()

    hero.visible_cells = visible_cells
    game.update_visited_cells(visible_cells)

    if door is not None:
      return

    hero = game.hero
    camera = game.camera
    nearby_enemies = [e for e in game.floor.elems if (
      isinstance(e, DungeonActor)
      and not hero.allied(e)
      and manhattan(hero.cell, e.cell) == 1
      and hero.elev == e.elev
      and not (type(e) is Mimic and e.idle)
    )]
    if nearby_enemies:
      enemy = nearby_enemies[0]
      hero_x, hero_y = hero.cell
      enemy_x, enemy_y = enemy.cell
      mid_x = (hero_x + enemy_x) / 2
      mid_y = (hero_y + enemy_y) / 2
      camera.focus((mid_x, mid_y), force=True)
    else:
      camera.blur()
    game.update_bubble()

    if new_room:
      new_room.on_enter(game)
      game.redraw_tiles(force=True)

  def darken(game, duration=inf):
    game.floor_view.darkened = True
    game.redraw_tiles(force=True)
    # not game.anims and game.anims.append([])
    # game.anims[0].append(StageView.DarkenAnim(duration=duration))

  def darken_end(game):
    game.floor_view.darkened = False
    game.redraw_tiles(force=True)
    # for group in game.anims:
    #   for anim in group:
    #     if type(anim) is StageView.DarkenAnim:
    #       group.remove(anim)
    #       if not group:
    #         game.anims.remove(group)
    #       return True
    # return False

  def step(game, run=False, moving=False):
    commands = {}
    ally = game.ally
    if ally:
      command = game.step_ally(ally)
      if type(command) is tuple:
        commands[ally] = [command]

    hero = game.hero
    actors = [e for e in game.floor.elems if isinstance(e, DungeonActor) and e is not hero]
    non_actors = [e for e in game.floor.elems if not isinstance(e, DungeonActor)]
    enemies = [a for a in actors if not a.allied(hero)]
    enemies.sort(key=lambda e: type(e) is MageActor and 1000 or manhattan(e.cell, hero.cell))

    for elem in non_actors:
      elem.step(game)

    for actor in actors:
      if actor.is_dead() or (not actor.cell in hero.visible_cells and not actor.aggro):
        actor.turns = 0
        continue
      if actor.charge_skill or actor.faction == "ally" and not actor.aggro:
        actor.turns = 1
      else:
        spd = actor.stats.ag / hero.stats.ag
        actor.turns += spd

    for actor in actors:
      while actor.turns >= 1:
        actor.turns -= 1
        had_aggro = actor.aggro
        if actor not in (hero, ally) and not (actor.faction == "ally" and actor.behavior == "guard"):
          command = actor.step_charge()
          command = command or actor.command
          command = command or game.step_enemy(actor)
          if actor.aggro and not had_aggro:
            break
          if type(command) is tuple:
            if actor in commands:
              commands[actor].append(command)
            else:
              commands[actor] = [command]
      if actor not in commands:
        game.end_turn(actor)

    step_status = lambda: game.end_turn(hero)
    end_exec = lambda: game.end_step(moving=moving)
    start_exec = lambda: game.next_command(on_end=end_exec)
    if commands:
      COMMAND_PRIORITY = ["move", "move_to", "use_skill", "attack", "wait"]
      game.commands = sorted(commands.items(), key=lambda item: COMMAND_PRIORITY.index(item[1][0][0]))
      if (hero.command
      and hero.command.on_end
      and not (type(hero.command) is MoveCommand and game.commands[0][1][0][0].startswith("move"))):
        hero.command.on_end = compose(hero.command.on_end, step_status)
        hero.command.on_end = compose(hero.command.on_end, start_exec)
      else:
        step_status()
        start_exec()
    elif hero.command and hero.command.on_end:
      hero.command.on_end = compose(hero.command.on_end, step_status)
      hero.command.on_end = compose(hero.command.on_end, end_exec)
    else:
      step_status()
      end_exec()

  def next_command(game, on_end=None):
    if not game.commands:
      return on_end and on_end()
    actor, commands = game.commands[0]
    step = lambda: (
      game.commands and not (game.commands[0] and game.commands[0][1]) and (
        game.commands.pop(0),
        game.end_turn(actor),
      ),
      game.next_command(on_end)
    )
    is_actor_visible = actor.cell in game.hero.visible_cells
    cmd_name, *cmd_args = commands.pop(0)
    if actor.is_immobile():
      return step()
    if cmd_name == "use_skill":
      return game.use_skill(actor, *cmd_args, on_end=step)
    if cmd_name == "attack":
      return game.attack(actor, *cmd_args, on_end=step)
    if cmd_name == "move":
      if commands:
        return game.move(actor, *cmd_args, run=game.is_hero_running, is_animated=is_actor_visible, on_end=step)
      else:
        game.move(actor, *cmd_args, run=game.is_hero_running, is_animated=is_actor_visible)
        return step()
    if cmd_name == "move_to":
      if commands:
        return game.move_to(actor, *cmd_args, run=game.is_hero_running, is_animated=is_actor_visible, on_end=step)
      else:
        game.move_to(actor, *cmd_args, run=game.is_hero_running, is_animated=is_actor_visible)
        return step()
    if cmd_name == "wait":
      return step()

  def end_turn(game, actor):
    actor.step_status(game)
    effect_elem = next((e for e in game.floor.get_elems_at(actor.cell) if type(e) is PoisonPuff), None)
    if effect_elem:
      effect_elem.effect(game, actor)

  def end_step(game, moving=False):
    actors = [e for e in game.floor.elems if isinstance(e, DungeonActor)]
    for actor in actors:
      actor.command = None
    hero = game.hero
    game.is_hero_running = False
    game.old_hero_cell = hero.cell
    if hero.ailment == "sleep":
      if (game.is_hero_sleeping and hero.get_hp() == hero.get_hp_max()
      or not game.is_hero_sleeping and game.find_closest_visible_enemy(hero) is None):
        hero.dispel_ailment()
      else:
        SLEEP_TURN_DURATION = 9 if game.is_hero_sleeping else 2
        game.anims.append([PauseAnim(
          duration=SLEEP_TURN_DURATION,
          on_end=game.step
        )])
        hero.regen(amount=1)
    if hero.ailment != "sleep":
      game.is_hero_sleeping = False
    game.refresh_fov(moving=moving)

  def step_ally(game, ally, run=False, old_hero_cell=None):
    if not ally or not ally.can_step():
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
      ally.command = True
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
      ally.command = game.move_to(ally, enemy.cell)
    elif not is_adjacent(ally.cell, hero.cell):
      ally.command = game.move_to(ally, hero.cell, run)

  def is_pit_between(game, a, b):
    ax, ay = a
    nx, ny = normal(a, b)
    target_cell = (ax + nx, ay + ny)
    return game.floor.get_tile_at(target_cell) is Stage.PIT

  def is_cell_in_vision_range(game, actor, cell):
    return manhattan(actor.cell, cell) <= VISION_RANGE and cell in shadowcast(game.floor, cell, VISION_RANGE)

  def step_enemy(game, enemy):
    if not enemy.can_step():
      return None

    if enemy.faction == "ally":
      hero = game.hero
      floor = game.floor
      target = game.find_closest_enemy(enemy)
      room = next((r for r in floor.rooms if enemy.cell in r.get_cells()), None)
      if (target and room and target.cell in room.get_cells() + room.get_border()
      or target and game.is_cell_in_vision_range(actor=enemy, cell=target.cell)
      ):
        enemy.alert()
      else:
        enemy.aggro = 0
        return ("move_to", game.old_hero_cell)

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
      enemies.sort(key=lambda e: manhattan(e.cell, actor.cell) + random() / 2)
    return enemies[0]

  def find_closest_visible_enemy(game, actor, cell=None):
    floor = game.floor
    visible_elems = [floor.get_elem_at(c) for c in actor.visible_cells if floor.get_elem_at(c)]
    visible_enemies = [e for e in visible_elems if isinstance(e, DungeonActor) and not e.allied(actor)]
    if len(visible_enemies) == 0:
      return None
    if len(visible_enemies) > 1:
      visible_enemies.sort(key=lambda e: manhattan(e.cell, cell or actor.cell))
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

  def handle_release(game, button):
    if game.child:
      return game.child.handle_release(button)
    if button in game.buttons_rejected:
      del game.buttons_rejected[button]

  def handle_press(game, button=None):
    if game.child:
      return game.child.handle_press(button)

    # debug functionality
    ctrl = keyboard.get_pressed(pygame.K_LCTRL) or keyboard.get_pressed(pygame.K_RCTRL)
    shift = keyboard.get_pressed(pygame.K_LSHIFT) or keyboard.get_pressed(pygame.K_RSHIFT)
    if keyboard.get_pressed(button) == 1 and ctrl:
      game.buttons_rejected[button] = True
      if button == pygame.K_ESCAPE:
        return game.toggle_lights()
      if button == pygame.K_s and shift:
        return print(game.parent.seeds)
      if button == pygame.K_s:
        return print(game.floor.seed)
      if button == pygame.K_d and shift:
        return game.handle_debug_toggle()
      if button == pygame.K_d:
        return game.handle_debug()
      if button == pygame.K_c:
        return print([a.__dict__ for g in game.anims for a in g], game.commands, game.get_head().transits, game.hero and game.hero.core.anims, game.hero.command)
      if button == pygame.K_p:
        return print(game.hero.cell)

    if game.anims or game.commands or game.get_head().transits or game.hero and game.hero.core.anims:
      return False

    directions = not button and [d for d in (gamepad.LEFT, gamepad.RIGHT, gamepad.UP, gamepad.DOWN) if gamepad.get_state(d)]
    if directions:
      directions = sorted(directions, key=lambda d: gamepad.get_state(d))
      button = directions[0]

    delta = ARROW_DELTAS[button] if button in ARROW_DELTAS else None
    if delta:
      if ctrl or gamepad.get_state(gamepad.controls.turn):
        return game.handle_turn(delta)
      moved = game.handle_move(delta, run=shift or gamepad.get_state(gamepad.controls.run))
      if not moved:
        if button not in game.buttons_rejected:
          game.buttons_rejected[button] = 0
        game.buttons_rejected[button] += 1
        if game.buttons_rejected[button] >= 30:
          return game.handle_push()
      return moved

    if gamepad.get_state(gamepad.controls.wait) > 30 or (
    button in (pygame.K_BACKSLASH, pygame.K_BACKQUOTE) and keyboard.get_pressed(button) > 30):
      return game.handle_sleep()

    if keyboard.get_pressed(button) != 1 and gamepad.get_state(button) != 1:
      return None

    if button == pygame.K_f:
      return game.handle_examine()

    if button == pygame.K_m or gamepad.get_state(gamepad.controls.minimap):
      return game.handle_minimap()

    if game.hero.is_dead() or game.hero.ailment == "sleep":
      return False

    if button in (pygame.K_TAB, gamepad.controls.ally):
      return game.handle_switch()

    if button in (pygame.K_BACKSLASH, pygame.K_BACKQUOTE) or gamepad.get_state(gamepad.controls.wait):
      return game.handle_wait()

    if button == pygame.K_q and ctrl or gamepad.get_state(gamepad.controls.use):
      return game.use_item()

    if gamepad.get_state(gamepad.controls.skill):
      return game.handle_skill()

    if gamepad.get_state(gamepad.controls.throw):
      return game.handle_throw() or game.handle_pickup()

    if gamepad.get_state(gamepad.controls.action):
      if game.hero.item:
        game.handle_place()
      elif game.handle_action():
        return True
      elif game.floor.get_tile_at(game.hero.cell) is Stage.STAIRS_UP:
        return game.handle_ascend()
      elif game.floor.get_tile_at(game.hero.cell) is Stage.STAIRS_DOWN:
        return game.handle_descend()
      elif game.floor.get_tile_at(game.hero.cell) is Stage.EXIT:
        return game.handle_exit()
      else:
        return game.handle_pickup()

    if button in (pygame.K_RETURN, pygame.K_SPACE):
      if game.hero.item:
        if shift:
          return game.handle_throw()
        else:
          return game.handle_place()
      else:
        if shift:
          return game.handle_pickup()
        elif game.floor.get_tile_at(game.hero.cell) is Stage.STAIRS_UP:
          return game.handle_ascend()
        elif game.floor.get_tile_at(game.hero.cell) is Stage.STAIRS_DOWN:
          return game.handle_descend()
        elif game.floor.get_tile_at(game.hero.cell) is Stage.EXIT:
          return game.handle_exit()
        elif button == pygame.K_RETURN:
          return game.handle_skill()
        elif button == pygame.K_SPACE:
          if game.handle_action():
            return True
          else:
            return game.handle_pickup()

    return None

  def handle_sleep(game):
    hero = game.hero
    floor = game.floor
    visible_actors = [floor.get_elem_at(c, superclass=DungeonActor) for c in hero.visible_cells]
    visible_enemies = [e for e in visible_actors if e and not e.allied(hero)]
    if hero.ailment:
      return False
    if visible_enemies:
      game.open(DialogueContext([("", "There are enemies nearby!")]))
      return False
    if not game.store.sp:
      game.open(DialogueContext([("", "You're too hungry to sleep right now...")]))
      return False
    hero.inflict_ailment("sleep")
    hero.command = None
    game.is_hero_sleeping = True
    game.step()
    return True

  def handle_turn(game, direction):
    game.hero.facing = direction
    game.update_bubble()
    return True

  def handle_struggle(game, actor):
    if actor.ailment != "freeze":
      return False
    actor.step_status(game)
    game.anims.append([
      ShakeAnim(duration=15, target=actor)
    ])
    if actor.ailment:
      game.step(moving=True)
      return True
    else:
      return False

  def find_hallway(game, cell):
    floor = game.floor
    if floor.get_tile_at(cell) is not Stage.HALLWAY:
      return []

    hallways = []
    stack = []
    for neighbor in neighborhood(cell):
      if floor.get_tile_at(neighbor) is Stage.HALLWAY:
        hallway = [cell]
        hallways.append(hallway)
        stack.append((hallway, neighbor))

    if not hallways:
      return []

    while stack:
      hallway, cell = stack.pop()
      hallway.append(cell)
      neighbors = [n for n in neighborhood(cell) if (
        floor.get_tile_at(n) is Stage.HALLWAY
        and n not in hallway
      )]
      for neighbor in neighbors:
        stack.append((hallway, neighbor))

    if len(hallways) == 1:
      return hallways[0]

    hallways.sort(key=len)
    return list(reversed(hallways[0]))[:-1] + hallways[1]

  def handle_move(game, delta, run=False):
    hero = game.hero
    ally = game.ally
    floor = game.floor

    if hero.ailment == "freeze":
      game.handle_struggle(actor=hero)

    if not hero.can_step():
      return False

    origin_cell = hero.cell
    origin_tile = floor.get_tile_at(origin_cell)
    hero_x, hero_y = origin_cell
    delta_x, delta_y = delta
    acted = False
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_tile = floor.get_tile_at(target_cell)
    target_elem = floor.get_elem_at(target_cell)
    if isinstance(target_elem, Door) and not target_elem.solid:
      target_elem = floor.get_elem_at(target_cell, exclude=[Door])

    moved = False
    def on_move():
      if not moved:
        return False

      if target_tile is Stage.OASIS:
        game.use_oasis()
      elif target_tile is Stage.EXIT:
        game.log.print("There's a staircase leading out of the dungeon here.")
      elif target_tile is Stage.STAIRS_UP:
        game.log.print("There's a staircase going up here.")
      elif target_tile is Stage.STAIRS_DOWN:
        if game.floors.index(floor):
          game.log.print("There's a staircase going down here.")
        else:
          game.log.print("You can return to the town from here.")

      # if not make_sound(1 / 10)
      is_waking_up = False
      if game.room:
        room = game.room
        room_elems = [a for a in [floor.get_elem_at(cell) for cell in room.get_cells()] if a]
        enemies = [e for e in room_elems if isinstance(e, DungeonActor) and not hero.allied(e)]
        enemy = next((e for e in enemies if e.ailment == "sleep" and randint(1, 10) == 1), None)
        if enemy:
          enemy.wake_up()
          if is_adjacent(hero.cell, enemy.cell):
            enemy.alert()
          if game.camera.is_cell_visible(enemy.cell):
            is_waking_up = True
            game.anims.append([
              AwakenAnim(
                duration=DungeonContext.AWAKEN_DURATION,
                target=enemy,
                on_end=lambda: (
                  ENABLED_COMBAT_LOG and game.log.print((enemy.token(), " woke up!")),
                  game.anims[0].append(PauseAnim(
                    duration=DungeonContext.PAUSE_DURATION,
                    on_end=lambda: game.step(moving=True)
                  ))
                )
              )
            ])

      # regen hp
      if game.store.sp:
        if not hero.is_dead() and not hero.ailment == "sleep":
          hero.regen()
        if ally and not ally.is_dead() and not ally.ailment == "sleep":
          ally.regen()

      # deplete sp
      if target_tile is not Stage.OASIS:
        game.store.sp -= 1 / 100

    moved = game.move(actor=hero, delta=delta, run=run, on_end=on_move)
    if hero.facing != delta:
      hero.facing = delta
      if not moved:
        game.update_bubble()

    game.is_hero_running = bool(run)
    if moved:
      ally and game.step_ally(ally, run, origin_cell)
      if target_tile is Stage.HALLWAY:
        hallway = game.find_hallway(origin_cell if origin_tile is Stage.HALLWAY else target_cell)
        if hallway:
          door = next((e for e in game.floor.get_elems_at(hallway[-1]) if isinstance(e, Door)), None)
          hero_path = hallway[hallway.index(game.hero.cell):]
          has_ally = game.ally and not game.ally.is_immobile() and manhattan(game.ally.cell, game.hero.cell) <= 2
          if has_ally:
            if game.ally.cell in hallway and ally.cell == origin_cell:
              ally_path = hallway[hallway.index(game.ally.cell):-1]
            elif game.ally.cell in hallway:
              ally_path = hallway[hallway.index(game.ally.cell)+1:-1]
            else:
              ally_path = [origin_cell] + hallway[:-1]
          else:
            ally_path = []
          game.anims += [
            [
              PathAnim(
                target=game.hero,
                path=hero_path,
                on_step=lambda cell: cell == hallway[-2] and door and not door.opened and door.handle_open(game)
              ),
              *([PathAnim(
                target=game.ally,
                path=ally_path,
              )] if ally_path else [])
            ],
            [
              PauseAnim(
                duration=1,
                on_end=lambda: game.step(moving=True)
              )
            ]
          ]
          game.hero.cell = hero_path[-1]
          if ally_path:
            game.ally.cell = ally_path[-1]
          game.room = None
          game.refresh_fov()
      else:
        game.step(moving=True)
    elif target_tile is Stage.PIT:
      moved = game.jump_pit(hero, run, on_move)
      if moved:
        game.step(moving=True)
    return moved

  def handle_push(game):
    hero = game.hero
    target_cell = add_vector(hero.cell, hero.facing)
    target_elem = next((e for e in game.floor.get_elems_at(target_cell) if (
      e.solid and not e.static
    )), None)
    if target_elem:
      command = PushCommand(target=target_elem)
      def end_push():
        hero.command.on_end = None
        if isinstance(target_elem, DungeonActor) and target_elem.faction == "ally":
          target_elem.command = command
        game.refresh_fov(moving=True)
        game.step(moving=True)
      pushed = game.push(
        actor=hero,
        target=target_elem,
        on_end=end_push
      )
      if pushed:
        hero.command = command
        game.hide_bubble()
      return True
    else:
      return False

  def push(game, actor, target, on_end=None):
    origin_cell = target.cell
    origin_tile = game.floor.get_tile_at(origin_cell)
    target_cell = add_vector(origin_cell, actor.facing)
    target_tile = game.floor.get_tile_at(target_cell)
    target_elem = game.floor.get_elem_at(target_cell)
    if target.static or target_tile is None or target_tile.solid or origin_tile.elev != target_tile.elev or target_elem and target_elem.solid:
      return False
    target.cell = target_cell
    target.elev = target_tile.elev
    game.move(actor, delta=actor.facing, duration=PUSH_DURATION, on_end=on_end)
    game.anims[-1] += [
      MoveAnim(
        target=target,
        duration=PUSH_DURATION,
        src=(*origin_cell, origin_tile.elev),
        dest=(*target_cell, target_tile.elev)
      ),
      PauseAnim(duration=15)
    ]
    target.on_push(game)
    if isinstance(target, DungeonActor) and target.ailment == "sleep":
      target.wake_up()
      target.alert()
    return True

  def obtain(game, item, target=None, on_end=None):
    if game.hero.item:
      obtained = False
    else:
      obtained = game.store.obtain(item)
      if obtained:
        game.anims.append([
          item_anim := ItemAnim(
            target=target,
            item=item()
          )
        ])
        game.open(child=DialogueContext(
          lite=True,
          script=[
            ("", ("Obtained ", item().token(), "."))
          ]
        ), on_close=lambda: (
          on_end and on_end(),
          item_anim and item_anim.end()
        ))
    return obtained

  def jump_pit(game, actor, run=False, on_end=None):
    facing_x, facing_y = actor.facing
    delta = (facing_x * 2, facing_y * 2)
    old_cell = actor.cell
    moved = game.move(actor=actor, delta=delta, run=run, jump=True, on_end=on_end)
    if moved and actor is game.hero and game.ally:
      game.step_ally(game.ally, run, old_cell)
    return moved

  def handle_action(game):
    hero = game.hero
    if hero.ailment == "freeze":
      game.handle_struggle(actor=hero)
    target_cell = add_vector(hero.cell, hero.facing)
    target_actor = game.floor.get_elem_at(target_cell, superclass=DungeonActor)
    if target_actor and not hero.allied(target_actor):
      if not hero.weapon:
        hero.weapon = hero.find_weapon()
      if hero.weapon:
        game.store.sp -= hero.weapon.cost
        return game.attack(hero, target_actor, on_end=game.step)
      return False
    target_elem = game.floor.get_elem_at(target_cell)
    if not target_elem or not target_elem.active:
      return False
    if game.talkbubble:
      game.talkbubble.hide()
    effect_result = target_elem and target_elem.effect(game)
    if effect_result != None and (
      not game.anims
      or not next((a for a in game.anims[0] if a.target is hero), None)
    ):
      not game.anims and game.anims.append([])
      game.anims[-1].append(AttackAnim(
        duration=DungeonContext.ATTACK_DURATION,
        target=hero,
        src=hero.cell,
        dest=target_cell
      ))
    if effect_result is True:
      game.step()
    return effect_result

  def handle_wait(game):
    game.step()

  def switch_chars(game):
    if not game.ally or game.ally.is_dead():
      return False
    game.hero, game.ally = game.ally, game.hero
    game.store.switch_chars()
    game.party.reverse()
    game.refresh_fov(moving=True)
    return True

  def handle_switch(game):
    return game.switch_chars()

  def recruit(game, actor):
    game.store.recruit(actor.core)
    game.ally = actor

  def handle_skill(game):
    game.log.exit()
    game.open(SkillContext(
      skills=game.hero.get_active_skills(),
      selected_skill=game.parent.get_skill(game.hero.core),
      actor=game.hero,
      on_close=lambda skill, dest: (
        skill and (
          game.parent.set_skill(game.hero.core, skill),
          game.use_skill(game.hero, skill, dest)
        ) or game.refresh_fov()
      )
    ))

  def handle_examine(game):
    game.log.exit()
    game.open(ExamineContext(
      on_close=lambda _: game.refresh_fov
    ))

  def handle_minimap(game, lock=False):
    game.log.exit()
    game.open(MinimapContext(
      minimap=game.minimap,
      lock=lock,
      on_close=game.refresh_fov
    ))

  def toggle_cutscenes(game):
    config.CUTSCENES = not config.CUTSCENES

  def toggle_god_mode(game):
    game.god_mode = not game.god_mode
    if game.god_mode:
      game.full_restore()

  def handle_debug(game):
    if game.child:
      return False
    ailments = {
      None: "None",
      "sleep": "Sleep",
      "poison": "Poison",
      "freeze": "Freeze",
    }
    def cycle_ailment():
      for i, (a, n) in enumerate(ailments.items()):
        if a == game.hero.ailment:
          i = (i + 1) % len(ailments)
          break
      next_ailment = [*ailments.keys()][i]
      game.hero.inflict_ailment(next_ailment)
    game.open(PromptContext(
      message="[ DEBUG MENU ]",
      choices=lambda: [
        Choice(text="Cutscenes: {}".format(config.CUTSCENES and "ON" or "OFF")),
        Choice(text="Lights: {}".format(game.lights and "ON" or "OFF")),
        Choice(text="Ailment: {}".format("None" if game.hero.ailment is None else ailments[game.hero.ailment])),
        Choice(text="GodMode: {}".format(game.god_mode and "ON" or "OFF")),
      ],
      on_choose=lambda choice: (
        choice.text.startswith("Cutscenes") and game.toggle_cutscenes(),
        choice.text.startswith("Lights") and game.toggle_lights(),
        choice.text.startswith("Ailment") and cycle_ailment(),
        choice.text.startswith("GodMode") and game.toggle_god_mode()
      ) and False
    ))
    return True

  def handle_debug_toggle(game):
    config.DEBUG = not config.DEBUG
    if config.DEBUG:
      game.handle_minimap()
    elif type(game.child) is MinimapContext:
      game.child.exit()
    print("Debug mode switched {}".format("on" if config.DEBUG else "off"))
    return True

  def handle_talk(game):
    hero = game.hero
    hero_x, hero_y = hero.cell
    facing_x, facing_y = hero.facing
    target_cell = (hero_x + facing_x, hero_y + facing_y)
    target = next((e for e in game.floor.elems if (
      e.cell == target_cell
      and isinstance(e, Npc)
    )), None)
    if target is None:
      return
    game.log.exit()
    game.open(DialogueContext(script=target.script))

  def move(game, actor, delta, run=False, jump=False, duration=0, is_animated=True, on_end=None):
    origin_cell = actor.cell
    origin_tile = game.floor.get_tile_at(actor.cell)
    origin_elem = game.floor.get_elem_at(origin_cell, exclude=[Door])
    origin_elev = origin_tile and origin_tile.elev
    actor_x, actor_y = actor.cell
    delta_x, delta_y = delta
    target_cell = (actor_x + delta_x, actor_y + delta_y)
    target_tile = game.floor.get_tile_at(target_cell)
    target_elem = game.floor.get_elem_at(target_cell)
    facing_x = -1 if delta_x < 0 else 1 if delta_x > 0 else 0
    facing_y = -1 if delta_y < 0 else 1 if delta_y > 0 else 0
    actor.facing = (facing_x, facing_y)
    if (target_tile and (not target_tile.solid or target_tile is game.floor.PIT and actor.floating)
    and (not origin_tile or abs(target_tile.elev - origin_tile.elev) < 1
      and (target_tile.direction == (0, 0) and origin_tile.direction == (0, 0)
      or normalize_direction(delta) == normalize_direction(origin_tile.direction)
      or normalize_direction(delta) == normalize_direction(target_tile.direction)
    )) and (target_elem is None
      or not target_elem.solid
      or (actor is game.hero
        and isinstance(target_elem, DungeonActor)
        and (target_elem.faction == "player"
          or target_elem.faction == "ally" and target_elem.behavior != "guard")
        and target_elem.can_step()
      )
    )):
      duration = duration or (RUN_DURATION if run else MOVE_DURATION)
      duration = duration * 1.5 if jump else duration
      anim_kind = JumpAnim if jump else MoveAnim
      src_cell = (*actor.cell, max(0, origin_tile.elev))
      dest_cell = (*target_cell, max(0, target_tile.elev))
      def unset_command():
        actor.command = None
      command = MoveCommand(direction=delta, on_end=compose(on_end, lambda: (
        unset_command(),
        origin_elem and origin_elem.on_leave(game),
        next((e for e in game.floor.get_elems_at(target_cell) if not e.solid and not isinstance(e, Door) and e.effect(game, actor)), None),
      )))
      if not actor.command:
        actor.command = command
      if is_animated:
        move_anim = anim_kind(
          duration=duration,
          target=actor,
          src=src_cell,
          dest=dest_cell,
          on_end=lambda: command.on_end and command.on_end()
        )
        move_group = game.find_move_group()
        if move_group:
          move_group.append(move_anim)
        else:
          game.anims.append([move_anim])
        if jump:
          game.anims.append([PauseAnim(duration=5)])
      else:
        command.on_end and command.on_end()
      actor.cell = target_cell
      actor.elev = target_tile.elev
      if isinstance(target_elem, DungeonActor) and target_elem.faction == "ally" and target_elem.can_step():
        game.move_to(actor=target_elem, cell=origin_cell, run=run)
      return True
    else:
      on_end and on_end()
      return False

  def find_move_group(game):
    for group in game.anims:
      for anim in group:
        if (isinstance(anim, MoveAnim)
        # and actor.allied(anim.target)
        and isinstance(anim.target, DungeonActor)):
          return group

  def find_move_to_delta(game, actor, dest):
    if actor.cell == dest:
      return (0, 0)

    delta_x, delta_y = (0, 0)
    actor_x, actor_y = actor.cell
    target_x, target_y = dest
    floor = game.floor

    is_cell_walkable = lambda cell: (
      (not Tile.is_solid(game.floor.get_tile_at(cell)) or game.floor.get_tile_at(cell) is game.floor.PIT
        and not next((e for e in game.floor.get_elems_at(cell) if e.solid), None)
      ) if actor.floating else game.floor.is_cell_empty(cell)
    )

    def select_x():
      if target_x < actor_x and is_cell_walkable((actor_x - 1, actor_y)):
        return -1
      elif target_x > actor_x and is_cell_walkable((actor_x + 1, actor_y)):
        return 1
      else:
        return 0

    def select_y():
      if target_y < actor_y and is_cell_walkable((actor_x, actor_y - 1)):
        return -1
      elif target_y > actor_y and is_cell_walkable((actor_x, actor_y + 1)):
        return 1
      else:
        return 0

    delta_x = select_x()
    if not delta_x:
      delta_y = select_y()

    return (delta_x, delta_y)

  def move_to(game, actor, cell, run=False, is_animated=True, on_end=None):
    if actor.cell == cell:
      return False

    delta_x, delta_y = game.find_move_to_delta(actor, dest=cell)
    if delta_x or delta_y:
      return game.move(actor=actor, delta=(delta_x, delta_y), run=run, is_animated=is_animated, on_end=on_end)
    else:
      on_end and on_end()
      return False

  def redraw_tiles(game, force=False):
    game.floor_view.redraw_tiles(
      stage=game.floor,
      camera=game.camera,
      visible_cells=game.get_visible_cells(),
      visited_cells=game.get_visited_cells(),
      anims=game.anims,
      force=force
    )

  def roll(game, dx, ag, chance):
    if dx >= ag:
      chance = chance + (dx - ag) / 100
    elif ag >= dx * 2:
      chance = dx / ag * chance * 0.75
    else:
      chance = dx / ag * chance
    return random() <= chance

  def roll_hit(game, attacker, defender):
    return game.roll(
      dx=attacker.stats.dx + attacker.stats.lu / 2,
      ag=defender.stats.ag + defender.stats.lu / 2,
      chance=0.8
    )

  def roll_crit(game, attacker, defender):
    return game.roll(
      dx=attacker.stats.dx + attacker.stats.lu / 2,
      ag=defender.stats.ag + defender.stats.lu / 2,
      chance=1 / 32
    )

  def roll_block(game, attacker, defender):
    return game.roll(
      dx=defender.stats.dx + defender.stats.lu / 2,
      ag=attacker.stats.dx + attacker.stats.lu / 2,
      chance=0.125
    )

  def can_block(game, defender, attacker):
    return (
      defender.find_shield()
      and not defender.is_immobile()
      and defender.facing == invert_direction(attacker.facing)
      and (type(defender.command) is not SkillCommand
        or game.roll_block(attacker=attacker, defender=defender))
    )

  def find_damage(game, actor, target, modifier=1):
    actor_str = actor.get_str() * modifier
    target_def = target.get_def()
    if game.floor.get_elem_at(target.cell, superclass=Door):
      target_def = max(0, target_def - 2)
    variance = 1
    return max(1, actor_str - target_def + randint(-variance, variance))

  def attack(game, actor, target, damage=None, modifier=1, is_ranged=False, is_animated=True, is_chaining=False, on_connect=None, on_end=None):
    actor.weapon = actor.find_weapon()
    if actor.weapon is None:
      return False

    if damage is None:
      damage = game.find_damage(actor, target, modifier)
      if ENABLED_COMBAT_LOG:
        game.log.print((actor.token(), " uses ", actor.weapon().token()))

    actor.face(target.cell)
    if (target.aggro <= 2 and target.faction != "player"
    or target.facing != actor.facing and target.facing != invert_direction(actor.facing)):
      modifier *= 1.25 # side attack/surprise attack bonus
    block = game.can_block(attacker=actor, defender=target)
    miss = (not target.is_immobile()
      and target.facing != actor.facing
      and ((target.aggro > 1 or target.faction == "player") and not game.roll_hit(attacker=actor, defender=target))
      and (not block or randint(0, 1)))
    crit = (not target.ailment == "freeze" and (
      target.ailment == "sleep"
      or actor.facing == target.facing
      or game.roll_crit(attacker=actor, defender=target)
    ))
    if miss:
      damage = None
    elif block:
      damage = max(0, damage - target.find_shield().en)
      target.block()
    elif crit:
      damage = game.find_damage(actor, target, modifier=modifier * 1.33)

    def connect():
      def end_attack():
        on_end = command.on_end
        command.on_end = None
        on_end and on_end()

      if is_adjacent(actor.cell, target.cell) or is_ranged:
        on_connect and on_connect()
        real_target = actor if target.counter else target
        real_damage = damage
        if target.counter:
          real_target = actor
          real_damage = DungeonActor.find_damage(actor, actor)
        game.flinch(
          target=real_target,
          damage=real_damage,
          direction=actor.facing,
          crit=crit,
          on_end=end_attack
        )
      else:
        end_attack()

    command = SkillCommand(skill=actor.weapon, on_end=on_end)
    actor.command = command

    if is_animated:
      anim = AttackAnim(
        duration=DungeonContext.ATTACK_DURATION,
        delay=(block and 12 or 0),
        target=actor,
        src=actor.cell,
        dest=target.cell,
        on_connect=connect,
      )
      if is_chaining:
        not game.anims and game.anims.append([])
        game.anims[0].append(anim)
      else:
        game.anims.append([anim])
    else:
      connect()

    return damage != None

  def nudge(game, actor, direction, on_end=None):
    floor = game.floor
    source_cell = actor.cell
    source_tile = game.floor.get_tile_at(source_cell)
    target_cell = add_vector(source_cell, direction)
    target_tile = game.floor.get_tile_at(target_cell)
    if not floor.is_cell_empty(target_cell) and floor.get_tile_at(target_cell) is not floor.PIT:
      return False
    actor.cell = target_cell
    actor.elev = target_tile.elev
    # actor.command = True
    if not game.anims: game.anims.append([])
    move_anim = next((a for a in game.anims[0] if a.target == actor and type(a) is MoveAnim), None)
    if move_anim:
      on_end = compose(on_end, move_anim.on_end)
      game.anims[0].remove(move_anim)
    game.anims[0].append(MoveAnim(
      duration=NUDGE_DURATION,
      target=actor,
      src=(*source_cell, source_tile.elev),
      dest=(*target_cell, target_tile.elev),
      on_end=on_end
    ))
    return True

  def kill(game, target, on_end=None):
    hero = game.hero
    def remove():
      target_skill = type(target).skill
      target_drops = type(target).drops
      if target_skill and target.rare:
        skill = target_skill
        if skill not in game.store.skills:
          game.floor.spawn_elem_at(target.cell, Soul(contents=skill))
      if not hero.allied(target):
        game.parent.record_kill(target)
        if (target_drops
        and not (not target_skill or target.rare)
        and randint(1, 3) == 1
        and not game.floor.get_tile_at(target.cell) is Stage.PIT
        and not game.floor.get_elem_at(target.cell, superclass=Bag)
        ):
          drop = choice(target_drops)
          game.floor.spawn_elem_at(target.cell, Bag(contents=drop))
      if target in game.floor.elems:
        game.floor.elems.remove(target)
      if game.room:
        game.room.on_death(game, target)
      if target is hero:
        game.anims[0].append(PauseAnim(
          duration=DungeonContext.PAUSE_DEATH_DURATION,
          on_end=lambda: (
            game.handle_switch()
            and [on_end and on_end()]
            or game.open(GameOverContext())
          )
        ))
      elif on_end:
        on_end()

    if ENABLED_COMBAT_LOG:
      if not hero.allied(target):
        game.log.print(("Defeated ", target.token(), "."))
      else:
        game.log.print((target.token(), " is defeated."))
    target.kill(game)
    game.anims[0].append(FlickerAnim(
      duration=FLICKER_DURATION,
      target=target,
      on_end=remove
    ))

  def flinch(game, target, damage, direction=None, delayed=False, block=False, crit=False, on_end=None):
    was_asleep = target.ailment == "sleep"
    if target.is_dead() and on_end:
      on_end()

    def awaken():
      if ENABLED_COMBAT_LOG:
        game.log.print((target.token(), " woke up!"))
      game.anims[0].append(PauseAnim(duration=DungeonContext.PAUSE_DURATION))

    def respond():
      if target.is_dead() or game.floor.get_tile_at(target.cell) is Stage.PIT:
        if not game.room or game.room.on_kill(game, target):
          game.kill(target, on_end)
      elif on_end:
        on_end()

    if target is game.hero and game.god_mode:
      damage = 0

    ENABLED_COMBAT_LOG and game.log.print((
      target.token(),
      " {}".format(game.hero.allied(target) and "receives" or "suffers"),
      " {} damage.".format(int(damage))
    ))

    if damage == 0:
      damage_text = "BLOCK"
    elif damage == None:
      damage_text = "MISS"
    else:
      damage_text = int(damage)

    display_text = lambda: game.numbers.append(DamageValue(
      text=damage_text,
      cell=target.cell,
      offset=(0, -target.elev * TILE_SIZE)
    ))

    if damage and crit:
      game.numbers.append(DamageValue(
        text="CRITICAL!",
        cell=target.cell,
        offset=(4, -4 - target.elev * TILE_SIZE),
        color=GOLD,
        delay=15
      ))
      game.vfx.append(FlashVfx())
      game.floor_view.shake(vertical=direction[1])
      direction and game.nudge(target, direction)
      if target is not game.hero:
        target.command = True
      target.turns = 0

    if damage == None:
      flinch = None
      if direction:
        target.facing = invert_direction(direction)
      display_text()
    elif int(damage) == 0 or block:
      flinch = ShakeAnim(
        target=target,
        magnitude=0.5,
        duration=15,
        on_start=display_text
      )
    else:
      flinch = FlinchAnim(
        target=target,
        duration=DungeonContext.FLINCH_DURATION,
        direction=direction,
        on_start=lambda: (
          direction and target.facing != direction and not target.charge_skill and setattr(target, "facing", invert_direction(direction)),
          target.damage(damage),
          display_text()
        )
      )

    if flinch:
      game.place_item(actor=target)

    pause = PauseAnim(duration=DungeonContext.FLINCH_PAUSE_DURATION, on_end=respond)
    anim_group = next((g for g in game.anims if not next((a for a in g if a.target is target), None)), [])
    anim_group += [*(flinch and [flinch] or []), pause]
    anim_group not in game.anims and game.anims.append(anim_group)

    if was_asleep and not target.ailment == "sleep" and not target.is_dead():
      game.anims.append([AwakenAnim(
        duration=DungeonContext.AWAKEN_DURATION,
        target=target,
        on_end=awaken
      )])

    if damage == None:
      return False
    else:
      return True

  def freeze(game, target):
    if target.is_dead():
      return False
    target.inflict_ailment("freeze")
    target.aggro = 0
    if ENABLED_COMBAT_LOG:
      game.log.print((target.token(), " is frozen.")),
    game.numbers.append(DamageValue(
      text="FROZEN",
      cell=target.cell,
      offset=(4, -4 - target.elev * TILE_SIZE),
      color=CYAN,
      delay=15
    ))
    return True

  def poison_actor(game, target, on_end=None):
    if (target.is_dead()
    or target.ailment == "poison"
    or game.anims and next((a for a in game.anims[0] if a.target is target and type(a) is FlinchAnim), None)
    ):
      return False
    anims = [
      flinch_anim := FlinchAnim(
        duration=30,
        target=target,
        on_start=lambda: flinch_anim.end() if target.ailment == "poison" else (
          target.inflict_ailment("poison"),
          game.numbers.append(DamageValue(
            text="POISON",
            cell=target.cell,
            offset=(4, -4 - target.elev * TILE_SIZE),
            color=PURPLE,
            delay=15
          ))
        )
      ),
      PauseAnim(target=target, duration=45, on_end=on_end)
    ]
    game.anims[0].extend(anims) if game.anims else game.anims.append(anims)

  def use_item(game, item=None, discard=True):
    carry_item = game.hero and game.hero.item
    if carry_item and item and carry_item is not item:
      return False, "Your hands are full!"
    elif carry_item and not discard:
      item = carry_item
      game.hero.item = None
    if not item:
      return False, "No item to use."
    if discard:
      game.anims.append([
        ItemAnim(
          duration=30,
          target=game.hero,
          item=item()
        ),
        PauseAnim(
          duration=60,
          on_end=game.step
        ),
      ])
    if issubclass(item, MaterialItem):
      success, message = False, "You can't use this item!"
    else:
      success, message = game.store.use_item(item, discard=discard)
    if success is False:
      game.anims.pop()
      return False, message
    elif success is True:
      game.log.print(("Used ", item.token(item)))
      game.log.print(message)
      return True, ""
    else:
      return None, ("Used ", item.token(item), "\n", message)

  def carry_item(game, item):
    if not game.hero.item:
      game.hero.item = item
      return True, None
    else:
      return False, "You can't carry any more."

  def drop_item(game, item):
    hero = game.hero
    if next((e for e in game.floor.get_elems_at(hero.cell) if isinstance(e, ItemDrop)), None):
      return False, "There's nowhere to drop this!"
    game.floor.spawn_elem_at(hero.cell, ItemDrop(item))
    game.step()
    return True, None

  def handle_place(game):
    return game.place_item(actor=game.hero)

  def place_item(game, actor, item=None):
    if not item and not actor.item:
      return False
    item = actor.item
    target_cell = add_vector(actor.cell, actor.facing)
    if (Tile.is_solid(game.floor.get_tile_at(target_cell))
    or next((e for e in game.floor.get_elems_at(target_cell) if e.solid or isinstance(e, ItemDrop)), None)):
      return False
    game.floor.spawn_elem_at(target_cell, ItemDrop(item))
    if not game.anims:
      game.anims.append([
        AttackAnim(
          duration=DungeonContext.ATTACK_DURATION,
          target=actor,
          src=actor.cell,
          dest=target_cell,
          on_end=game.step
        )
      ])
    actor.item = None
    return True

  def handle_pickup(game):
    return game.pickup_item(actor=game.hero)

  def pickup_item(game, actor, itemdrop=None):
    target_cell = add_vector(actor.cell, actor.facing)
    itemdrop = itemdrop or next((e for e in game.floor.get_elems_at(target_cell) if isinstance(e, ItemDrop)), None)
    if not itemdrop:
      return False
    game.floor.remove_elem(itemdrop)
    game.hero.item = itemdrop.item
    game.anims.append([
      AttackAnim(
        target=game.hero,
        src=game.hero.cell,
        dest=target_cell
      )
    ])
    return True

  def handle_throw(game):
    return game.throw_item(actor=game.hero)

  def throw_item(game, actor, item=None):
    if not item and not actor.item:
      return False
    item = actor.item
    facing_cell = add_vector(actor.cell, actor.facing)
    target_elem = None
    target_cell = actor.cell
    nonpit_cell = actor.cell
    throwing = True
    while throwing:
      next_cell = add_vector(target_cell, actor.facing)
      next_tile = game.floor.get_tile_at(next_cell)
      next_elem = next((e for e in game.floor.get_elems_at(next_cell) if e.solid), None)
      if (not next_tile is game.floor.PIT and Tile.is_solid(next_tile)
      or next((e for e in game.floor.get_elems_at(next_cell) if e.solid and not isinstance(e, DungeonActor)), None)
      ):
        throwing = False
        break
      elif next_elem:
        target_elem = next_elem
        throwing = False
      if next_tile is not game.floor.PIT:
        nonpit_cell = next_cell
      target_cell = next_cell
    if game.floor.get_tile_at(target_cell) is game.floor.PIT:
      target_cell = nonpit_cell
    if target_cell == actor.cell:
      game.anims.append([
        AttackAnim(
          target=actor,
          src=actor.cell,
          dest=facing_cell,
        )
      ])
      return False
    itemdrop = ItemDrop(item)
    game.anims.append([
      AttackAnim(
        target=actor,
        src=actor.cell,
        dest=facing_cell,
        on_connect=lambda: (
          setattr(actor, "item", None),
          game.floor.spawn_elem_at(actor.cell, itemdrop),
          game.anims[0].append(throw_anim := ItemDrop.ThrownAnim(
            target=itemdrop,
            src=actor.cell,
            dest=target_cell,
            on_end=lambda: (
              "effect" in dir(item) and target_elem and isinstance(target_elem, DungeonActor) and (
                response := item().effect(game, actor=target_elem, cell=target_cell),
                response and game.log.print(response),
                game.floor.remove_elem(itemdrop),
              ) or item.fragile and (
                item().effect(game, cell=target_cell),
                game.floor.remove_elem(itemdrop)
              ) or (
                setattr(itemdrop, "cell", target_cell),
              ),
              game.anims[0].append(
                PauseAnim(
                  duration=30,
                  on_end=lambda:(
                    game.step(),
                    game.camera.blur()
                  )
                )
              )
            )
          )),
          game.camera.focus(target_cell) #, tween=True, speed=throw_anim.duration),
        )
      )
    ])
    return True

  def use_skill(game, actor, skill, dest=None, on_end=None):
    camera = game.camera
    if actor.faction == "player":
      game.store.sp -= skill.cost
    if skill.kind == "weapon":
      actor_x, actor_y = actor.cell
      facing_x, facing_y = actor.facing
      target_cell = (actor_x + facing_x, actor_y + facing_y)
      target = next((e for e in game.floor.elems if (
        isinstance(e, DungeonActor)
        and e.faction == "enemy"
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
        camera.focus(target_cell)
        game.anims.append([
          AttackAnim(
            target=actor,
            src=actor.cell,
            dest=target_cell,
            on_end=lambda: (
              camera.blur(),
              game.step()
            )
          )
        ])
    else:
      target_cell = skill.effect(actor, dest, game, on_end=lambda: (
        on_end() if on_end else (
          camera.blur(),
          actor is game.hero and game.step(),
          game.refresh_fov()
        )
      ))
      if target_cell or target_cell is False:
        if target_cell:
          camera.focus(target_cell, force=True)
        if ENABLED_COMBAT_LOG:
          game.log.print((actor.token(), " uses ", skill().token()))
        elif skill.name:
          game.log.exit()
          game.display_skill(skill, user=actor)
      else:
        camera.focus(actor.cell, speed=8, force=True)

  def display_skill(game, skill, user):
    prev_skill_banner = next((c for c in game.comps if type(c) is SkillBanner), None)
    if prev_skill_banner:
      prev_skill_banner.exit()
    game.comps.append(SkillBanner(
      text=skill.name,
      color=user.color(),
    ))

  def full_restore(game, actor=None):
    if actor is None:
      for actor in game.party:
        game.full_restore(actor)
      return
    actor.regen(actor.get_hp_max())
    actor.dispel_ailment()
    game.numbers.append(DamageValue(actor.get_hp_max(), add_vector(actor.cell, (0, -0.25)), color=GREEN))
    game.numbers.append(DamageValue(game.get_sp_max(), actor.cell, color=CYAN))
    game.store.sp = game.store.sp_max

  def use_oasis(game):
    if game.oasis_used:
      return
    game.oasis_used = True
    game.log.print("You use the oasis")
    floor = game.floor
    palm = next((e for e in floor.elems if type(e) is Palm), None)
    if not palm:
      game.anims.append([PauseAnim(
        duration=120,
        on_end=lambda: game.log.print("But nothing happened...")
      )])
      return

    palm.vanish(game)

    hero = game.hero
    game.full_restore(hero)

    ally = game.ally
    if ally:
      if ally.is_dead():
        ally.revive()
        floor.spawn_elem_at(add_vector(hero.cell, (-1, 0)), ally)
      game.full_restore(ally)
      game.log.print("The party's HP and SP has been restored.")
    else:
      game.log.print("Your HP and SP have been restored.")

    game.anims.append([PauseAnim(duration=60)])

  def learn_skill(game, skill):
    game.parent.learn_skill(skill)

  def handle_ascend(game):
    if game.floor.get_tile_at(game.hero.cell) is not Stage.STAIRS_UP:
      return game.log.print("There's nowhere to go up here!")
    game.ascend()

  def handle_exit(game):
    if game.floor.get_tile_at(game.hero.cell) is not Stage.EXIT:
      return game.log.print("There's nowhere to go up here!")
    game.leave_dungeon()

  def handle_descend(game):
    if game.floor.get_tile_at(game.hero.cell) is not Stage.STAIRS_DOWN:
      return game.log.print("There's nowhere to go down here!")
    gen = next((f for f in DungeonContext.FLOORS if f.__name__ == game.floor.generator), None)
    gen_index = DungeonContext.FLOORS.index(gen) if gen in DungeonContext.FLOORS else None
    if game.floors.index(game.floor) == 0 and not gen_index:
      return game.leave_dungeon()
    game.descend()

  def handle_floorchange(game, direction):
    for comp in game.comps:
      comp.exit()
    game.change_floors(direction)

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
    def remove_heroes():
      old_floor.remove_elem(game.hero)
      if game.ally and not game.ally.is_dead():
        old_floor.remove_elem(game.ally)

    gen_index = next((i for i, g in enumerate(DungeonContext.FLOORS) if g.__name__ == game.floor.generator), None)
    index = game.floors.index(game.floor) + direction
    if index >= len(game.floors) or index < 0:
      # create a new floor if out of bounds
      if gen_index is not None:
        Floor = DungeonContext.FLOORS[gen_index + direction]
      else:
        Floor = DebugFloor
      app = game.get_head()
      app.transition(
        transits=(DissolveIn(), DissolveOut()),
        loader=Floor.generate(game.store),
        on_end=lambda floor: (
          remove_heroes(),
          game.use_floor(floor, direction=direction, generator=Floor),
          game.log.print(direction == 1 and "You go upstairs." or "You go downstairs.")
        )
      )
    elif index >= 0:
      # go back to old floor if within bounds
      def change_floors():
        remove_heroes()
        new_floor = game.floors[index]
        stairs_x, stairs_y = new_floor.find_tile(entry_tile)
        new_floor.spawn_elem_at((stairs_x, stairs_y), game.hero)
        if game.ally and not game.ally.is_dead():
          new_floor.spawn_elem_at((stairs_x - 1, stairs_y), game.ally)
        game.floor = new_floor
        game.refresh_fov(moving=True)
        game.camera.reset()
        game.log.print((direction == 1
          and "You go back upstairs."
          or "You go back downstairs."))
      game.get_head().transition([
        DissolveIn(on_end=change_floors),
        DissolveOut()
      ])

    return True

  def leave_dungeon(game):
    app = game.get_head()
    app.transition([
      DissolveIn(on_end=lambda: game.parent.goto_town(returning=True)),
      DissolveOut()
    ])

  def toggle_lights(game):
    game.lights = not game.lights
    game.refresh_fov()
    return True

  def get_gold(game):
    return game.store.gold

  def change_gold(game, amount):
    game.store.gold += amount
    return game.store.gold

  def get_sp(game):
    return game.store.sp

  def get_sp_max(game):
    return MAX_SP

  def get_visible_cells(game, actor=None):
    return (actor or game.hero).visible_cells

  def get_visited_cells(game, floor=None):
    floor = floor or game.floor
    return next((cells for i, cells in enumerate(game.memory) if i is game.floors.index(floor)), None)

  def update_visited_cells(game, cells):
    visited_cells = game.get_visited_cells()
    for cell in cells:
      if cell not in visited_cells:
        visited_cells.append(cell)

  def update_camera(game):
    if game.camera.get_pos():
      old_x, old_y = game.camera.get_pos()
      game.camera.update(game)
      new_x, new_y = game.camera.get_pos()
      if game.anims and type(game.anims[0][0]) is StageView.FadeAnim and game.anims[0][0].time == 1:
        game.redraw_tiles(force=True)
      elif round(new_x - old_x) or round(new_y - old_y):
        game.redraw_tiles()
    else:
      game.camera.update(game)
      game.redraw_tiles()

  def update_bubble(game):
    hero = game.hero
    facing_cell = add_vector(hero.cell, hero.facing)
    facing_elems = game.floor.get_elems_at(facing_cell)
    facing_elem = next((e for e in facing_elems if (
      e.solid
      and e.active
      and (not isinstance(e, DungeonActor) or e.faction == "ally")
    )), None)
    if not game.talkbubble or facing_elem is not game.talkbubble.target:
      if game.talkbubble:
        game.talkbubble.done = True
        game.talkbubble = None
      if facing_elem and not facing_elem.hidden and not game.anims and not hero.item:
        bubble_cell = facing_cell
        game.talkbubble = TalkBubble(
          target=facing_elem,
          cell=bubble_cell,
          elev=Tile.get_elev(game.floor.get_tile_at(facing_cell)),
          flipped=game.camera.is_cell_beyond_yrange(bubble_cell),
        )
        game.vfx.append(game.talkbubble)

  def show_bubble(game):
    game.talkbubble and game.talkbubble.show()

  def hide_bubble(game):
    game.talkbubble and game.talkbubble.hide()

  def update(game):
    super().update()
    game.update_camera()

    for elem in game.floor.elems:
      elem_type = type(elem).__name__
      bench_tag = "update {}".format(elem_type)
      debug.bench(bench_tag)
      vfx = elem.update(game) or []
      vfx and game.vfx.extend(vfx)
      bench_diff = debug.bench(bench_tag, quiet=True)
      if bench_diff > 1:
        debug.log("update {} in {}ms".format(elem_type, bench_diff))

    for fx in game.vfx:
      if fx.kind:
        continue
      if fx.done:
        game.vfx.remove(fx)
      else:
        game.vfx += fx.update(game) or []

    if game.anims:
      group = game.anims[0]
      for anim in group:
        if anim is None:
          group.remove(anim)
          continue
        anim.update()
        if type(anim) is PauseAnim:
          break
      game.anims[0] = [a for a in game.anims[0] if not a.done]
      while game.anims and not game.anims[0]:
        game.anims.pop(0)
    for comp in game.comps:
      if "done" in dir(comp) and comp.done:
        game.comps.remove(comp)
    game.time += 1

  def view(game):
    sprites = []
    sprites += game.floor_view.view(game)
    if game.debug:
      sprites += game.minimap.view()
    else:
      for comp in game.comps:
        sprites += comp.view()
      if game.child or game.get_head().transits:
        if type(game.child) is InventoryContext:
          game.hide_bubble()
        else:
          for comp in [c for c in game.comps if c.active]:
            if (not (type(game.child) is MinimapContext and type(comp) is Minimap)
            and (not type(comp) is Log or type(game.child) is GameOverContext)
            and not (type(game.child) is SkillContext and (
              type(comp) is Hud
              or type(comp) is SpMeter
              or type(comp) is Minimap
            ))):
              comp.exit()
              game.hide_bubble()
      else:
        for comp in [c for c in game.comps if not c.active]:
          if type(comp) is not Log:
            comp.enter()
        game.show_bubble()
        game.update_bubble()

    if game.time < LABEL_FRAMES and not game.child:
      label_image = assets.ttf["normal"].render("Dungeon {}F".format(game.get_floor_no()), WHITE)
      label_image = outline(label_image, BLACK)
      label_image = outline(label_image, WHITE)
      sprites.append(Sprite(
        image=label_image,
        pos=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4),
        origin=("center", "center"),
        layer="ui"
      ))

    sprites += super().view()
    sprites.sort(key=lambda sprite: StageView.order(sprite))

    return sprites
