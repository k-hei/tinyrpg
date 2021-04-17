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
from cell import is_adjacent, manhattan

import gen
import fov
import config
import palette

from camera import Camera
from inventory import Inventory
from comps.statuspanel import StatusPanel
from comps.log import Log
from comps.minimap import Minimap
from comps.previews import Previews
from comps.damage import DamageValue

from transits.dissolve import DissolveOut

from contexts.inventory import InventoryContext
from contexts.skill import SkillContext
from contexts.examine import ExamineContext
from contexts.custom import CustomContext

from actors import Actor
from actors.knight import Knight
from actors.mage import Mage
from actors.eye import Eye
from actors.chest import Chest
from actors.mimic import Mimic
from actors.npc import NPC

from skills.blitzritter import Blitzritter
from skills.shieldbash import ShieldBash
from skills.counter import Counter
from skills.ignis import Ignis
from skills.glacio import Glacio
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

class DungeonContext(Context):
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
  TOP_FLOOR = 5

  def __init__(game, parent):
    super().__init__(parent)
    game.sp_max = 40
    game.sp = game.sp_max
    game.room = None
    game.floor = None
    game.floors = []
    game.memory = []
    game.anims = []
    game.vfx = []
    game.numbers = []
    game.log = Log()
    game.camera = Camera(config.window_size)
    game.hud = StatusPanel()
    game.minimap = Minimap((15, 15))
    game.inventory = Inventory((2, 2), [Potion()])
    game.previews = Previews()
    game.hero = Knight(skills=[])
    game.ally = Mage(skills=[])
    game.skill_pool = [Blitzritter, ShieldBash, Counter, Ignis, Glacio, Somnus, Obscura, DetectMana]
    game.skill_builds = { game.hero: [], game.ally: [] }
    game.skill_selected = { game.hero: None, game.ally: None }
    game.key_requires_reset = {}
    game.create_floor()

  def create_floor(game):
    floor_no = len(game.floors) + 1
    if floor_no == DungeonContext.TOP_FLOOR:
      floor = gen.top_floor()
    elif floor_no == 3:
      floor = gen.giant_room((19, 19))
    else:
      floor = gen.dungeon((19, 19), len(game.floors) + 1)

    if floor_no == DungeonContext.TOP_FLOOR:
      game.log.print("The air feels different up here.")
    elif floor.find_tile(Stage.DOOR_HIDDEN):
      game.log.print("This floor seems to hold many secrets.")

    floor.spawn_actor(game.hero, floor.entrance)
    if not game.ally.dead:
      x, y = floor.entrance
      floor.spawn_actor(game.ally, (x - 1, y))

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

    visited_cells = next((cells for floor, cells in game.memory if floor is game.floor), None)
    for cell in visible_cells:
      if cell not in visited_cells:
        visited_cells.append(cell)
    game.hero.visible_cells = visible_cells

    hero = game.hero
    camera = game.camera
    for actor in game.floor.actors:
      if actor.faction == "enemy" and is_adjacent(hero.cell, actor.cell) and not (type(actor) is Mimic and actor.idle):
        hero_x, hero_y = hero.cell
        actor_x, actor_y = actor.cell
        mid_x = (hero_x + actor_x) / 2
        mid_y = (hero_y + actor_y) / 2
        camera.focus((mid_x, mid_y))
        break
    else:
      camera.blur()

  def step(game, run=False):
    for actor in game.floor.actors:
      if actor.faction == "enemy":
        game.step_enemy(actor, run)
      elif actor.asleep:
        actor.hp += min(actor.hp_max, 1 / 25)
      if isinstance(actor, Actor) and actor.counter:
        actor.counter = max(0, actor.counter - 1)

  # TODO: move into enemy module
  def step_enemy(game, enemy, run=False):
    if enemy.stun:
      enemy.stun = False
      return False

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
      steps_to_hero = manhattan(enemy.cell, hero.cell)
      steps_to_ally = manhattan(enemy.cell, ally.cell)
      if steps_to_ally <= steps_to_hero and not ally.dead:
        game.move_to(enemy, ally.cell)
      else:
        game.move_to(enemy, hero.cell)

    return True

  def handle_keyup(game, key):
    game.key_requires_reset[key] = False

  def handle_keydown(game, key):
    if game.anims or game.log.anim or game.hud.anims:
      return False

    if game.child:
      return game.child.handle_keydown(key)

    key_deltas = {
      pygame.K_LEFT: (-1, 0),
      pygame.K_RIGHT: (1, 0),
      pygame.K_UP: (0, -1),
      pygame.K_DOWN: (0, 1),
      pygame.K_a: (-1, 0),
      pygame.K_d: (1, 0),
      pygame.K_w: (0, -1),
      pygame.K_s: (0, 1)
    }

    key_requires_reset = key in game.key_requires_reset and game.key_requires_reset[key]
    if key in key_deltas and not key_requires_reset:
      delta = key_deltas[key]
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

    if game.hero.dead or game.hero.asleep:
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
    if hero.dead or hero.asleep:
      return False
    old_cell = hero.cell
    hero_x, hero_y = old_cell
    delta_x, delta_y = delta
    acted = False
    moved = game.move(hero, delta, run)
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_tile = floor.get_tile_at(target_cell)
    target_actor = floor.get_actor_at(target_cell)
    if moved:
      if not ally.dead and not ally.asleep:
        last_group = game.anims[len(game.anims) - 1]
        if manhattan(ally.cell, old_cell) == 1:
          ally_x, ally_y = ally.cell
          old_x, old_y = old_cell
          game.move(ally, (old_x - ally_x, old_y - ally_y), run)
          last_group.append(game.anims.pop()[0])
        elif manhattan(ally.cell, hero.cell) > 1:
          game.move_to(ally, hero.cell, run)
          last_group.append(game.anims.pop()[0])

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
            not floor.get_actor_at(c)
            and floor.get_tile_at(c) is Stage.FLOOR
            and manhattan(c, hero.cell) > 2
          )]
          for i in range(monsters):
            cell = random.choice(cells)
            enemy = Eye()
            floor.spawn_actor(enemy, cell)
            cells.remove(cell)
            if random.randint(0, 9):
              enemy.asleep = True

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
        room_actors = [floor.get_actor_at(cell) for cell in room.get_cells() if floor.get_actor_at(cell)]
        enemies = [actor for actor in room_actors if actor.faction == "enemy"]
        enemy = next((e for e in enemies if e.asleep and random.randint(1, 10) == 1), None)
        if enemy:
          enemy.wake_up()
          is_waking_up = True
          if game.camera.is_cell_visible(enemy.cell):
            game.anims.append([
              AwakenAnim(
                duration=DungeonContext.AWAKEN_DURATION,
                target=enemy,
                on_end=lambda: (
                  game.log.print(enemy.name.upper() + " woke up!"),
                  game.anims[0].append(PauseAnim(
                    duration=DungeonContext.PAUSE_DURATION,
                    on_end=lambda: (
                      game.step(),
                      game.refresh_fov(moving=True)
                    )
                  ))
                )
              )
            ])

      if not is_waking_up:
        game.step()
        game.refresh_fov(moving=True)

      if game.sp:
        if not hero.dead and not hero.asleep:
          hero.regen()
        if not ally.dead and not ally.asleep:
          ally.regen()

      acted = True
      game.sp = max(0, game.sp - 1 / 100)
    elif target_actor and target_actor.faction == "enemy":
      if target_actor.idle:
        game.anims.append([
          AttackAnim(
            duration=DungeonContext.ATTACK_DURATION,
            target=hero,
            src_cell=hero.cell,
            dest_cell=target_cell
          ),
          PauseAnim(duration=15, on_end=lambda: (
            game.anims[0].append(FlickerAnim(
              duration=45,
              target=target_actor,
              on_end=lambda: (
                target_actor.activate(),
                game.log.print("The lamp was " + target_actor.name.upper() + "!"),
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
        game.log.print(hero.name.upper() + " attacks")
        game.attack(
          actor=hero,
          target=target_actor,
          on_end=lambda: (
            game.step(),
            game.refresh_fov()
          )
        )
        game.sp = max(0, game.sp - 1)
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
      if type(target_actor) is NPC:
        npc = target_actor
        game.log.clear()
        message = npc.message
        game.log.print(npc.name + ": " + message[0])
        for i in range(1, len(message)):
          game.log.print(message[i])
        if npc.message == npc.messages[0]:
          npc.message = npc.messages[1]
        else:
          npc.message = npc.messages[0]
      elif type(target_actor) is Chest:
        chest = target_actor
        item = chest.contents
        if item:
          if not game.inventory.is_full():
            game.anims.append([
              ChestAnim(
                duration=30,
                target=chest,
                item=type(item),
                on_end=chest.open
              )
            ])
            game.inventory.append(item)
            game.log.print("You open the lamp")
            game.log.print("Received " + item.name + ".")
            acted = True
          else:
            game.log.print("Your inventory is already full!")
        else:
          game.log.print("There's nothing left to take...")
        game.step(run)
        game.refresh_fov()
      elif target_actor and target_actor.faction == "player":
        game.log.exit()
        game.anims[0].append(PauseAnim(
          duration=60,
          on_end=lambda: (
            target_actor.wake_up(),
            game.log.print(target_actor.name.upper() + " woke up!"),
            game.anims[0].append(ShakeAnim(
              duration=DungeonContext.SHAKE_DURATION,
              target=target_actor,
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
    game.handle_floorchange(1)

  def handle_descend(game):
    if game.floor.get_tile_at(game.hero.cell) is not Stage.STAIRS_DOWN:
      return game.log.print("There's nowhere to go down here!")
    if game.floors.index(game.floor) == 0:
      return game.log.print("You aren't ready to go back yet.")
    game.handle_floorchange(-1)

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
          game.use_skill(skill) if skill else game.refresh_fov()
        )
      )

  def handle_inventory(game):
    if game.child is None:
      game.log.exit()
      game.child = InventoryContext(
        parent=game,
        inventory=game.inventory
      )

  def handle_custom(game):
    if game.child is None:
      game.log.exit()
      game.hud.exit()
      game.minimap.exit()
      game.child = CustomContext(
        parent=game,
        on_close=lambda _: (
          game.update_skills(),
          game.hud.enter(),
          game.minimap.enter()
        )
      )

  def handle_examine(game):
    if game.child is None:
      game.log.exit()
      game.hud.exit()
      game.child = ExamineContext(
        parent=game,
        on_close=lambda _: (
          game.hud.enter(),
          game.refresh_fov()
        )
      )

  def move(game, actor, delta, run=False):
    actor_x, actor_y = actor.cell
    delta_x, delta_y = delta
    target_cell = (actor_x + delta_x, actor_y + delta_y)
    target_tile = game.floor.get_tile_at(target_cell)
    target_actor = game.floor.get_actor_at(target_cell)
    actor.facing = delta
    if not target_tile.solid and (target_actor is None or actor is game.hero and target_actor is game.ally and not game.ally.asleep):
      duration = DungeonContext.RUN_DURATION if run else DungeonContext.MOVE_DURATION
      anim = MoveAnim(
        duration=duration,
        target=actor,
        src_cell=actor.cell,
        dest_cell=target_cell,
        on_end=game.refresh_fov
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
      target_actor = floor.get_actor_at(cell)
      return not target_tile.solid and not target_actor

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
      return game.move(actor, (delta_x, delta_y), run)
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
        game.log.print(target.name.upper() + " reflected the attack!")
        # target.counter = False
        real_target = actor
        real_damage = Actor.find_damage(actor, actor)
      game.flinch(
        target=real_target,
        damage=real_damage,
        on_end=on_end
      )
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
      game.floor.actors.remove(target)
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
        if trap and len([a for a in game.floor.actors if a.faction == "enemy"]) == 0:
          trap_x, trap_y = trap
          game.floor.set_tile_at((trap_x - 2, trap_y), Stage.DOOR_OPEN)
        if on_end:
          on_end()

    if target.faction == "enemy":
      game.log.print("Defeated " + target.name.upper() + ".")
    else:
      game.log.print(target.name.upper() + " is defeated.")
    game.anims[0].append(FlickerAnim(
      duration=DungeonContext.FLICKER_DURATION,
      target=target,
      on_end=remove
    ))

  def flinch(game, target, damage, on_end=None):
    was_asleep = target.asleep
    end = lambda: on_end and on_end()
    if target.dead: end()

    def awaken():
      game.log.print(target.name.upper() + " woke up!")
      game.anims[0].append(PauseAnim(duration=DungeonContext.PAUSE_DURATION))

    def respond():
      if target.dead:
        game.kill(target, on_end)
      elif is_adjacent(target.cell, target.cell):
        # pause before performing step
        return game.anims[0].append(PauseAnim(duration=DungeonContext.PAUSE_DURATION, on_end=end))
      else:
        end()

    target.damage(damage)
    game.numbers.append(DamageValue(str(damage), target.cell))
    verb = "receives" if target.faction == "enemy" else "suffers"
    game.log.print(target.name.upper() + " " + verb + " " + str(damage) + " damage.")
    game.anims[0].append(ShakeAnim(
      duration=DungeonContext.SHAKE_DURATION,
      target=target,
      on_end=respond
    ))
    if was_asleep and not target.asleep:
      game.anims[0].append(AwakenAnim(
        duration=DungeonContext.AWAKEN_DURATION,
        target=target,
        on_end=awaken
      ))

  def use_skill(game, skill):
    hero = game.hero
    camera = game.camera
    game.log.print(game.hero.name.upper() + " uses " + skill.name),
    target_cell = game.hero.use_skill(game, on_end=lambda: (
      camera.blur(),
      game.step(),
      game.refresh_fov()
    ))
    if target_cell:
      camera.focus(target_cell)

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

  def update_skills(game, char=None):
    if char is None:
      game.update_skills(game.hero)
      game.update_skills(game.ally)
      return
    char.skills = [skill for skill, cell in game.skill_builds[char]]
    game.skill_selected[char] = char.skills[0] if char.skills else None

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
    if not game.child or game.log.anim and game.log.exiting:
      log = game.log.render()
      surface.blit(log, (
        window_width / 2 - log.get_width() / 2,
        window_height + game.log.y
      ))

    animating = game.log.anim and game.log.exiting or game.hud.anims
    if game.child and not animating:
      game.child.draw(surface)

    game.hud.draw(surface, game)
    game.minimap.draw(surface, game)
    game.previews.draw(surface, game)
