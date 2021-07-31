import math
from random import random, randint, choice
import pygame
from pygame import Rect
from copy import deepcopy
from dataclasses import dataclass
import json

import config
from config import (
  WINDOW_WIDTH,
  WINDOW_HEIGHT,
  WINDOW_SIZE,
  VISION_RANGE,
  MOVE_DURATION,
  RUN_DURATION,
  JUMP_DURATION,
  PUSH_DURATION,
  NUDGE_DURATION,
  FLICKER_DURATION,
  LABEL_FRAMES,
  ENABLED_COMBAT_LOG
)

import keyboard
from keyboard import ARROW_DELTAS, key_times

import debug

from lib.cell import add as add_vector, is_adjacent, manhattan, normal
import lib.direction as direction
from lib.compose import compose

import assets
from assets import load as load_assets
from sprite import Sprite
from filters import recolor, replace_color, outline
from colors.palette import BLACK, WHITE, RED, GREEN, BLUE, YELLOW, CYAN
from text import render as render_text
from transits.dissolve import DissolveIn, DissolveOut

import dungeon.gen as gen
from dungeon.fov import shadowcast
from dungeon.camera import Camera
from dungeon.stage import Stage, Tile
from dungeon.stageview import StageView

from dungeon.actors import DungeonActor
from dungeon.actors.eye import Eyeball
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

from comps.damage import DamageValue
from comps.hud import Hud
from comps.log import Log, Message, Token
from comps.minimap import Minimap
from comps.previews import Previews
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

from dungeon.data import DungeonData
from dungeon.command import MoveCommand, MoveToCommand, PushCommand, SkillCommand

def manifest(core):
  if type(core) is Knight: return KnightActor(core)
  if type(core) is Mage: return MageActor(core)

