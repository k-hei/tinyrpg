import math
import random
import pygame
from pygame import Rect

from contexts import Context
from assets import load as load_assets
from text import render as render_text
from filters import recolor, replace_color
from stage import Stage
from keyboard import key_times, ARROW_DELTAS
from cell import is_adjacent, manhattan

import gen
import fov
import config
import palette
import keyboard

from camera import Camera
from comps.hud import Hud
from comps.log import Log, Message, Token
from comps.minimap import Minimap
from comps.previews import Previews
from comps.damage import DamageValue
from comps.spmeter import SpMeter

from transits.dissolve import DissolveOut

from contexts.inventory import InventoryContext
from contexts.skill import SkillContext
from contexts.custom import CustomContext
from contexts.examine import ExamineContext
from contexts.minimap import MinimapContext

from actors import Actor
from actors.knight import Knight
from actors.mage import Mage
from actors.eye import Eye
from actors.mimic import Mimic
from actors.npc import NPC
from props.chest import Chest
from props.soul import Soul

from items import get_color as get_item_color

from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.pause import PauseAnim
from anims.awaken import AwakenAnim
from anims.activate import ActivateAnim
from anims.chest import ChestAnim

class DungeonContext(Context):
  MOVE_DURATION = 16
  RUN_DURATION = 12
  ATTACK_DURATION = 12
  FLINCH_DURATION = 25
  FLINCH_PAUSE_DURATION = 60
  FLICKER_DURATION = 30
  PAUSE_DURATION = 15
  PAUSE_ITEM_DURATION = 30
  PAUSE_DEATH_DURATION = 45
  AWAKEN_DURATION = 45
  VISION_RANGE = 3.5

  def __init__(game, parent):
    super().__init__(parent)
    game.hero = parent.hero
    game.ally = parent.ally
    game.new_skills = parent.new_skills
    game.skill_pool = parent.skill_pool
    game.skill_builds = parent.skill_builds
    game.monster_kills = parent.monster_kills
    game.skill_selected = { game.hero: None, game.ally: None }
    game.room = None
    game.floor = None
    game.floors = []
    game.memory = []
    game.anims = []
    game.vfx = []
    game.numbers = []
    game.key_requires_reset = {}
    game.log = Log()
    game.camera = Camera(config.WINDOW_SIZE)
    game.hud = Hud()
    game.sp_meter = SpMeter()
    game.minimap = Minimap(parent=game)
    game.previews = Previews()
    game.update_skills()
    game.create_floor()

  def get_floor_no(game):
    return len(game.floors) + 1

  def create_floor(game):
    floor_no = game.get_floor_no()
    if floor_no == config.TOP_FLOOR:
      floor = gen.top_floor()
    elif floor_no == 3:
      floor = gen.giant_room((19, 19))
    else:
      floor = gen.dungeon((27, 27), floor_no)

    promoted = False
    enemies = [e for e in floor.elems if isinstance(e, Actor) and e.faction == "enemy"]
    for monster, kills in game.monster_kills.items():
      if (monster.skill is not None
      and monster.skill not in game.skill_pool
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

    hero = game.hero
    ally = game.ally
    floor.spawn_elem(hero, floor.entrance)
    hero.facing = (1, 0)
    if not ally.dead:
      x, y = floor.entrance
      floor.spawn_elem(ally, (x - 1, y))
      ally.facing = (1, 0)

    game.floor = floor
    game.floors.append(game.floor)
    game.memory.append((game.floor, []))
    game.refresh_fov(moving=True)

  def refresh_fov(game, moving=False):
    visible_cells = fov.shadowcast(game.floor, game.hero.cell, DungeonContext.VISION_RANGE)

    if moving:
      rooms = [room for room in game.floor.rooms if game.hero.cell in room.get_cells() + room.get_border()]
      old_room = game.room
      if len(rooms) == 1:
        new_room = rooms[0]
      else:
        new_room = next((room for room in rooms if room is not game.room), None)
      if new_room is not old_room:
        game.room = new_room

    if game.room:
      visible_cells += game.room.get_cells() + game.room.get_border()

    # for cell in visible_cells:
    #   col, row = cell
    #   cell_above = (col, row - 1)
    #   cell_below = (col, row + 1)
    #   tile_below = game.floor.get_tile_at(cell_below)
    #   if (game.floor.get_tile_at(cell) is Stage.WALL and (
    #     tile_below is Stage.FLOOR
    #     or tile_below is Stage.DOOR
    #     or tile_below is Stage.DOOR_OPEN
    #   ) and cell_above not in visible_cells):
    #     visible_cells.append(cell_above)

    visited_cells = next((cells for floor, cells in game.memory if floor is game.floor), None)
    for cell in visible_cells:
      if cell not in visited_cells:
        visited_cells.append(cell)
    game.hero.visible_cells = visible_cells

    hero = game.hero
    camera = game.camera
    nearby_enemies = [e for e in game.floor.elems if (
      isinstance(e, Actor)
      and e.faction == "enemy"
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

    actors = [e for e in game.floor.elems if isinstance(e, Actor)]
    enemies = [a for a in actors if a.faction == "enemy"]

    for actor in actors:
      if actor in enemies:
        game.step_enemy(actor)

      if actor.ailment == "sleep":
        actor.regen(actor.get_hp_max() / 50)

      if actor.ailment == "poison":
        damage = int(actor.get_hp_max() * Actor.POISON_STRENGTH)
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
    if ally.stepped or ally.dead or ally.ailment == "sleep":
      return False
    hero = game.hero
    actors = [e for e in game.floor.elems if isinstance(e, Actor)]
    enemies = [a for a in actors if a.faction == "enemy"]
    adjacent_enemies = [e for e in enemies if is_adjacent(e.cell, ally.cell)]
    if adjacent_enemies:
      adjacent_enemies.sort(key=lambda e: e.get_hp())
      enemy = adjacent_enemies[0]
      game.attack(ally, enemy)
      ally.stepped = True
    elif old_hero_cell and is_adjacent(ally.cell, old_hero_cell):
      ally_x, ally_y = ally.cell
      old_x, old_y = old_hero_cell
      ally_delta = (old_x - ally_x, old_y - ally_y)
      ally.stepped = game.move(ally, ally_delta, run)
    elif enemies and not is_adjacent(ally.cell, hero.cell):
      enemies.sort(key=lambda e: e.get_hp())
      enemy = enemies[0]
      ally.stepped = game.move_to(ally, enemy.cell)
    elif not is_adjacent(ally.cell, hero.cell):
      ally.stepped = game.move_to(ally, hero.cell, run)
    if ally.stepped and len(game.anims) >= 2:
      game.anims[-2].append(game.anims.pop()[0])
    ally.stepped = True

  def step_enemy(game, enemy):
    if enemy.dead or enemy.stepped or enemy.idle or enemy.ailment == "sleep":
      return False

    hero = game.hero
    ally = game.ally
    rooms = [r for r in game.floor.rooms if enemy.cell in r.get_cells()]
    if len(rooms) == 0:
      return False

    room = rooms[0]
    room_cells = room.get_cells() + room.get_border()
    if hero.cell not in room_cells:
      return False

    return enemy.step(game)

  def find_closest_enemy(game, actor):
    enemies = [e for e in game.floor.elems if (
      isinstance(e, Actor)
      and not e.dead
      and e.faction != actor.faction
    )]
    if len(enemies) == 0:
      return None
    if len(enemies) > 1:
      enemies.sort(key=lambda e: manhattan(e.cell, actor.cell) + random.random() / 2)
    return enemies[0]

  def handle_keyup(game, key):
    game.key_requires_reset[key] = False

  def handle_keydown(game, key):
    if game.anims or game.log.anim or game.hud.anims:
      return False

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

    if key == pygame.K_ESCAPE and keyboard.get_pressed(pygame.K_LCTRL):
      return game.handle_debug()

    if game.hero.dead or game.hero.ailment == "sleep":
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
    if hero.dead or hero.ailment == "sleep":
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
      if target_tile is Stage.STAIRS_UP:
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

      is_waking_up = False
      if game.room:
        room = game.room
        room_elems = [a for a in [floor.get_elem_at(cell) for cell in room.get_cells()] if a]
        enemies = [e for e in room_elems if isinstance(e, Actor) and e.faction == "enemy"]
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
                  game.log.print(enemy.token() + " woke up!"),
                  game.anims[0].append(PauseAnim(
                    duration=DungeonContext.PAUSE_DURATION,
                    on_end=end_move
                  ))
                )
              )
            ])

      if not is_waking_up:
        end_move()

      if game.parent.sp:
        if not hero.dead and not hero.ailment == "sleep":
          hero.regen()
        if not ally.dead and not ally.ailment == "sleep":
          ally.regen()
      game.parent.sp = max(0, game.parent.sp - 1 / 100)

    moved = game.move(hero, delta, run, on_move)
    if moved:
      game.step_ally(game.ally, run, old_cell)
      acted = True
    elif isinstance(target_elem, Actor) and target_elem.faction == "enemy":
      if target_elem.idle:
        game.anims.append([
          AttackAnim(
            duration=DungeonContext.ATTACK_DURATION,
            target=hero,
            src_cell=hero.cell,
            dest_cell=target_cell
          ),
          PauseAnim(duration=15, on_end=lambda: (
            game.anims[0].append(ActivateAnim(
              duration=45,
              target=target_elem,
              on_end=lambda: (
                target_elem.activate(),
                game.log.print("The lamp was ", target_elem.token(), "!"),
                game.anims[0].append(PauseAnim(duration=15, on_end=lambda: (
                  game.step(),
                  game.refresh_fov()
                )))
              )
            ))
          ))
        ])
        game.log.print("You open the lamp")
      else:
        game.log.print(hero.token(), " attacks")
        game.attack(
          actor=hero,
          target=target_elem,
          on_end=lambda: (
            game.step(),
            game.refresh_fov()
          )
        )
        game.parent.sp = max(0, game.parent.sp - 1)
        acted = True
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
            game.parent.inventory.append(item)
            game.log.print("You open the lamp")
            game.log.print("Received ", Token(item.name, get_item_color(item)), ".")
            acted = True
          else:
            game.log.print("Your inventory is already full!")
        else:
          game.log.print("There's nothing left to take...")
        game.step(run)
        game.refresh_fov()
      elif isinstance(target_elem, Actor) and target_elem.ailment == "sleep" and target_elem.faction == "player":
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
      elif target_tile is Stage.DOOR:
        game.floor.set_tile_at(target_cell, Stage.DOOR_OPEN)
        game.step(run)
        game.refresh_fov()
      elif target_tile is Stage.DOOR_HIDDEN:
        game.log.print("Discovered a hidden door!")
        game.floor.set_tile_at(target_cell, Stage.DOOR_OPEN)
        game.step(run)
        game.refresh_fov()
      elif target_tile is Stage.DOOR_LOCKED:
        game.log.print("The door is locked...")
    return moved

  def handle_wait(game):
    game.step()

  def handle_swap(game):
    if game.ally.dead:
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
        on_close=lambda skill: (
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
      game.sp_meter.exit()
      game.child = MinimapContext(
        parent=game,
        minimap=game.minimap,
        on_close=lambda _: (
          game.hud.enter(),
          game.sp_meter.enter(),
          game.refresh_fov()
        )
      )

  def handle_debug(game):
    game.memory[game.floors.index(game.floor)] = (game.floor, game.floor.get_cells())

  def move(game, actor, delta, run=False, on_end=None):
    actor_x, actor_y = actor.cell
    delta_x, delta_y = delta
    target_cell = (actor_x + delta_x, actor_y + delta_y)
    target_tile = game.floor.get_tile_at(target_cell)
    target_elem = game.floor.get_elem_at(target_cell)
    actor.facing = delta
    if target_tile and not target_tile.solid and (
    (target_elem is None or not target_elem.solid)
    or actor is game.hero
    and target_elem is game.ally
    and not game.ally.ailment == "sleep"):
      duration = DungeonContext.RUN_DURATION if run else DungeonContext.MOVE_DURATION
      anim = MoveAnim(
        duration=duration,
        target=actor,
        src_cell=actor.cell,
        dest_cell=target_cell,
        on_end=on_end
      )
      if game.anims and actor.faction == "enemy":
        game.anims[0].append(anim)
      else:
        game.anims.append([anim])
      actor.cell = target_cell
      return True
    else:
      return False

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
      return game.move(actor, (delta_x, delta_y), run, on_end=game.refresh_fov)
    else:
      return False

  def attack(game, actor, target, damage=None, on_connect=None, on_end=None):
    if not damage:
      damage = Actor.find_damage(actor, target)
    def connect():
      if on_connect:
        on_connect()
      real_target = actor if target.counter else target
      real_damage = damage
      if target.counter:
        game.log.print(actor.token(), " reflected the attack!")
        # target.counter = False
        real_target = actor
        real_damage = Actor.find_damage(actor, actor)
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
    def remove():
      if target.faction == "enemy" and type(target).skill:
        game.monster_kills[type(target)] = game.monster_kills[type(target)] + 1 if type(target) in game.monster_kills else 0
        if target.rare:
          skill = type(target).skill
          if skill not in game.skill_pool:
            game.floor.spawn_elem(Soul(skill), target.cell)
      target.kill()
      game.floor.elems.remove(target)
      if target is game.hero:
        game.anims[0].append(PauseAnim(
          duration=DungeonContext.PAUSE_DEATH_DURATION,
          on_end=lambda: (
            game.handle_swap(),
            on_end and on_end()
          )
        ))
      else:
        trap = game.floor.find_tile(Stage.MONSTER_DEN)
        if trap and len([e for e in game.floor.elems if isinstance(e, Actor) and e.faction == "enemy"]) == 0:
          trap_x, trap_y = trap
          game.floor.set_tile_at((trap_x - 2, trap_y), Stage.DOOR_OPEN)
        if on_end:
          on_end()

    if target.faction == "enemy":
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
    if target.dead: end()

    def awaken():
      game.log.print(target.token(), " woke up!")
      game.anims[0].append(PauseAnim(duration=DungeonContext.PAUSE_DURATION))

    def respond():
      if target.dead or game.floor.get_tile_at(target.cell) is Stage.PIT:
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
        game.log.print(target.token(),
          (" receives" if target.faction == "enemy" else " suffers")
          + " " + str(damage) + " damage.")
      )
    )

    pause = PauseAnim(duration=DungeonContext.FLINCH_PAUSE_DURATION, on_end=respond)

    if delayed:
      game.anims.append([flinch, pause])
    else:
      game.anims[0].extend([flinch, pause])
    if was_asleep and not target.ailment == "sleep" and not target.dead:
      game.anims[0].append(AwakenAnim(
        duration=DungeonContext.AWAKEN_DURATION,
        target=target,
        on_end=awaken
      ))

  def use_skill(game, actor, skill):
    camera = game.camera
    if actor.faction == "player":
      if game.parent.sp >= skill.cost:
        game.parent.sp -= skill.cost
        if game.parent.sp < 1:
          game.parent.sp = 0
    game.log.print(actor.token(), " uses " + skill.name)
    target_cell = skill.effect(actor, game, on_end=lambda: (
      camera.blur(),
      actor is game.hero and game.step(),
      game.refresh_fov()
    ))
    if target_cell:
      camera.focus(target_cell)

  def use_item(game, item):
    success, message = item.effect(game)
    if success:
      game.log.print("Used " + item.name)
      game.log.print(message)
      game.parent.inventory.items.remove(item)
      game.anims.append([
        PauseAnim(
          duration=30,
          on_end=game.step
        )
      ])
      return (True, None)
    else:
      return (False, message)

  def update_skills(game, char=None):
    if char is None:
      game.update_skills(game.hero)
      game.update_skills(game.ally)
      return
    char.skills = [skill for skill, cell in game.skill_builds[char]]
    active_skills = [s for s in char.skills if s.kind != "passive"]
    skill = active_skills[0] if active_skills else None
    game.skill_selected[char] = skill

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
      if not game.ally.dead:
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

  def draw(game, surface):
    assets = load_assets()
    surface.fill(0x000000)
    window_width = surface.get_width()
    window_height = surface.get_height()

    game.camera.update(game)
    game.floor.draw(surface, game)

    for group in game.anims:
      for anim in group:
        if type(anim) is PauseAnim:
          anim.update()
          if anim.done:
            group.remove(anim)
      if len(group) == 0:
        game.anims.remove(group)

    # is_playing_enter_transit = len(game.parent.transits) and type(game.parent.transits[0]) is DissolveOut
    # if not is_playing_enter_transit:
    if not game.child or game.log.anim and not game.log.active:
      game.log.draw(surface)

    animating = (
      game.log.anim and not game.log.active
      or game.hud.anims
      or game.previews.anims
    )
    if game.child and not animating:
      game.child.draw(surface)

    game.hud.draw(surface, game)
    game.sp_meter.draw(surface, game.parent)
    game.previews.draw(surface, game)
    game.minimap.draw(surface)
