from contexts import Context
from assets import load as load_assets
from text import render as render_text
from filters import recolor
from stage import Stage
from log import Log
from camera import Camera
from inventory import Inventory
from keyboard import key_times
import gen
import fov
import pygame
import config

from actors.knight import Knight
from actors.mage import Mage
from actors.eye import Eye
from actors.chest import Chest

from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.shake import ShakeAnim
from anims.flicker import FlickerAnim
from anims.pause import PauseAnim
from anims.awaken import AwakenAnim

MOVE_DURATION = 8
ATTACK_DURATION = 12
SHAKE_DURATION = 30
FLICKER_DURATION = 30
PAUSE_DURATION = 15
PAUSE_ITEM_DURATION = 30
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
    ctx.camera = Camera((config.window_width, config.window_height))
    ctx.inventory = Inventory(2, 2)
    ctx.create_floor()
    ctx.key_requires_reset = {}

  def create_floor(ctx):
    floor = gen.dungeon((19, 19))

    if floor.find_tile(Stage.DOOR_HIDDEN):
      ctx.log.print("This floor seems to hold many secrets.")

    stairs_x, stairs_y = floor.find_tile(Stage.STAIRS_DOWN)
    floor.spawn_actor(ctx.hero, (stairs_x, stairs_y))
    if not ctx.ally.dead:
      floor.spawn_actor(ctx.ally, (stairs_x - 1, stairs_y))

    ctx.floor = floor
    ctx.floors.append(ctx.floor)
    ctx.memory.append((ctx.floor, []))
    ctx.refresh_fov()

  def refresh_fov(ctx):
    visible_cells = fov.shadowcast(ctx.floor, ctx.hero.cell, VISION_RANGE)

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

  def handle_keyup(ctx, key):
    ctx.key_requires_reset[key] = False

  def handle_keydown(ctx, key):
    if len(ctx.anims):
      return False

    key_deltas = {
      pygame.K_LEFT: (-1, 0),
      pygame.K_RIGHT: (1, 0),
      pygame.K_UP: (0, -1),
      pygame.K_DOWN: (0, 1)
    }

    key_requires_reset = key in ctx.key_requires_reset and ctx.key_requires_reset[key]
    if key in key_deltas and not key_requires_reset:
      delta = key_deltas[key]
      moved = ctx.handle_move(delta)
      if not moved:
        ctx.key_requires_reset[key] = True

  def handle_move(ctx, delta):
    hero = ctx.hero
    ally = ctx.ally
    if hero.dead:
      return False
    hero_x, hero_y = hero.cell
    delta_x, delta_y = delta
    acted = False
    moved = ctx.move(hero, delta)
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_tile = ctx.floor.get_tile_at(target_cell)
    target_actor = ctx.floor.get_actor_at(target_cell)
    if moved:
      if not ally.dead:
        last_group = ctx.anims[len(ctx.anims) - 1]
        ally_x, ally_y = ally.cell
        ctx.move(ally, (hero_x - ally_x, hero_y - ally_y))
        last_group.append(ctx.anims.pop()[0])
      ctx.refresh_fov()

      if target_tile is Stage.STAIRS_UP:
        ctx.log.print("There's a staircase going up here.")
      elif target_tile is Stage.STAIRS_DOWN:
        if ctx.floors.index(ctx.floor):
          ctx.log.print("There's a staircase going down here.")
        else:
          ctx.log.print("You can return to the town from here.")

      if not hero.dead:
        hero.regen()
      if not ally.dead:
        ally.regen()

      acted = True
      ctx.sp = max(0, ctx.sp - 1 / 100)
    elif target_actor and type(target_actor) is Eye:
      # ctx.attack(hero, target_actor)
      ctx.sp = max(0, ctx.sp - 1)
      acted = True
    else:
      ctx.anims.append([
        AttackAnim(
          duration=ATTACK_DURATION,
          target=hero,
          src_cell=hero.cell,
          dest_cell=target_cell
        )
      ])
      if target_actor and type(target_actor) is Chest:
        if target_actor.contents:
          if not ctx.inventory.is_full():
            contents = target_actor.open()
            ctx.inventory.append(contents)
            ctx.log.print("You open the lamp")
            ctx.log.print("Received " + contents + ".")
            acted = True
          else:
            ctx.log.print("Your inventory is already full!")
        else:
          ctx.log.print("There's nothing left to take...")
      elif target_tile is Stage.DOOR:
        ctx.log.print("You open the door.")
        ctx.floor.set_tile_at(target_cell, Stage.DOOR_OPEN)
        acted = True
      elif target_tile is Stage.DOOR_HIDDEN:
        ctx.log.print("Discovered a hidden door!")
        ctx.floor.set_tile_at(target_cell, Stage.DOOR_OPEN)
        acted = True
    if acted:
      # ctx.step()
      ctx.refresh_fov()
    return moved

  def move(ctx, actor, delta, face=True):
    actor_x, actor_y = actor.cell
    delta_x, delta_y = delta
    target_cell = (actor_x + delta_x, actor_y + delta_y)
    target_tile = ctx.floor.get_tile_at(target_cell)
    target_actor = ctx.floor.get_actor_at(target_cell)
    if face and delta_x:
      actor.facing = (delta_x, 0)
    if not target_tile.solid and (target_actor is None or actor is ctx.hero and target_actor is ctx.ally):
      ctx.anims.append([
        MoveAnim(
          duration=MOVE_DURATION,
          target=actor,
          src_cell=actor.cell,
          dest_cell=target_cell
        )
      ])
      actor.cell = target_cell
      return True
    else:
      return False

  def render(ctx, surface):
    assets = load_assets()
    surface.fill(0x000000)
    window_width = surface.get_width()
    window_height = surface.get_height()

    ctx.camera.update(ctx)
    ctx.floor.render(surface, ctx)

    for group in ctx.anims:
      for anim in group:
        if type(anim) is PauseAnim:
          anim.update()
          if anim.done:
            anim_group.remove(anim)
      if len(group) == 0:
        ctx.anims.remove(group)



