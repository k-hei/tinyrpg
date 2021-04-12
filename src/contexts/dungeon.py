from contexts import Context
from assets import load as load_assets
from text import render as render_text
from filters import recolor
from stage import Stage
from actors.knight import Knight
from actors.mage import Mage
from log import Log
from camera import Camera
from inventory import Inventory
import gen
import fov
import pygame
import config

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

  def handle_keydown(ctx, key):
    key_deltas = {
      pygame.K_LEFT: (-1, 0),
      pygame.K_RIGHT: (1, 0),
      pygame.K_UP: (0, -1),
      pygame.K_DOWN: (0, 1)
    }
    if key in key_deltas:
      delta = key_deltas[key]
      return ctx.handle_move(delta)
    return False

  def handle_move(ctx, delta):
    pass

  def render(ctx, surface):
    assets = load_assets()
    surface.fill(0x000000)
    window_width = surface.get_width()
    window_height = surface.get_height()

    hero = ctx.hero
    visible_cells = hero.visible_cells
    visited_cells = next((cells for floor, cells in ctx.memory if floor is ctx.floor), None)

    ctx.camera.update(ctx)
    ctx.floor.render_tiles(
      surface=surface,
      visible_cells=ctx.hero.visible_cells,
      visited_cells=visited_cells,
      camera_pos=ctx.camera.pos
    )


#   def render(ctx, surface):
#     window_width, window_height = WINDOW_SIZE
#     hero = game.p1

#     visible_cells = hero.visible_cells
#     visited_cells = next((cells for floor, cells in game.memory if floor is game.floor), None)

#     anim_group = None
#     if len(game.anims) > 0:
#       anim_group = game.anims[0]

#     hero_x, hero_y = hero.cell
#     focus_x, focus_y = hero.cell
#     CAMERA_SPEED = 8
#     if game.room:
#       focus_x, focus_y = game.room.get_center()
#       CAMERA_SPEED = 16
#     elif anim_group:
#       for anim in anim_group:
#         if anim.target is hero and type(anim) is MoveAnim and not anim.done:
#           focus_x, focus_y = anim.cur_cell
#           break

#     camera_x = -((focus_x + 0.5) * TILE_SIZE - window_width / 2)
#     camera_y = -((focus_y + 0.5) * TILE_SIZE - window_height / 2)
#     if camera is not None:
#       old_camera_x, old_camera_y = camera
#       camera_x = old_camera_x + (camera_x - old_camera_x) / CAMERA_SPEED
#       camera_y = old_camera_y + (camera_y - old_camera_y) / CAMERA_SPEED
#     camera = (camera_x, camera_y)

#     (floor_width, floor_height) = game.floor.size
#     surface.fill((0, 0, 0))
#     for x, y in visited_cells:
#       tile = game.floor.get_tile_at((x, y))
#       sprite = None
#       if tile is Stage.WALL or tile is Stage.DOOR_HIDDEN:
#         if game.floor.get_tile_at((x, y + 1)) is Stage.FLOOR:
#           sprite = sprites["wall_base"]
#         else:
#           sprite = sprites["wall"]
#       elif tile is Stage.STAIRS_UP:
#         sprite = sprites["stairs_up"]
#       elif tile is Stage.STAIRS_DOWN:
#         sprite = sprites["stairs_down"]
#       elif tile is Stage.DOOR:
#         sprite = sprites["door"]
#       elif tile is Stage.DOOR_OPEN:
#         sprite = sprites["door_open"]
#       elif tile is Stage.FLOOR:
#         sprite = sprites["floor"]
#       if sprite:
#         opacity = 255
#         if (x, y) not in visible_cells:
#           distance = math.sqrt(math.pow(x - hero_x, 2) + math.pow(y - hero_y, 2))
#           opacity = (1 - distance / 8) * 128
#         sprite.set_alpha(opacity)
#         surface.blit(sprite, (round(x * TILE_SIZE + camera_x), round(y * TILE_SIZE + camera_y)))
#         sprite.set_alpha(None)

#     # depth sorting
#     def get_actor_y(actor):
#       return actor.cell[1]
#     game.floor.actors.sort(key=get_actor_y)

#     is_drawing_knight = False
#     is_drawing_mage = False

#     for actor in game.floor.actors:
#       if actor.cell not in visible_cells:
#         continue

#       (col, row) = actor.cell
#       sprite_x = col * TILE_SIZE
#       sprite_y = row * TILE_SIZE

#       sprite = None
#       if type(actor) is Knight:
#         sprite = sprites["knight"]
#       elif type(actor) is Mage:
#         sprite = sprites["mage"]
#       elif type(actor) is Eye:
#         sprite = sprites["eye"]
#       elif type(actor) is Chest:
#         if actor.opened:
#           sprite = sprites["chest_open"]
#         else:
#           sprite = sprites["chest"]

#       facing = None
#       if anim_group:
#         for anim in anim_group:
#           if anim.target is not actor:
#             continue

#           if type(anim) is ShakeAnim:
#             sprite_x += anim.update()
#             if type(actor) is Knight:
#               sprite = sprites["knight_flinch"]
#             elif type(actor) is Eye:
#               sprite = sprites["eye_flinch"]
#               will_awaken = next((anim for anim in anim_group if type(anim) is AwakenAnim), None)
#               if will_awaken:
#                 sprite = sprite.copy()
#                 pixels = PixelArray(sprite)
#                 pixels.replace(RED, PURPLE)
#                 pixels.close()

#           if type(anim) is FlickerAnim:
#             visible = anim.update()
#             if not visible:
#               sprite = None
#             elif type(actor) is Knight:
#               sprite = sprites["knight_flinch"]
#             elif type(actor) is Eye:
#               sprite = sprites["eye_flinch"]