class DungeonContext(Context):
  ATTACK_DURATION = 12
  FLINCH_DURATION = 25
  FLINCH_PAUSE_DURATION = 15
  PAUSE_DURATION = 15
  PAUSE_ITEM_DURATION = 30
  PAUSE_DEATH_DURATION = 45
  AWAKEN_DURATION = 45
  FLOORS = [Floor1, Floor2, Floor3]

  def __init__(game, party, floors, floor_index=0, memory=[]):
    super().__init__()
    game.hero = manifest(party[0])
    game.ally = manifest(party[1]) if len(party) == 2 else None
    game.party = [game.hero, game.ally] if game.ally else [game.hero]
    game.floors = floors
    game.floor = floors[floor_index]
    game.floor_view = None
    game.floor_cells = None
    game.memory = memory
    game.room = None
    game.room_within = None
    game.room_entrances = {}
    game.rooms_entered = []
    game.oasis_used = False
    game.anims = []
    game.commands = []
    game.vfx = []
    game.numbers = []
    game.keys_rejected = {}
    game.seeds = []
    game.lights = False
    game.god_mode = False
    game.camera = Camera(WINDOW_SIZE)
    game.log = None
    game.minimap = None
    game.comps = []
    game.debug = False
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
      Hud(party=game.parent.party, hp=True),
      Previews(parent=game),
      FloorNo(parent=game),
      SpMeter(parent=game.parent)
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
    return gen_index + 1 if gen_index is not None else '??'

  def get_inventory(game):
    return game.parent.inventory.items

  def save(game):
    return DungeonData(
      floor_index=game.floors.index(game.floor),
      floors=deepcopy(game.floors),
      memory=deepcopy(game.memory)
    )

  def use_floor(game, floor, direction=1, generator=None):
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
      and e.get_faction() == "player"
      and type(e.core) is type(game.parent.party[0])
    )), None)
    if hero:
      game.hero = hero
      hero.core = game.parent.party[0]
    else:
      hero = game.hero
      hero.facing = (1, 0)
      floor.spawn_elem_at(direction == 1 and floor.entrance or floor.exit, hero)

      ally = game.ally
      if ally and not ally.is_dead():
        x, y = floor.entrance
        ally.facing = (1, 0)
        floor.spawn_elem_at((x - 1, y), ally)

    enemies = [e for e in floor.elems if isinstance(e, DungeonActor) and not hero.allied(e)]
    for monster, kills in game.parent.monster_kills.items():
      if (monster.skill is not None
      and monster.skill not in game.parent.skill_pool
      and kills >= 3):
        enemy = next((e for e in enemies if type(e) is monster), None)
        if enemy is not None:
          enemy.promote()

    game.room = None
    game.anims = []
    game.commands = []
    game.refresh_fov(moving=True)
    game.rooms_entered.append(game.room)
    game.camera.reset()
    game.camera.update(game)
    game.floor_view = StageView(WINDOW_SIZE)
    game.redraw_tiles()
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
    hero = game.hero
    floor = game.floor
    visible_cells = []

    def is_within_room(room, cell):
      _, room_y = room.cell
      room_cells = room.get_cells() + room.get_border()
      return hero.cell in [(x, y) for (x, y) in room_cells if (
        y != room_y + room.get_height() + 1
        and y != room_y - 2
      )]

    door = None
    new_room = None
    if moving:
      rooms = [room for room in floor.rooms if is_within_room(room, hero.cell)]
      room_within = next((r for r in floor.rooms if hero.cell in r.get_cells()), None)
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
        game.room_entrances[room] = hero.cell
        if game.room:
          room_cells = room.get_cells() + room.get_border()
          game.camera.illuminate(room, actor=game.hero)
          game.log.exit()
          def illuminate():
            hero.visible_cells = room_cells
            game.redraw_tiles(force=True)
          game.anims[0].append(PauseAnim(duration=45))
          game.anims += [
            [StageView.FadeAnim(
              target=room_cells,
              duration=15,
              on_start=lambda: game.update_visited_cells(room_cells),
              on_end=illuminate
            )],
            [PauseAnim(duration=15)]
          ]
      game.room = room
      game.room_within = room_within

    if game.lights:
      if not game.floor_cells:
        game.floor_cells = game.floor.get_visible_cells()
      visible_cells = game.floor_cells
    elif not game.camera.anims:
      visible_cells = shadowcast(floor, hero.cell, VISION_RANGE)
      if game.room:
        visible_cells += game.room.get_cells() + game.room.get_border()

    if not game.camera.anims:
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

  def step(game, run=False, moving=False):
    commands = {}
    ally = game.ally
    if ally:
      command = game.step_ally(ally)
      if type(command) is tuple:
        commands[ally] = command

    hero = game.hero
    hero.step_ailment(game)
    actors = [e for e in game.floor.elems if isinstance(e, DungeonActor) and e is not hero]
    enemies = [a for a in actors if not a.allied(hero)]
    enemies.sort(key=lambda e: type(e) is MageActor and 1000 or manhattan(e.cell, hero.cell))

    for actor in actors:
      spd = actor.stats.ag / hero.stats.ag
      actor.turns += spd

    for actor in actors:
      if actor.is_dead():
        continue
      while actor.turns >= 1:
        actor.turns -= 1
        if actor in enemies and actor is not ally:
          command = game.step_enemy(actor)
          if type(command) is tuple:
            if actor in commands:
              commands[actor].append(command)
            else:
              commands[actor] = [command]
        if game.room and actor.cell in game.room.get_cells():
          actor.step_ailment(game)
        if actor.counter:
          actor.counter = max(0, actor.counter - 1)

    end_exec = lambda: game.end_step(moving=moving)
    start_exec = lambda: game.next_command(on_end=end_exec)
    if commands:
      COMMAND_PRIORITY = ["move", "move_to", "use_skill", "attack"]
      game.commands = sorted(commands.items(), key=lambda item: COMMAND_PRIORITY.index(item[1][0][0]))
      if (hero.command
      and hero.command.on_end
      and not (type(hero.command) is MoveCommand and game.commands[0][1][0][0].startswith("move"))):
        hero.command.on_end = compose(hero.command.on_end, start_exec)
      else:
        start_exec()
    elif hero.command and hero.command.on_end:
      hero.command.on_end = compose(hero.command.on_end, end_exec)
    else:
      end_exec()

  def next_command(game, on_end=None):
    if not game.commands:
      return on_end and on_end()
    step = lambda: (
      not (game.commands[0] and game.commands[0][1]) and game.commands.pop(0),
      game.next_command(on_end)
    )
    actor, commands = game.commands[0]
    cmd_name, *cmd_args = commands.pop(0)
    if actor.is_immobile():
      return step()
    if cmd_name == "use_skill":
      return game.use_skill(actor, *cmd_args, on_end=step)
    if cmd_name == "attack":
      return game.attack(actor, *cmd_args, on_end=step)
    if cmd_name == "move":
      if commands:
        return game.move(actor, *cmd_args, on_end=step)
      else:
        game.move(actor, *cmd_args)
        return step()
    if cmd_name == "move_to":
      if commands:
        return game.move_to(actor, *cmd_args, on_end=step)
      else:
        game.move_to(actor, *cmd_args)
        return step()

  def end_step(game, moving=False):
    actors = [e for e in game.floor.elems if isinstance(e, DungeonActor)]
    for actor in actors:
      actor.command = None
    hero = game.hero
    if hero.ailment == "sleep":
      if hero.get_hp() == hero.get_hp_max():
        hero.dispel_ailment()
      else:
        game.anims.append([PauseAnim(
          duration=5,
          on_end=game.step
        )])
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

  def step_enemy(game, enemy):
    if not enemy.can_step():
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
      enemies.sort(key=lambda e: manhattan(e.cell, actor.cell) + random() / 2)
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
    if key in game.keys_rejected:
      del game.keys_rejected[key]

  def handle_keydown(game, key):
    if game.child:
      return game.child.handle_keydown(key)

    if game.anims or game.commands or game.get_head().transits or game.hero and game.hero.core.anims:
      return False

    # debug functionality
    ctrl = keyboard.get_pressed(pygame.K_LCTRL) or keyboard.get_pressed(pygame.K_RCTRL)
    shift = keyboard.get_pressed(pygame.K_LSHIFT) or keyboard.get_pressed(pygame.K_RSHIFT)
    if keyboard.get_pressed(key) == 1 and ctrl:
      game.keys_rejected[key] = True
      if key == pygame.K_ESCAPE:
        return game.toggle_lights()
      if key == pygame.K_s and shift:
        return print(game.parent.seeds)
      if key == pygame.K_s:
        return print(game.floor.seed)
      if key == pygame.K_d and shift:
        return game.handle_debug_toggle()
      if key == pygame.K_d:
        return game.handle_debug()
      if key == pygame.K_p:
        return print(game.hero.cell)

    if key in ARROW_DELTAS:
      moved = game.handle_move(delta=ARROW_DELTAS[key], run=shift)
      if not moved:
        if key not in game.keys_rejected:
          game.keys_rejected[key] = 0
        game.keys_rejected[key] += 1
        if game.keys_rejected[key] >= 30:
          game.handle_push()
      return moved

    if ((key == pygame.K_BACKSLASH or key == pygame.K_BACKQUOTE)
    and keyboard.get_pressed(key) > 30):
      return game.handle_sleep()

    if keyboard.get_pressed(key) != 1:
      return False

    if key == pygame.K_TAB:
      return game.handle_swap()

    if key == pygame.K_f:
      return game.handle_examine()

    if key == pygame.K_m:
      return game.handle_minimap()

    if game.hero.is_dead() or game.hero.ailment == "sleep":
      return False

    if key == pygame.K_BACKSLASH or key == pygame.K_BACKQUOTE:
      return game.handle_wait()

    if key == pygame.K_RETURN or key == pygame.K_SPACE:
      if game.floor.get_tile_at(game.hero.cell) is Stage.STAIRS_UP:
        return game.handle_ascend()
      elif game.floor.get_tile_at(game.hero.cell) is Stage.STAIRS_DOWN:
        return game.handle_descend()

    if key == pygame.K_RETURN:
      return game.handle_skill()

    if key == pygame.K_SPACE:
      return game.handle_action()

    return None

  def handle_sleep(game):
    hero = game.hero
    floor = game.floor
    visible_actors = [floor.get_elem_at(c, superclass=DungeonActor) for c in hero.visible_cells]
    visible_enemies = [e for e in visible_actors if e and not e.allied(hero)]
    if hero.ailment or visible_enemies:
      return False
    hero.inflict_ailment("sleep")
    hero.command = None
    game.step()
    return True

  def handle_move(game, delta, run=False):
    hero = game.hero
    ally = game.ally
    floor = game.floor

    if hero.ailment == "freeze":
      hero.step_ailment(game)
      game.anims.append([
        ShakeAnim(duration=15, target=hero)
      ])
      if hero.ailment:
        game.step(moving=True)
        return True
      else:
        return

    if not hero.can_step():
      return False

    old_cell = hero.cell
    hero_x, hero_y = old_cell
    delta_x, delta_y = delta
    acted = False
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_tile = floor.get_tile_at(target_cell)
    target_elem = floor.get_elem_at(target_cell)
    if isinstance(target_elem, Door) and not target_elem.solid:
      target_elem = floor.get_elem_at(target_cell, exclude=[Door])

    def on_move():
      if not moved:
        return False

      origin_elem = game.floor.get_elem_at(old_cell, exclude=[Door])
      if origin_elem:
        origin_elem.aftereffect(game)

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

      # if not make_sound(1 / 10)
      is_waking_up = False
      if game.room:
        room = game.room
        room_elems = [a for a in [floor.get_elem_at(cell) for cell in room.get_cells()] if a]
        enemies = [e for e in room_elems if isinstance(e, DungeonActor) and not hero.allied(e)]
        enemy = next((e for e in enemies if e.ailment == "sleep" and randint(1, 10) == 1), None)
        if enemy:
          enemy.wake_up()
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
      if game.parent.sp:
        if not hero.is_dead() and not hero.ailment == "sleep":
          hero.regen()
        if ally and not ally.is_dead() and not ally.ailment == "sleep":
          ally.regen()

      # deplete sp
      if target_tile is not Stage.OASIS:
        game.parent.deplete_sp(1 / 100)

    if hero.get_facing() != delta:
      hero.set_facing(delta)
      game.update_bubble()

    moved = game.move(actor=hero, delta=delta, run=run, on_end=on_move)
    if moved:
      ally and game.step_ally(ally, run, old_cell)
      game.step(moving=True)
    elif target_tile is Stage.PIT:
      moved = game.jump_pit(hero, run, on_move)
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
    if target.static or target_tile is None or target_tile.solid or target_tile.elev or target_elem and target_elem.solid:
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
    return True

  def obtain(game, item):
    if isinstance(item, Gold):
      game.change_gold(item.amount)
    elif type(item) is type and issubclass(item, Skill):
      game.learn_skill(item)
    else:
      game.parent.obtain(item)
    return True

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
    target_cell = add_vector(hero.cell, hero.get_facing())
    target_actor = game.floor.get_elem_at(target_cell, superclass=DungeonActor)
    if target_actor and not hero.allied(target_actor):
      if not hero.weapon:
        hero.weapon = hero.find_weapon()
      if hero.weapon:
        game.parent.deplete_sp(hero.weapon.cost)
        return game.attack(hero, target_actor, on_end=game.step)
      return False
    target_elem = game.floor.get_elem_at(target_cell)
    if not target_elem or not target_elem.active:
      return False
    effect_result = target_elem and target_elem.effect(game)
    if game.talkbubble:
      game.talkbubble.hide()
    def bump():
      anim = AttackAnim(
        duration=DungeonContext.ATTACK_DURATION,
        target=hero,
        src=hero.cell,
        dest=target_cell
      )
      not game.anims and game.anims.append([])
      game.anims[-1].append(anim)
    if not game.anims or not next((a for a in game.anims[0] if a.target is hero), None):
      bump()
    if effect_result == True:
      game.step()

  def handle_wait(game):
    game.step()

  def handle_swap(game):
    if not game.ally or game.ally.is_dead():
      return False
    game.hero, game.ally = game.ally, game.hero
    game.parent.swap_chars()
    game.refresh_fov(moving=True)
    return True

  def recruit(game, actor):
    game.parent.recruit(actor.core)
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

  def move(game, actor, delta, run=False, jump=False, duration=0, on_end=None):
    origin_tile = game.floor.get_tile_at(actor.cell)
    origin_elev = origin_tile and origin_tile.elev
    actor_x, actor_y = actor.cell
    delta_x, delta_y = delta
    target_cell = (actor_x + delta_x, actor_y + delta_y)
    target_tile = game.floor.get_tile_at(target_cell)
    target_elem = game.floor.get_elem_at(target_cell)
    facing_x = -1 if delta_x < 0 else 1 if delta_x > 0 else 0
    facing_y = -1 if delta_y < 0 else 1 if delta_y > 0 else 0
    actor.facing = (facing_x, facing_y)
    if (target_tile and not target_tile.solid
    and abs(target_tile.elev - origin_tile.elev) < 1
    and (target_tile.direction == (0, 0) and origin_tile.direction == (0, 0)
      or direction.normalize(delta) == direction.normalize(origin_tile.direction)
      or direction.normalize(delta) == direction.normalize(target_tile.direction))
    and (target_elem is None
      or not target_elem.solid
      or actor is game.hero and target_elem is game.ally and game.ally.can_step()
    )):
      duration = duration or (RUN_DURATION if run else MOVE_DURATION)
      duration = duration * 1.5 if jump else duration
      anim_kind = JumpAnim if jump else MoveAnim
      src_cell = (*actor.cell, max(0, origin_tile.elev))
      dest_cell = (*target_cell, max(0, target_tile.elev))
      command = MoveCommand(direction=delta, on_end=on_end)
      if not actor.command:
        actor.command = command
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
      actor.cell = target_cell
      actor.elev = target_tile.elev
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

  def move_to(game, actor, cell, run=False, on_end=None):
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

    if randint(0, 1):
      delta_x = select_x()
      if not delta_x:
        delta_y = select_y()
    else:
      delta_y = select_y()
      if not delta_y:
        delta_x = select_x()

    if delta_x or delta_y:
      return game.move(actor=actor, delta=(delta_x, delta_y), run=run, on_end=on_end)
    else:
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
      chance=0.125
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
      and defender.get_facing() == direction.invert(attacker.get_facing())
      and (type(defender.command) is not SkillCommand
        or game.roll_block(attacker=attacker, defender=defender))
    )

  def find_damage(game, actor, target, modifier=1):
    actor_str = actor.get_str() * modifier
    target_def = target.get_def()
    if game.floor.get_elem_at(target.cell, superclass=Door):
      target_def = max(0, target_def - 2)
    if game.can_block(attacker=actor, defender=target):
      target_def *= 1.5
    variance = 1 if actor.core.faction == "enemy" else 2
    return max(0, actor_str - target_def + randint(-variance, variance))

  def attack(game, actor, target, damage=None, modifier=1, on_connect=None, on_end=None):
    actor.weapon = actor.find_weapon()
    if actor.weapon is None:
      return False

    if damage is None:
      damage = game.find_damage(actor, target, modifier)
      if ENABLED_COMBAT_LOG:
        game.log.print((actor.token(), " uses ", actor.weapon().token()))

    actor.face(target.cell)

    crit = game.roll_crit(attacker=actor, defender=target)
    block = game.can_block(attacker=actor, defender=target)
    if (not target.is_immobile()
    and not game.roll_hit(attacker=actor, defender=target)
    and (not block or randint(0, 1))):
      damage = None
    elif block:
      damage = 0
      target.block()
    elif crit:
      damage = game.find_damage(actor, target, modifier=1.5)

    def connect():
      on_connect and on_connect()

      real_target = actor if target.counter else target
      real_damage = damage
      if target.counter:
        ENABLED_COMBAT_LOG and game.log.print((target.token(), " reflected the attack!"))
        # target.counter = False
        real_target = actor
        real_damage = DungeonActor.find_damage(actor, actor)

      def end_attack():
        on_end = command.on_end
        command.on_end = None
        on_end and on_end()

      game.flinch(
        target=real_target,
        damage=real_damage,
        direction=actor.facing,
        crit=crit,
        on_end=end_attack
      )

    command = SkillCommand(skill=actor.weapon, on_end=on_end)
    actor.command = command
    game.anims.append([
      AttackAnim(
        duration=DungeonContext.ATTACK_DURATION,
        delay=(block and 12 or 0),
        target=actor,
        src=actor.cell,
        dest=target.cell,
        on_connect=connect,
      )
    ])

    return True

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
      if not hero.allied(target):
        game.parent.record_kill(target)
        enemy_skill = type(target).skill
        enemy_drops = type(target).drops
        if enemy_skill and target.rare:
          skill = enemy_skill
          if skill not in game.parent.skill_pool:
            game.floor.spawn_elem_at(target.cell, Soul(contents=skill))
        elif (enemy_drops
        and randint(1, 3) == 1
        and not game.floor.get_tile_at(target.cell) is Stage.PIT
        and not game.floor.get_elem_at(target.cell, superclass=Bag)):
          drop = choice(enemy_drops)
          game.floor.spawn_elem_at(target.cell, Bag(contents=drop))
      target.kill()
      if target in game.floor.elems:
        game.floor.elems.remove(target)
      if game.room:
        game.room.on_death(game, target)
      if target is hero:
        game.anims[0].append(PauseAnim(
          duration=DungeonContext.PAUSE_DEATH_DURATION,
          on_end=lambda: (
            game.handle_swap()
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

    if game.god_mode and target is game.hero:
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
    game.numbers.append(DamageValue(
      text=damage_text,
      cell=target.cell
    ))

    if damage and crit:
      game.numbers.insert(0, DamageValue(
        text="CRITICAL!",
        cell=target.cell,
        offset=(4, -4),
        color=YELLOW,
        delay=15
      ))
      game.vfx.append(FlashVfx())
      game.floor_view.shake(vertical=direction[1])
      game.nudge(target, direction)
      target.turns = 0

    if damage == None:
      flinch = None
    elif int(damage) == 0 or block:
      flinch = ShakeAnim(
        target=target,
        magnitude=0.5,
        duration=15
      )
    else:
      flinch = FlinchAnim(
        target=target,
        duration=DungeonContext.FLINCH_DURATION,
        direction=direction
      )
      target.damage(damage)

    pause = PauseAnim(duration=DungeonContext.FLINCH_PAUSE_DURATION, on_end=respond)
    if delayed or not game.anims:
      game.anims.append([*(flinch and [flinch] or []), pause])
    else:
      game.anims[0] += [*(flinch and [flinch] or []), pause]

    if was_asleep and not target.ailment == "sleep" and not target.is_dead():
      game.anims.append([AwakenAnim(
        duration=DungeonContext.AWAKEN_DURATION,
        target=target,
        on_end=awaken
      )])

  def freeze(game, target):
    if target.is_dead():
      return False
    target.inflict_ailment("freeze")
    if ENABLED_COMBAT_LOG:
      game.log.print((target.token(), " is frozen.")),
    game.numbers.append(DamageValue(
      text="FROZEN",
      cell=target.cell,
      offset=(4, -4),
      color=CYAN,
      delay=15
    ))
    return True

  def use_item(game, item):
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
      success, message = item.use(item, game)
    if success:
      game.log.print(("Used ", item.token(item)))
      game.log.print(message)
      game.parent.inventory.items.remove(item)
      return True, None
    else:
      game.anims.pop()
      return False, message

  def use_skill(game, actor, skill, dest=None, on_end=None):
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
      if ENABLED_COMBAT_LOG:
        game.log.print((actor.token(), " uses ", skill().token()))
      else:
        game.log.exit()
        game.comps.append(SkillBanner(
          text=skill.name,
          color=actor.color(),
        ))
      target_cell = skill.effect(actor, dest, game, on_end=lambda: (
        on_end() if on_end else (
          camera.blur(),
          actor is game.hero and game.step(),
          game.refresh_fov()
        )
      ))
      if target_cell:
        camera.focus(target_cell, force=True)

  def full_restore(game):
    hero = game.hero
    hero.regen(hero.get_hp_max())
    hero.dispel_ailment()
    game.numbers.append(DamageValue(hero.get_hp_max(), add_vector(hero.cell, (0, -0.25)), color=GREEN))
    game.numbers.append(DamageValue(game.get_sp_max(), hero.cell, color=CYAN))
    game.parent.regen_sp()

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
    game.full_restore()

    ally = game.ally
    if ally:
      if ally.is_dead():
        ally.revive()
        floor.spawn_elem_at(add_vector(hero.cell, (-1, 0)), ally)
      game.numbers.append(DamageValue(ally.get_hp_max(), add_vector(ally.cell, (0, -0.25)), GREEN))
      game.numbers.append(DamageValue(game.get_sp_max(), ally.cell, CYAN))
      ally.regen(ally.get_hp_max())
      ally.dispel_ailment()
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
      if gen_index is None:
        return game.leave_dungeon()
      app = game.get_head()
      Floor = DungeonContext.FLOORS[gen_index + direction]
      app.transition(
        transits=(DissolveIn(), DissolveOut()),
        loader=Floor.generate(game.parent.story),
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
    return game.parent.get_gold()

  def change_gold(game, amount):
    return game.parent.change_gold(amount)

  def get_sp(game):
    return game.parent.get_sp()

  def get_sp_max(game):
    return game.parent.get_sp_max()

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
      and (not isinstance(e, DungeonActor) or hero.allied(e))
    )), None)
    if game.talkbubble:
      game.talkbubble.done = True
      game.talkbubble = None
    if facing_elem:
      game.talkbubble = TalkBubble(cell=facing_cell)
      game.vfx.append(game.talkbubble)

  def show_bubble(game):
    game.talkbubble and game.talkbubble.show()

  def hide_bubble(game):
    game.talkbubble and game.talkbubble.hide()

  def update(game):
    super().update()
    game.update_camera()

    for elem in game.floor.elems:
      vfx = elem.update(game) or []
      vfx and game.vfx.extend(vfx)

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
        anim.update()
        if anim.done:
          group.remove(anim)
        if type(anim) is PauseAnim:
          break
      if not group:
        game.anims.remove(group)
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
      if game.child and type(game.child) is not InventoryContext or game.get_head().transits:
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
      label_image = assets.ttf["roman"].render("Dungeon {}F".format(game.get_floor_no()), WHITE)
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
