import math
import random
import pygame
from pygame import Rect

from contexts import Context
from assets import load as load_assets
from text import render as render_text
from filters import recolor, replace_color
from stage import Stage
from actors import Actor
from keyboard import key_times
from cell import is_adjacent

import gen
import fov
import config
import palette

from log import Log
from camera import Camera
from inventory import Inventory
from statuspanel import StatusPanel
from minimap import Minimap

from transits.dissolve import DissolveOut

from contexts.inventory import InventoryContext
from contexts.skill import SkillContext

from actors.knight import Knight
from actors.mage import Mage
from actors.eye import Eye
from actors.chest import Chest

from skills.shieldbash import ShieldBash
from skills.phalanx import Phalanx
from skills.blitzritter import Blitzritter
from skills.helmsplitter import HelmSplitter
from skills.ignis import Ignis
from skills.somnus import Somnus
from skills.obscura import Obscura
from skills.detectmana import DetectMana

from items.potion import Potion
from items.ankh import Ankh

from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.shake import ShakeAnim
from anims.flicker import FlickerAnim
from anims.pause import PauseAnim
from anims.awaken import AwakenAnim
from anims.chest import ChestAnim

MOVE_DURATION = 16
RUN_DURATION = 12
ATTACK_DURATION = 12
SHAKE_DURATION = 30
FLICKER_DURATION = 30
PAUSE_DURATION = 15
PAUSE_ITEM_DURATION = 30
PAUSE_DEATH_DURATION = 45
AWAKEN_DURATION = 45
VISION_RANGE = 3.5