#           if type(anim) is AwakenAnim and len(anim_group) == 1:
#             if type(actor) is Eye:
#               sprite = sprites["eye_attack"]
#             recolored = anim.update()
#             if recolored and sprite:
#               sprite = sprite.copy()
#               pixels = PixelArray(sprite)
#               pixels.replace(RED, PURPLE)
#               pixels.close()

#           if type(anim) is AttackAnim:
#             if type(actor) is Eye:
#               sprite = sprites["eye_attack"]

#           if type(anim) in (AttackAnim, MoveAnim):
#             src_x, src_y = anim.src_cell
#             dest_x, dest_y = anim.dest_cell
#             if dest_x < src_x:
#               facing = -1
#             elif dest_x > src_x:
#               facing = 1
#             col, row = anim.update()
#             sprite_x = col * TILE_SIZE
#             sprite_y = row * TILE_SIZE

#         if anim.done:
#           anim_group.remove(anim)
#           if len(anim_group) == 0:
#             game.anims.remove(anim_group)

#       if type(actor) is Eye and actor.asleep and sprite:
#         sprite = sprite.copy()
#         pixels = PixelArray(sprite)
#         pixels.replace(RED, PURPLE)
#         pixels.close()

#       for group in game.anims:
#         for anim in group:
#           if anim.target is actor and type(anim) is MoveAnim and group is not anim_group:
#             col, row = anim.src_cell
#             sprite_x = col * TILE_SIZE
#             sprite_y = row * TILE_SIZE

#       existing_facing = next((facing for facing in facings if facing[0] is actor), None)
#       if facing is None:
#         if existing_facing:
#           actor, facing = existing_facing
#       else:
#         if existing_facing in facings:
#           facings.remove(existing_facing)
#         facings.append((actor, facing))

#       if sprite and type(actor) is Knight:
#         is_drawing_knight = True

#       if sprite and type(actor) is Mage:
#         is_drawing_mage = True

#       is_flipped = facing == -1
#       if sprite:
#         surface.blit(pygame.transform.flip(sprite, is_flipped, False), (sprite_x + camera_x, sprite_y + camera_y))

#     if anim_group:
#       for anim in anim_group:
#         if type(anim) is PauseAnim:
#           anim.update()

#         if anim.done:
#           anim_group.remove(anim)
#           if len(anim_group) == 0:
#             game.anims.remove(anim_group)

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

#   def move(game, actor, delta):
#     actor_x, actor_y = actor.cell
#     delta_x, delta_y = delta
#     target_cell = (actor_x + delta_x, actor_y + delta_y)
#     target_tile = game.floor.get_tile_at(target_cell)
#     target_actor = game.floor.get_actor_at(target_cell)
#     if not target_tile.solid and (target_actor is None or actor is game.p1 and target_actor is game.p2):
#       game.anims.append([
#         MoveAnim(
#           duration=Game.MOVE_DURATION,
#           target=actor,
#           src_cell=actor.cell,
#           dest_cell=target_cell
#         )
#       ])
#       actor.cell = target_cell
#       return True
#     else:
#       return False

#   def handle_move(game, delta):
#     hero = game.p1
#     ally = game.p2
#     if hero.dead:
#       return False
#     hero.facing = delta
#     hero_x, hero_y = hero.cell
#     delta_x, delta_y = delta
#     acted = False
#     moved = game.move(hero, delta)
#     target_cell = (hero_x + delta_x, hero_y + delta_y)
#     target_tile = game.floor.get_tile_at(target_cell)
#     target_actor = game.floor.get_actor_at(target_cell)
#     if moved:
#       if not ally.dead:
#         last_group = game.anims[len(game.anims) - 1]
#         ally_x, ally_y = ally.cell
#         game.move(ally, (hero_x - ally_x, hero_y - ally_y))
#         last_group.append(game.anims.pop()[0])
#       game.refresh_fov()

#       if target_tile is Stage.STAIRS_UP:
#         game.log.print("There's a staircase going up here.")
#       elif target_tile is Stage.STAIRS_DOWN:
#         if game.floors.index(game.floor):
#           game.log.print("There's a staircase going down here.")
#         else:
#           game.log.print("You can return to the town from here.")

#       if not hero.dead:
#         hero.regen()
#       if not ally.dead:
#         ally.regen()

#       acted = True
#       game.sp = max(0, game.sp - 1 / 100)
#     elif target_actor and type(target_actor) is Eye:
#       game.attack(hero, target_actor)
#       game.sp = max(0, game.sp - 1)
#       acted = True
#     else:
#       game.anims.append([
#         AttackAnim(
#           duration=Game.ATTACK_DURATION,
#           target=hero,
#           src_cell=hero.cell,
#           dest_cell=target_cell
#         )
#       ])
#       if target_actor and type(target_actor) is Chest:
#         if target_actor.contents:
#           if not game.inventory.is_full():
#             contents = target_actor.open()
#             game.inventory.append(contents)
#             game.log.print("You open the lamp")
#             game.log.print("Received " + contents + ".")
#             acted = True
#           else:
#             game.log.print("Your inventory is already full!")
#         else:
#           game.log.print("There's nothing left to take...")
#       elif target_tile is Stage.DOOR:
#         game.log.print("You open the door.")
#         game.floor.set_tile_at(target_cell, Stage.DOOR_OPEN)
#         acted = True
#       elif target_tile is Stage.DOOR_HIDDEN:
#         game.log.print("Discovered a hidden door!")
#         game.floor.set_tile_at(target_cell, Stage.DOOR_OPEN)
#         acted = True
#       game.refresh_fov()
#     if acted:
#       game.step()
#     return moved

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