#   def render(ctx, surface):

#     portrait_knight = sprites["portrait_knight"].copy()
#     portrait_mage = sprites["portrait_mage"].copy()
#     pixels_knight = PixelArray(portrait_knight)
#     pixels_mage = PixelArray(portrait_mage)

#     hero_anim = None
#     for group in game.anims:
#       for anim in group:
#         if anim.target is hero:
#           hero_anim = anim
#           break

#     knight = game.p1 if type(hero) is Knight else game.p2
#     mage = game.p1 if type(hero) is Mage else game.p2

#     if knight.dead and not is_drawing_knight:
#       pixels_knight.replace(WHITE, RED)
#     elif type(hero) is not Knight:
#       pixels_knight.replace(WHITE, GRAY)
#     pixels_knight.close()

#     if mage.dead and not is_drawing_mage:
#       pixels_mage.replace(WHITE, RED)
#     elif type(hero) is not Mage:
#       pixels_mage.replace(WHITE, GRAY)
#     pixels_mage.close()

#     surface.blit(portrait_knight, (8, 6))
#     surface.blit(portrait_mage, (36, 6))
#     surface.blit(sprites["hud"], (64, 6))

#     x = 74

#     hp_y = 11
#     surface.blit(sprites["tag_hp"], (x, hp_y))
#     surface.blit(sprites["bar"], (x + 19, hp_y + 7))
#     pygame.draw.rect(surface, 0xFFFFFF, Rect(x + 22, hp_y + 8, math.ceil(50 * game.p1.hp / game.p1.hp_max), 2))
#     hp_text = str(math.ceil(game.p1.hp)) + "/" + str(game.p1.hp_max)
#     surface.blit(recolor(render_text("0" + str(math.ceil(game.p1.hp)) + "/" + "0" + str(game.p1.hp_max), font_smallcaps), (0x7F, 0x7F, 0x7F)), (x + 19, hp_y + 1))
#     surface.blit(render_text("  " + str(math.ceil(game.p1.hp)) + "/  " + str(game.p1.hp_max), font_smallcaps), (x + 19, hp_y + 1))