class DungeonContext(Context):
  def __init__(ctx, parent):
    super().__init__(parent)
    ctx.sp_max = 40
    ctx.sp = ctx.sp_max
    ctx.room = None
    ctx.floor = None
    ctx.floors = []
    ctx.memory = []
    ctx.anims = []
    ctx.hero = Knight()
    ctx.ally = Mage()
    ctx.log = Log()
    ctx.camera = Camera(config.window_size)
    ctx.hud = StatusPanel()
    ctx.minimap = Minimap((15, 15))
    ctx.inventory = Inventory((2, 2), [Potion()])
    ctx.create_floor()
    ctx.key_requires_reset = {}
    ctx.skills = {
      ctx.hero: [ShieldBash(), Phalanx(), Blitzritter(), HelmSplitter()],
      ctx.ally: [Ignis(), Somnus(), DetectMana()]
    }

  def create_floor(ctx):
    floor = gen.dungeon((19, 19), len(ctx.floors) + 1)

    if floor.find_tile(Stage.DOOR_HIDDEN):
      ctx.log.print("This floor seems to hold many secrets.")

    entrance = floor.find_tile(Stage.STAIRS_DOWN)
    if entrance is None:
      x, y = floor.rooms[0].get_center()
      entrance = (x, y + 2)

    floor.spawn_actor(ctx.hero, entrance)
    if not ctx.ally.dead:
      x, y = entrance
      floor.spawn_actor(ctx.ally, (x - 1, y))

    ctx.floor = floor
    ctx.floors.append(ctx.floor)
    ctx.memory.append((ctx.floor, []))
    ctx.refresh_fov(moving=True)

  def refresh_fov(ctx, moving=False):
    visible_cells = fov.shadowcast(ctx.floor, ctx.hero.cell, VISION_RANGE)

    if moving:
      rooms = [room for room in ctx.floor.rooms if ctx.hero.cell in room.get_cells() + room.get_border()]
      old_room = ctx.room
      if len(rooms) == 1:
        new_room = rooms[0]
      else:
        new_room = next((room for room in rooms if room is not ctx.room), None)
      if new_room is not old_room:
        ctx.room = new_room

    if ctx.room:
      visible_cells += ctx.room.get_cells() + ctx.room.get_border()

    visited_cells = next((cells for floor, cells in ctx.memory if floor is ctx.floor), None)
    for cell in visible_cells:
      if cell not in visited_cells:
        visited_cells.append(cell)
    ctx.hero.visible_cells = visible_cells

  def step(game, run=False):
    for actor in game.floor.actors:
      if actor.faction == "enemy":
        game.step_enemy(actor, run)
      elif actor.asleep:
        actor.hp += 1 / 25

  # TODO: move into enemy module (requires some kind of event/cache system)
  def step_enemy(game, enemy, run=False):
    if enemy.dead or enemy.asleep or enemy.idle:
      return False

    hero = game.hero
    ally = game.ally
    room = next((room for room in game.floor.rooms if enemy.cell in room.get_cells()), None)
    if not room:
      return False

    room_cells = room.get_cells() + room.get_border()
    if hero.cell not in room_cells:
      return False

    if is_adjacent(enemy.cell, hero.cell) and not hero.dead:
      game.log.print(enemy.name.upper() + " attacks")
      game.attack(enemy, hero, run)
    elif is_adjacent(enemy.cell, ally.cell) and not ally.dead:
      game.log.print(enemy.name.upper() + " attacks")
      game.attack(enemy, ally, run)
    else:
      delta_x, delta_y = (0, 0)
      enemy_x, enemy_y = enemy.cell
      hero_x, hero_y = hero.cell

      if random.randint(1, 2) == 1:
        if hero_x < enemy_x:
          delta_x = -1
        elif hero_x > enemy_x:
          delta_x = 1
        elif hero_y < enemy_y:
          delta_y = -1
        elif hero_y > enemy_y:
          delta_y = 1
      else:
        if hero_y < enemy_y:
          delta_y = -1
        elif hero_y > enemy_y:
          delta_y = 1
        elif hero_x < enemy_x:
          delta_x = -1
        elif hero_x > enemy_x:
          delta_x = 1

      if delta_x == 0 and delta_y == 0:
        return True
      game.move(enemy, (delta_x, delta_y), run)

    return True

  def handle_keyup(ctx, key):
    ctx.key_requires_reset[key] = False

  def handle_keydown(ctx, key):
    if len(ctx.anims) or ctx.log.anim or ctx.hud.anims:
      return False

    if ctx.child:
      return ctx.child.handle_keydown(key)

    key_deltas = {
      pygame.K_LEFT: (-1, 0),
      pygame.K_RIGHT: (1, 0),
      pygame.K_UP: (0, -1),
      pygame.K_DOWN: (0, 1)
    }

    key_requires_reset = key in ctx.key_requires_reset and ctx.key_requires_reset[key]
    if key in key_deltas and not key_requires_reset:
      delta = key_deltas[key]
      run = pygame.K_RSHIFT in key_times and key_times[pygame.K_RSHIFT] > 0
      moved = ctx.handle_move(delta, run)
      if not moved:
        ctx.key_requires_reset[key] = True
      return moved

    if key not in key_times or key_times[key] != 1:
      return False

    if key == pygame.K_TAB:
      return ctx.handle_swap()

    if ctx.hero.dead or ctx.hero.asleep:
      return False

    if key == pygame.K_BACKSPACE:
      return ctx.handle_inventory()

    if key == pygame.K_SPACE:
      return ctx.handle_wait()

    if key == pygame.K_RETURN:
      if ctx.floor.get_tile_at(ctx.hero.cell) is Stage.STAIRS_UP:
        return ctx.handle_ascend()
      elif ctx.floor.get_tile_at(ctx.hero.cell) is Stage.STAIRS_DOWN:
        return ctx.handle_descend()
      else:
        return ctx.handle_skill()

    return False

  def handle_move(ctx, delta, run=False):
    hero = ctx.hero
    ally = ctx.ally
    if hero.dead or hero.asleep:
      return False
    hero_x, hero_y = hero.cell
    delta_x, delta_y = delta
    acted = False
    moved = ctx.move(hero, delta, run)
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_tile = ctx.floor.get_tile_at(target_cell)
    target_actor = ctx.floor.get_actor_at(target_cell)
    if moved:
      if not ally.dead and not ally.asleep:
        last_group = ctx.anims[len(ctx.anims) - 1]
        ally_x, ally_y = ally.cell
        ctx.move(ally, (hero_x - ally_x, hero_y - ally_y), run)
        last_group.append(ctx.anims.pop()[0])

      if target_tile is Stage.STAIRS_UP:
        ctx.log.print("There's a staircase going up here.")
      elif target_tile is Stage.STAIRS_DOWN:
        if ctx.floors.index(ctx.floor):
          ctx.log.print("There's a staircase going down here.")
        else:
          ctx.log.print("You can return to the town from here.")

      is_waking_up = False
      if ctx.room:
        room = ctx.room
        floor = ctx.floor
        room_actors = [floor.get_actor_at(cell) for cell in room.get_cells() if floor.get_actor_at(cell)]
        enemies = [actor for actor in room_actors if actor.faction == "enemy"]
        for enemy in enemies:
          if enemy.asleep and random.randint(1, 10) == 1:
            enemy.asleep = False
            is_waking_up = True
            ctx.anims.append([
              AwakenAnim(
                duration=AWAKEN_DURATION,
                target=enemy,
                on_end=lambda: (
                  ctx.log.print(enemy.name.upper() + " woke up!"),
                  ctx.anims[0].append(PauseAnim(duration=PAUSE_DURATION)),
                )
              )
            ])
            break

      if not is_waking_up:
        ctx.step()
        ctx.refresh_fov(moving=True)

      if not hero.dead and not hero.asleep:
        hero.regen()
      if not ally.dead and not ally.asleep:
        ally.regen()

      acted = True
      ctx.sp = max(0, ctx.sp - 1 / 100)
    elif target_actor and target_actor.faction == "enemy":
      if target_actor.idle:
        ctx.anims.append([
          AttackAnim(
            duration=ATTACK_DURATION,
            target=hero,
            src_cell=hero.cell,
            dest_cell=target_cell
          ),
          PauseAnim(duration=15, on_end=lambda: (
            target_actor.activate(),
            ctx.log.print("The lamp was " + target_actor.name.upper() + "!"),
            ctx.step(),
            ctx.anims[0].append(PauseAnim(
              duration=15,
              on_end=lambda: ctx.refresh_fov
            ))
          ))
        ])
        ctx.log.print("You open the lamp")
      else:
        ctx.log.print(hero.name.upper() + " attacks")
        ctx.attack(hero, target_actor, run)
        ctx.sp = max(0, ctx.sp - 1)
        acted = True
        ctx.step(run)
        ctx.refresh_fov()
    else:
      ctx.anims.append([
        AttackAnim(
          duration=ATTACK_DURATION,
          target=hero,
          src_cell=hero.cell,
          dest_cell=target_cell
        )
      ])
      if type(target_actor) is Chest:
        chest = target_actor
        item = chest.contents
        if item:
          if not ctx.inventory.is_full():
            ctx.anims.append([
              ChestAnim(
                duration=30,
                target=chest,
                item=type(item),
                on_end=chest.open
              )
            ])
            ctx.inventory.append(item)
            ctx.log.print("You open the lamp")
            ctx.log.print("Received " + item.name + ".")
            acted = True
          else:
            ctx.log.print("Your inventory is already full!")
        else:
          ctx.log.print("There's nothing left to take...")
        ctx.step(run)
        ctx.refresh_fov()
      elif target_actor and target_actor.faction == "player":
        ctx.log.exit()
        ctx.anims[0].append(PauseAnim(
          duration=60,
          on_end=lambda: (
            target_actor.wake_up(),
            ctx.log.print(target_actor.name.upper() + " woke up!"),
            ctx.anims[0].append(ShakeAnim(
              duration=SHAKE_DURATION,
              target=target_actor,
            ))
          )
        ))
      elif target_tile is Stage.DOOR:
        ctx.log.print("You open the door.")
        ctx.floor.set_tile_at(target_cell, Stage.DOOR_OPEN)
        ctx.step(run)
        ctx.refresh_fov()
      elif target_tile is Stage.DOOR_HIDDEN:
        ctx.log.print("Discovered a hidden door!")
        ctx.floor.set_tile_at(target_cell, Stage.DOOR_OPEN)
        ctx.step(run)
        ctx.refresh_fov()
      elif target_tile is Stage.DOOR_LOCKED:
        ctx.log.print("The door is locked...")
    return moved

  def handle_wait(ctx):
    ctx.step()

  def handle_swap(game):
    if game.ally.dead:
      return False
    game.hero, game.ally = (game.ally, game.hero)
    game.refresh_fov(moving=True)
    return True

  def handle_ascend(ctx):
    if ctx.floor.get_tile_at(ctx.hero.cell) is not Stage.STAIRS_UP:
      return ctx.log.print("There's nowhere to go up here!")
    ctx.handle_floorchange(1)

  def handle_descend(ctx):
    if ctx.floor.get_tile_at(ctx.hero.cell) is not Stage.STAIRS_DOWN:
      return ctx.log.print("There's nowhere to go down here!")
    if ctx.floors.index(ctx.floor) == 0:
      return ctx.log.print("You aren't ready to go back yet.")
    ctx.handle_floorchange(-1)

  def handle_floorchange(ctx, direction):
    ctx.log.exit()
    ctx.hud.exit()
    ctx.parent.dissolve(
      on_clear=lambda: (
        ctx.camera.reset(),
        ctx.change_floors(direction)
      ),
      on_end=ctx.hud.enter
    )

  def handle_skill(ctx):
    if ctx.child is None:
      ctx.log.exit()
      ctx.child = SkillContext(
        parent=ctx,
        on_close=lambda skill: (
          skill and ctx.hero.use_skill(ctx)
        )
      )

  def handle_inventory(ctx):
    if ctx.child is None:
      ctx.log.exit()
      ctx.child = InventoryContext(
        parent=ctx,
        inventory=ctx.inventory
      )

  def move(ctx, actor, delta, run=False):
    actor_x, actor_y = actor.cell
    delta_x, delta_y = delta
    target_cell = (actor_x + delta_x, actor_y + delta_y)
    target_tile = ctx.floor.get_tile_at(target_cell)
    target_actor = ctx.floor.get_actor_at(target_cell)
    actor.facing = delta
    if not target_tile.solid and (target_actor is None or actor is ctx.hero and target_actor is ctx.ally and not ctx.ally.asleep):
      duration = RUN_DURATION if run else MOVE_DURATION
      ctx.anims.append([
        MoveAnim(
          duration=duration,
          target=actor,
          src_cell=actor.cell,
          dest_cell=target_cell
        )
      ])
      actor.cell = target_cell
      return True
    else:
      return False

  def attack(game, actor, target, damage=None, run=False, on_connect=None, on_end=None):
    def remove():
      game.floor.actors.remove(target)
      if target.faction == "player":
        game.anims[0].append(PauseAnim(
          duration=PAUSE_DEATH_DURATION,
          on_end=lambda: (
            game.handle_swap(),
            on_end and on_end()
          )
        ))
      else:
        if on_end: on_end()

    def awaken():
      game.log.print(target.name.upper() + " woke up!")
      game.anims[0].append(PauseAnim(duration=PAUSE_DURATION, on_end=on_end))

    def respond():
      if target.dead:
        if target.faction == "enemy":
          game.log.print("Defeated " + target.name.upper() + ".")
        else:
          game.log.print(target.name.upper() + " is defeated.")
        game.anims[0].append(FlickerAnim(
          duration=FLICKER_DURATION,
          target=target,
          on_end=remove
        ))
      elif is_adjacent(actor.cell, target.cell):
        game.anims[0].append(PauseAnim(duration=PAUSE_DURATION, on_end=on_end))

    def shake():
      actor.attack(target)
      verb = "suffers" if actor.faction == "enemy" else "receives"
      game.log.print(target.name.upper() + " " + verb + " " + str(damage) + " damage.")
      if on_connect: on_connect()
      game.anims[0].append(ShakeAnim(
        duration=SHAKE_DURATION,
        target=target,
        on_end=respond
      ))
      if was_asleep and not target.asleep:
        game.anims[0].append(AwakenAnim(
          duration=AWAKEN_DURATION,
          target=target,
          on_end=awaken
        ))

    was_asleep = target.asleep
    if not damage:
      damage = Actor.find_damage(actor, target)
    if damage >= target.hp:
      target.dead = True

    game.anims.append([
      AttackAnim(
        duration=ATTACK_DURATION,
        target=actor,
        src_cell=actor.cell,
        dest_cell=target.cell,
        on_connect=shake
      )
    ])

  def use_item(game, item):
    success, message = item.effect(game)
    if success:
      game.log.print("Used " + item.name)
      game.log.print(message)
      game.inventory.items.remove(item)
      game.anims.append([
        PauseAnim(
          duration=30,
          on_end=game.step
        )
      ])
      return (True, None)
    else:
      return (False, message)

  def change_floors(game, direction):
    exit_tile = Stage.STAIRS_UP if direction == 1 else Stage.STAIRS_DOWN
    entry_tile = Stage.STAIRS_DOWN if direction == 1 else Stage.STAIRS_UP

    if direction not in (1, -1):
      return False

    target_tile = game.floor.get_tile_at(game.hero.cell)
    if target_tile is not exit_tile:
      return False

    old_floor = game.floor
    old_floor.remove_actor(game.hero)
    old_floor.remove_actor(game.ally)

    index = game.floors.index(game.floor) + direction
    if index >= len(game.floors):
      # create a new floor if out of bounds
      game.log.print("You go upstairs.")
      game.create_floor()
    elif index >= 0:
      # go back to old floor if within bounds
      new_floor = game.floors[index]
      stairs_x, stairs_y = new_floor.find_tile(entry_tile)
      new_floor.spawn_actor(game.hero, (stairs_x, stairs_y))
      if not game.ally.dead:
        new_floor.spawn_actor(game.ally, (stairs_x - 1, stairs_y))
      game.floor = new_floor
      game.refresh_fov(moving=True)
      game.log.print("You go upstairs." if direction == 1 else "You go back downstairs.")

    return True

  def draw(ctx, surface):
    assets = load_assets()
    surface.fill(0x000000)
    window_width = surface.get_width()
    window_height = surface.get_height()

    ctx.camera.update(ctx)
    ctx.floor.draw(surface, ctx)

    for group in ctx.anims:
      for anim in group:
        if type(anim) is PauseAnim:
          anim.update()
          if anim.done:
            group.remove(anim)
      if len(group) == 0:
        ctx.anims.remove(group)

    # is_playing_enter_transit = len(ctx.parent.transits) and type(ctx.parent.transits[0]) is DissolveOut
    # if not is_playing_enter_transit:
    if not ctx.child or ctx.log.anim and ctx.log.exiting:
      log = ctx.log.render(assets.sprites["log"], assets.fonts["standard"])
      surface.blit(log, (
        window_width / 2 - log.get_width() / 2,
        window_height + ctx.log.y
      ))

    animating = ctx.log.anim and ctx.log.exiting or ctx.hud.anims
    if ctx.child and not animating:
      ctx.child.draw(surface)

    ctx.hud.draw(surface, ctx)
    ctx.minimap.draw(surface, ctx)
