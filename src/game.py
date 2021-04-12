import gen
import fov
import random
from cell import is_adjacent
from stage import Stage
from log import Log
from inventory import Inventory
from anims import AttackAnim, FlickerAnim, MoveAnim, ShakeAnim, PauseAnim
from actors import Knight, Mage, Eye, Chest

class Game:
  MOVE_DURATION = 8
  ATTACK_DURATION = 12
  SHAKE_DURATION = 30
  FLICKER_DURATION = 30
  PAUSE_DURATION = 15

  def __init__(game):
    game.log = Log()
    game.inventory = Inventory(2, 2)
    game.anims = []
    game.room = None
    game.sp_max = 40
    game.sp = game.sp_max
    game.floors = []
    game.floor = None
    game.p1 = None
    game.p2 = None
    game.load_floor()

  def refresh_fov(game):
    hero = game.p1
    hero.visible_cells = fov.shadowcast(game.floor, hero.cell, 3.5)
    rooms = [room for room in game.floor.rooms if hero.cell in room.get_cells() + room.get_border()]
    old_room = game.room
    if len(rooms) == 1:
      new_room = rooms[0]
    else:
      new_room = next((room for room in rooms if room is not game.room), None)
    if new_room is not old_room:
      game.room = new_room
    if game.room:
      hero.visible_cells += game.room.get_cells() + game.room.get_border()

  def load_floor(game):
    players = None
    if game.p1 and game.p2:
      players = (game.p1, game.p2)
    game.floor = gen.dungeon(19, 19, players)
    cells = game.floor.get_cells()
    for cell in cells:
      if game.floor.get_tile_at(cell) is Stage.DOOR_HIDDEN:
        game.log.print("There's an air of mystery about this floor...")
        break
    if players is None:
      game.p1 = next((actor for actor in game.floor.actors if type(actor) is Knight), None)
      game.p2 = next((actor for actor in game.floor.actors if type(actor) is Mage), None)
    game.refresh_fov()
    game.floors.append(game.floor)

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
      if target_tile is Stage.STAIRS:
        game.log.print("There's a staircase going up here.")
      if not hero.dead:
        hero.regen()
      if not ally.dead:
        ally.regen()
      acted = True
    elif target_actor and type(target_actor) is Eye:
      game.log.print(hero.name.upper() + " attacks")
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

    def on_flicker_end(_):
      game.floor.actors.remove(target)
      if target.faction == "player":
        game.swap()

    def on_shake_end(_):
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
        game.anims[0].append(PauseAnim(
          duration=Game.PAUSE_DURATION,
          target=target
        ))

    def on_connect(_):
      damage = actor.attack(target)
      verb = "suffers" if actor.faction == "enemy" else "receives"
      game.log.print(target.name.upper() + " " + verb + " " + str(damage) + " damage.")
      if was_asleep and not target.asleep:
        game.log.print(target.name.upper() + " woke up!")
      game.anims[0].append(ShakeAnim(
        duration=Game.SHAKE_DURATION,
        target=target,
        on_end=on_shake_end
      ))

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

  def swap(game):
    if game.p2.dead:
      return False
    game.p1, game.p2 = (game.p2, game.p1)
    game.refresh_fov()
    return True

  def special(game):
    if game.sp >= 2:
      if type(game.p1) is Knight:
        game.shield_bash()
      elif type(game.p1) is Mage:
        game.detect_mana()
      game.sp -= 2

  def detect_mana(game):
    game.log.print("MAGE uses Detect Mana")
    cells = game.p1.visible_cells
    for cell in cells:
      tile = game.floor.get_tile_at(cell)
      if tile is Stage.DOOR_HIDDEN:
        game.log.print("There's a hidden passage somewhere here.")
        break
    else:
      game.log.print("You don't sense anything magical nearby.")

  def shield_bash(game):
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

  def ascend(game):
    target_tile = game.floor.get_tile_at(game.p1.cell)
    if target_tile is Stage.STAIRS:
      game.floor += 1
      game.log.print("You go upstairs.")
      game.load_floor()
      return True
    return False

  def ascend(game):
    target_tile = game.floor.get_tile_at(game.p1.cell)
    if target_tile is not Stage.STAIRS:
      return False
    index = game.floors.index(game.floor) + 1
    if index < len(game.floors):
      game.floor = game.floors[index]
    else:
      game.load_floor()
    game.log.print("You go upstairs.")
    return True