#     sp_y = 24
#     surface.blit(sprites["tag_sp"], (x, sp_y))
#     surface.blit(sprites["bar"], (x + 19, sp_y + 7))
#     pygame.draw.rect(surface, 0xFFFFFF, Rect(x + 22, sp_y + 8, math.ceil(50 * game.sp / game.sp_max), 2))
#     hp_text = str(math.ceil(game.sp)) + "/" + str(game.sp_max)
#     surface.blit(recolor(render_text(str(math.ceil(game.sp)) + "/" + str(game.sp_max), font_smallcaps), (0x7F, 0x7F, 0x7F)), (x + 19, sp_y + 1))
#     surface.blit(render_text(str(math.ceil(game.sp)) + "/" + str(game.sp_max), font_smallcaps), (x + 19, sp_y + 1))

#     floor_y = 38
#     floor = game.floors.index(game.floor) + 1
#     surface.blit(sprites["tag_floor"], (x, floor_y))
#     surface.blit(render_text(str(floor) + "F", font_smallcaps), (x + 13, floor_y + 3))

#     box = sprites["box"]
#     cols = game.inventory.cols
#     rows = game.inventory.rows
#     margin_x = 8
#     margin_y = 6
#     spacing = 2
#     start_x = window_width - (box.get_width() + spacing) * cols - margin_x
#     for row in range(rows):
#       for col in range(cols):
#         index = row * cols + col
#         x = start_x + (box.get_width() + spacing) * col
#         y = margin_y + (box.get_height() + spacing) * row
#         surface.blit(box, (x, y))
#         if index < len(game.inventory.items):
#           item = game.inventory.items[index]
#           if item == "Potion":
#             sprite = sprites["icon_potion"]
#           elif item == "Bread":
#             sprite = sprites["icon_bread"]
#           elif item == "Warp Crystal":
#             sprite = sprites["icon_crystal"]
#           elif item == "Ankh":
#             sprite = sprites["icon_ankh"]
#           if sprite:
#             surface.blit(sprite, (x + 8, y + 8))

#     is_playing_enter_transition = len(transits) and type(transits[0]) is DissolveOut
#     if not is_playing_enter_transition:
#       log = game.log.render(sprites["log"], font_standard)
#       surface.blit(log, (
#         window_width / 2 - log.get_width() / 2,
#         window_height + game.log.y
#       ))







#   def step(game):
#     enemies = [actor for actor in game.floor.actors if type(actor) is Eye]
#     for enemy in enemies:
#       game.step_enemy(enemy)

#   def step_enemy(game, enemy):
#     if enemy.dead or enemy.asleep:
#       return False

#     hero = game.p1
#     room = next((room for room in game.floor.rooms if enemy.cell in room.get_cells()), None)
#     if not room or hero.cell not in room.get_cells():
#       return False

#     if is_adjacent(enemy.cell, hero.cell):
#       if not hero.dead:
#         game.attack(enemy, hero)
#     else:
#       delta_x, delta_y = (0, 0)
#       enemy_x, enemy_y = enemy.cell
#       hero_x, hero_y = hero.cell

#       if random.randint(1, 2) == 1:
#         if hero_x < enemy_x:
#           delta_x = -1
#         elif hero_x > enemy_x:
#           delta_x = 1
#         elif hero_y < enemy_y:
#           delta_y = -1
#         elif hero_y > enemy_y:
#           delta_y = 1
#       else:
#         if hero_y < enemy_y:
#           delta_y = -1
#         elif hero_y > enemy_y:
#           delta_y = 1
#         elif hero_x < enemy_x:
#           delta_x = -1
#         elif hero_x > enemy_x:
#           delta_x = 1

#       if delta_x == 0 and delta_y == 0:
#         return True
#       game.move(enemy, (delta_x, delta_y))

#     return True

#   def attack(game, actor, target):
#     was_asleep = target.asleep
#     game.log.print(actor.name.upper() + " attacks")

#     def on_flicker_end():
#       game.floor.actors.remove(target)
#       if target.faction == "player":
#         game.swap()

#     def on_awaken_end():
#       game.log.print(target.name.upper() + " woke up!")
#       game.anims[0].append(PauseAnim(duration=Game.PAUSE_DURATION))

