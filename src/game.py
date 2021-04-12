import gen
import fov
import random
from cell import is_adjacent
from stage import Stage
from log import Log
from inventory import Inventory
from anims import AttackAnim, FlickerAnim, MoveAnim, ShakeAnim, PauseAnim, AwakenAnim
from actors import Knight, Mage, Eye, Chest

class Game:
  MOVE_DURATION = 8
  ATTACK_DURATION = 12
  SHAKE_DURATION = 30
  FLICKER_DURATION = 30
  PAUSE_DURATION = 15
  PAUSE_ITEM_DURATION = 30
  AWAKEN_DURATION = 45

  def __init__(game):
    game.log = Log()
    game.inventory = Inventory(2, 2)
    game.sp_max = 40
    game.sp = game.sp_max
    game.room = None
    game.floor = None
    game.floors = []
    game.memory = []
    game.anims = []
    game.p1 = Knight()
    game.p2 = Mage()
    game.load_floor()

  def refresh_fov(game):
    hero = game.p1
    visible_cells = fov.shadowcast(game.floor, hero.cell, 3.5)

    rooms = [room for room in game.floor.rooms if hero.cell in room.get_cells() + room.get_border()]
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
    hero.visible_cells = visible_cells

  def load_floor(game):
    floor = gen.dungeon((19, 19))
    hidden_door = floor.find_tile(Stage.DOOR_HIDDEN)
    if hidden_door:
      game.log.print("There's an air of mystery about this floor...")
    stairs_x, stairs_y = floor.find_tile(Stage.STAIRS_DOWN)
    floor.spawn_actor(game.p1, (stairs_x, stairs_y))
    if not game.p2.dead:
      floor.spawn_actor(game.p2, (stairs_x - 1, stairs_y))
    game.floor = floor
    game.floors.append(game.floor)
    game.memory.append((game.floor, []))
    game.refresh_fov()

  def step(game):
    enemies = [actor for actor in game.floor.actors if type(actor) is Eye]
    for enemy in enemies:
      game.step_enemy(enemy)

  def step_enemy(game, enemy):
    if enemy.dead or enemy.asleep:
      return False

    hero = game.p1
    room = next((room for room in game.floor.rooms if enemy.cell in room.get_cells()), None)
    if not room or hero.cell not in room.get_cells():
      return False

    if is_adjacent(enemy.cell, hero.cell):
      if not hero.dead:
        game.attack(enemy, hero)
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
      game.move(enemy, (delta_x, delta_y))

    return True

  def move(game, actor, delta):
    actor_x, actor_y = actor.cell
    delta_x, delta_y = delta
    target_cell = (actor_x + delta_x, actor_y + delta_y)
    target_tile = game.floor.get_tile_at(target_cell)
    target_actor = game.floor.get_actor_at(target_cell)
    if not target_tile.solid and (target_actor is None or actor is game.p1 and target_actor is game.p2):
      game.anims.append([
        MoveAnim(
          duration=Game.MOVE_DURATION,
          target=actor,
          src_cell=actor.cell,
          dest_cell=target_cell
        )
      ])
      actor.cell = target_cell
      return True
    else:
      return False

  def handle_move(game, delta):
    hero = game.p1
    ally = game.p2
    if hero.dead:
      return False
    hero.facing = delta
    hero_x, hero_y = hero.cell
    delta_x, delta_y = delta
    acted = False
    moved = game.move(hero, delta)
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_tile = game.floor.get_tile_at(target_cell)
    target_actor = game.floor.get_actor_at(target_cell)
    if moved:
      if not ally.dead:
        last_group = game.anims[len(game.anims) - 1]
        ally_x, ally_y = ally.cell
        game.move(ally, (hero_x - ally_x, hero_y - ally_y))
        last_group.append(game.anims.pop()[0])
      game.refresh_fov()

      if target_tile is Stage.STAIRS_UP:
        game.log.print("There's a staircase going up here.")
      elif target_tile is Stage.STAIRS_DOWN:
        if game.floors.index(game.floor):
          game.log.print("There's a staircase going down here.")
        else:
          game.log.print("You can return to the town from here.")

      if not hero.dead:
        hero.regen()
      if not ally.dead:
        ally.regen()

      acted = True
      game.sp = max(0, game.sp - 1 / 100)
    elif target_actor and type(target_actor) is Eye:
      game.attack(hero, target_actor)
      game.sp = max(0, game.sp - 1)
      acted = True
    else:
      game.anims.append([
        AttackAnim(
          duration=Game.ATTACK_DURATION,
          target=hero,
          src_cell=hero.cell,
          dest_cell=target_cell
        )
      ])
      if target_actor and type(target_actor) is Chest:
        if target_actor.contents:
          if not game.inventory.is_full():
            contents = target_actor.open()
            game.inventory.append(contents)
            game.log.print("You open the lamp")
            game.log.print("Received " + contents + ".")
            acted = True
          else:
            game.log.print("Your inventory is already full!")
        else:
          game.log.print("There's nothing left to take...")
      elif target_tile is Stage.DOOR:
        game.log.print("You open the door.")
        game.floor.set_tile_at(target_cell, Stage.DOOR_OPEN)
        acted = True
      elif target_tile is Stage.DOOR_HIDDEN:
        game.log.print("Discovered a hidden door!")
        game.floor.set_tile_at(target_cell, Stage.DOOR_OPEN)
        acted = True
      game.refresh_fov()
    if acted:
      game.step()
    return moved

  def attack(game, actor, target):
    was_asleep = target.asleep
    game.log.print(actor.name.upper() + " attacks")

    def on_flicker_end():
      game.floor.actors.remove(target)
      if target.faction == "player":
        game.swap()

    def on_awaken_end():
      game.log.print(target.name.upper() + " woke up!")
      game.anims[0].append(PauseAnim(duration=Game.PAUSE_DURATION))

    def on_shake_end():
      if target.dead:
        if target.faction == "enemy":
          game.log.print("Defeated " + target.name.upper() + ".")
        else:
          game.log.print(target.name.upper() + " is defeated.")
        game.anims[0].append(FlickerAnim(
          duration=Game.FLICKER_DURATION,
          target=target,
          on_end=on_flicker_end
        ))
      elif is_adjacent(actor.cell, target.cell):
        game.anims[0].append(PauseAnim(duration=Game.PAUSE_DURATION))

    def on_connect():
      damage = actor.attack(target)
      verb = "suffers" if actor.faction == "enemy" else "receives"
      game.log.print(target.name.upper() + " " + verb + " " + str(damage) + " damage.")
      game.anims[0].append(ShakeAnim(
        duration=Game.SHAKE_DURATION,
        target=target,
        on_end=on_shake_end
      ))
      if was_asleep and not target.asleep:
        game.anims[0].append(AwakenAnim(
          duration=Game.AWAKEN_DURATION,
          target=target,
          on_end=on_awaken_end)
        )

    damage = actor.find_damage(target)
    if damage >= target.hp:
      target.dead = True

    game.anims.append([
      AttackAnim(
        duration=Game.ATTACK_DURATION,
        target=actor,
        src_cell=actor.cell,
        dest_cell=target.cell,
        on_connect=on_connect
      )
    ])

  def use_item(game):
    hero = game.p1
    if len(game.inventory.items) == 0:
      game.log.print("No items to use!")
      return
    item = game.inventory.items[0]
    game.inventory.items.remove(item)
    game.log.print("Used " + item)
    if item == "Potion":
      game.log.print(hero.name.upper() + " restored 10 HP.")
      hero.regen(10)
    elif item == "Bread":
      game.log.print("The party restored 5 SP.")
      if game.sp + 5 < game.sp_max:
        game.sp += 5
      else:
        game.sp = game.sp_max
    else:
      game.log.print("But nothing happened...")
    game.anims.append([ PauseAnim(duration=Game.PAUSE_ITEM_DURATION) ])
    game.step()

  def swap(game):
    if game.p2.dead:
      return False
    game.p1, game.p2 = (game.p2, game.p1)
    game.refresh_fov()
    return True

  def special(game):
    if type(game.p1) is Knight:
      game.shield_bash()
    elif type(game.p1) is Mage:
      game.detect_mana()

  def detect_mana(game):
    if game.sp >= 1:
      game.sp = max(0, game.sp - 1)
    def search():
      cells = game.p1.visible_cells
      for cell in cells:
        tile = game.floor.get_tile_at(cell)
        if tile is Stage.DOOR_HIDDEN:
          game.log.print("There's a hidden passage somewhere here.")
          break
      else:
        game.log.print("You don't sense anything magical nearby.")
    game.log.print("MAGE uses Detect Mana")
    game.anims.append([ PauseAnim(duration=30, on_end=search) ])

  def shield_bash(game):
    if game.sp >= 2:
      game.sp = max(0, game.sp - 2)
    source_cell = game.p1.cell
    hero_x, hero_y = source_cell
    delta_x, delta_y = game.p1.facing
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_actor = game.floor.get_actor_at(target_cell)
    game.log.print("HERO uses Shield Bash")

    if target_actor and target_actor is not game.p2:
      # nudge target actor 1 square in the given direction
      target_x, target_y = target_cell
      nudge_cell = (target_x + delta_x, target_y + delta_y)
      nudge_tile = game.floor.get_tile_at(nudge_cell)
      nudge_actor = game.floor.get_actor_at(nudge_cell)
      game.anims.append([
        ShakeAnim(duration=Game.SHAKE_DURATION, target=target_actor)
      ])
      if not nudge_tile.solid and nudge_actor is None:
        target_actor.cell = nudge_cell
        game.anims.append([
          MoveAnim(
            duration=Game.MOVE_DURATION,
            target=target_actor,
            src_cell=target_cell,
            dest_cell=nudge_cell
          )
        ])
      if type(target_actor) is Eye:
        game.attack(target_actor)
        game.log.print("EYEBALL is reeling.")
    else:
      game.log.print("But nothing happened...")
      game.anims.append([
        AttackAnim(
          duration=Game.ATTACK_DURATION,
          target=game.p1,
          src_cell=game.p1.cell,
          dest_cell=target_cell
        )
      ])

  def change_floors(game, direction):
    exit_tile = Stage.STAIRS_UP if direction == 1 else Stage.STAIRS_DOWN
    entry_tile = Stage.STAIRS_DOWN if direction == 1 else Stage.STAIRS_UP
    text = "You go upstairs." if direction == 1 else "You go downstairs."

    if direction not in (1, -1):
      return False

    target_tile = game.floor.get_tile_at(game.p1.cell)
    if target_tile is not exit_tile:
      return False

    game.log.print(text)
    old_floor = game.floor
    old_floor.remove_actor(game.p1)
    old_floor.remove_actor(game.p2)

    index = game.floors.index(game.floor) + direction
    if index >= len(game.floors):
      # create a new floor if out of bounds
      game.load_floor()
    elif index >= 0:
      # go back to old floor if within bounds
      new_floor = game.floors[index]
      stairs_x, stairs_y = new_floor.find_tile(entry_tile)
      new_floor.spawn_actor(game.p1, (stairs_x, stairs_y))
      if not game.p2.dead:
        new_floor.spawn_actor(game.p2, (stairs_x - 1, stairs_y))
      game.floor = new_floor
      game.refresh_fov()

    return True