#     def on_shake_end():
#       if target.dead:
#         if target.faction == "enemy":
#           game.log.print("Defeated " + target.name.upper() + ".")
#         else:
#           game.log.print(target.name.upper() + " is defeated.")
#         game.anims[0].append(FlickerAnim(
#           duration=Game.FLICKER_DURATION,
#           target=target,
#           on_end=on_flicker_end
#         ))
#       elif is_adjacent(actor.cell, target.cell):
#         game.anims[0].append(PauseAnim(duration=Game.PAUSE_DURATION))

#     def on_connect():
#       damage = actor.attack(target)
#       verb = "suffers" if actor.faction == "enemy" else "receives"
#       game.log.print(target.name.upper() + " " + verb + " " + str(damage) + " damage.")
#       game.anims[0].append(ShakeAnim(
#         duration=Game.SHAKE_DURATION,
#         target=target,
#         on_end=on_shake_end
#       ))
#       if was_asleep and not target.asleep:
#         game.anims[0].append(AwakenAnim(
#           duration=Game.AWAKEN_DURATION,
#           target=target,
#           on_end=on_awaken_end)
#         )

#     damage = actor.find_damage(target)
#     if damage >= target.hp:
#       target.dead = True

#     game.anims.append([
#       AttackAnim(
#         duration=Game.ATTACK_DURATION,
#         target=actor,
#         src_cell=actor.cell,
#         dest_cell=target.cell,
#         on_connect=on_connect
#       )
#     ])

#   def use_item(game):
#     hero = game.p1
#     if len(game.inventory.items) == 0:
#       game.log.print("No items to use!")
#       return
#     item = game.inventory.items[0]
#     game.inventory.items.remove(item)
#     game.log.print("Used " + item)
#     if item == "Potion":
#       game.log.print(hero.name.upper() + " restored 10 HP.")
#       hero.regen(10)
#     elif item == "Bread":
#       game.log.print("The party restored 5 SP.")
#       if game.sp + 5 < game.sp_max:
#         game.sp += 5
#       else:
#         game.sp = game.sp_max
#     else:
#       game.log.print("But nothing happened...")
#     game.anims.append([ PauseAnim(duration=Game.PAUSE_ITEM_DURATION) ])
#     game.step()

#   def swap(game):
#     if game.p2.dead:
#       return False
#     game.p1, game.p2 = (game.p2, game.p1)
#     game.refresh_fov()
#     return True

#   def special(game):
#     if type(game.p1) is Knight:
#       game.shield_bash()
#     elif type(game.p1) is Mage:
#       game.detect_mana()

#   def detect_mana(game):
#     if game.sp >= 1:
#       game.sp = max(0, game.sp - 1)
#     def search():
#       cells = game.p1.visible_cells
#       for cell in cells:
#         tile = game.floor.get_tile_at(cell)
#         if tile is Stage.DOOR_HIDDEN:
#           game.log.print("There's a hidden passage somewhere here.")
#           break
#       else:
#         game.log.print("You don't sense anything magical nearby.")
#     game.log.print("MAGE uses Detect Mana")
#     game.anims.append([ PauseAnim(duration=30, on_end=search) ])

#   def shield_bash(game):
#     if game.sp >= 2:
#       game.sp = max(0, game.sp - 2)
#     source_cell = game.p1.cell
#     hero_x, hero_y = source_cell
#     delta_x, delta_y = game.p1.facing
#     target_cell = (hero_x + delta_x, hero_y + delta_y)
#     target_actor = game.floor.get_actor_at(target_cell)
#     game.log.print("HERO uses Shield Bash")

#     if target_actor and target_actor is not game.p2:
#       # nudge target actor 1 square in the given direction
#       target_x, target_y = target_cell
#       nudge_cell = (target_x + delta_x, target_y + delta_y)
#       nudge_tile = game.floor.get_tile_at(nudge_cell)
#       nudge_actor = game.floor.get_actor_at(nudge_cell)
#       game.anims.append([
#         ShakeAnim(duration=Game.SHAKE_DURATION, target=target_actor)
#       ])
#       if not nudge_tile.solid and nudge_actor is None:
#         target_actor.cell = nudge_cell
#         game.anims.append([
#           MoveAnim(
#             duration=Game.MOVE_DURATION,
#             target=target_actor,
#             src_cell=target_cell,
#             dest_cell=nudge_cell
#           )
#         ])
#       if type(target_actor) is Eye:
#         game.attack(target_actor)
#         game.log.print("EYEBALL is reeling.")
#     else:
#       game.log.print("But nothing happened...")
#       game.anims.append([
#         AttackAnim(
#           duration=Game.ATTACK_DURATION,
#           target=game.p1,
#           src_cell=game.p1.cell,
#           dest_cell=target_cell
#         )
#       ])

#   def change_floors(game, direction):
#     exit_tile = Stage.STAIRS_UP if direction == 1 else Stage.STAIRS_DOWN
#     entry_tile = Stage.STAIRS_DOWN if direction == 1 else Stage.STAIRS_UP
#     text = "You go upstairs." if direction == 1 else "You go downstairs."

#     if direction not in (1, -1):
#       return False

#     target_tile = game.floor.get_tile_at(game.p1.cell)
#     if target_tile is not exit_tile:
#       return False

#     game.log.print(text)
#     old_floor = game.floor
#     old_floor.remove_actor(game.p1)
#     old_floor.remove_actor(game.p2)

#     index = game.floors.index(game.floor) + direction
#     if index >= len(game.floors):
#       # create a new floor if out of bounds
#       game.load_floor()
#     elif index >= 0:
#       # go back to old floor if within bounds
#       new_floor = game.floors[index]
#       stairs_x, stairs_y = new_floor.find_tile(entry_tile)
#       new_floor.spawn_actor(game.p1, (stairs_x, stairs_y))
#       if not game.p2.dead:
#         new_floor.spawn_actor(game.p2, (stairs_x - 1, stairs_y))
#       game.floor = new_floor
#       game.refresh_fov()

#     return True

# key_requires_reset = {}
# for key in key_times:
#   key_requires_reset[key] = False

# def handle_keyup(ctx, key):
#   key_requires_reset[key] = False

# def handle_keydown(ctx, key):
#   key_deltas = {
#     pygame.K_LEFT: (-1, 0),
#     pygame.K_RIGHT: (1, 0),
#     pygame.K_UP: (0, -1),
#     pygame.K_DOWN: (0, 1)
#   }

#   if key in key_deltas and not key_requires_reset[key]:
#     moved = game.handle_move((delta_x, delta_y))
#     if not moved:
#       key_requires_reset[key] = True

#   if not key_times[key] == 1:
#     return False

#   if key == pygame.K_TAB:
#     return ctx.handle_swap()

#   if key == pygame.K_:
#     return ctx.handle_inventory()

#   if key == pygame.K_q:
#     return ctx.handle_item()

#   if key == pygame.K_SPACE:
#     return ctx.handle_special()

#   if key == pygame.K_COMMA and key_times[pygame.KMOD_SHIFT]:
#     return ctx.handle_ascend()

#   if key == pygame.K_PERIOD and key_times[pygame.KMOD_SHIFT]:
#     return ctx.handle_descend()

#   return False

# def change_floors(ctx, direction):
#   ctx.log.exit()
#   on_end =
#   ctx.parent.dissolve(lambda: ctx.change_floors(1))
#   ctx.parent.transits.append(DissolveIn(surface, on_end))
#   ctx.parent.transits.append(DissolveOut(surface))

# def handle_ascend(ctx):
#   if ctx.floor.get_tile_at(ctx.hero.cell) is not Stage.STAIRS_UP:
#     return ctx.log.print("There's nowhere to go up here!")
#   ctx.change_floors(1)

# def handle_descend(ctx):
#   if ctx.floor.get_tile_at(ctx.hero.cell) is not Stage.STAIRS_DOWN:
#     return ctx.log.print("There's nowhere to go down here!")
#   ctx.change_floors(1)

# def handle_keydown(ctx, key):
#   if len(ctx.transits):
#     return

#   if ctx.child:
#     ctx.child.handle_keydown(key)
#     return

# def reset_camera():
#   global camera
#   camera = None
