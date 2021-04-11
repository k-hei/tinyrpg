import gen
import fov
from cell import is_adjacent
from stage import Stage
from log import Log
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
    game.anims = []
    game.inventory = []
    game.room = None
    game.reload()

  def refresh_fov(game):
    hero = game.p1
    hero.visible_cells = fov.shadowcast(game.stage, hero.cell, 3.5)
    rooms = [room for room in game.stage.rooms if hero.cell in room.get_cells() + room.get_border()]
    if len(rooms) == 1:
      game.room = rooms[0]
    else:
      game.room = next((room for room in rooms if room is not game.room), None)
    if game.room:
      hero.visible_cells += game.room.get_cells() + game.room.get_border()

  def reload(game, swapped=False):
    game.stage = gen.dungeon(19, 19)
    cells = game.stage.get_cells()
    for cell in cells:
      if game.stage.get_tile_at(cell) is Stage.DOOR_HIDDEN:
        game.log.print("There's an air of mystery about this floor...")
        break
    game.p1 = next((actor for actor in game.stage.actors if type(actor) is Knight), None)
    game.p2 = next((actor for actor in game.stage.actors if type(actor) is Mage), None)
    if swapped:
      game.swap()
    else:
      game.refresh_fov()

  def move(game, delta):
    source_cell = game.p1.cell
    (hero_x, hero_y) = source_cell
    (delta_x, delta_y) = delta
    game.p1.facing = delta
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_tile = game.stage.get_tile_at(target_cell)
    target_actor = game.stage.get_actor_at(target_cell)
    if not target_tile.solid and (target_actor is None or target_actor is game.p2):
      game.anims.append(MoveAnim(
        duration=Game.MOVE_DURATION,
        target=game.p1,
        src_cell=source_cell,
        dest_cell=target_cell
      ))
      game.anims.append(MoveAnim(
        duration=Game.MOVE_DURATION,
        target=game.p2,
        src_cell=game.p2.cell,
        dest_cell=source_cell
      ))
      game.p2.cell = source_cell
      game.p1.cell = target_cell
      game.refresh_fov()
      if target_tile is Stage.STAIRS:
        game.log.print("There's a staircase going up here.")
      return True
    elif target_actor and type(target_actor) is Eye:
      game.log.print(game.p1.name.upper() + " attacks")
      game.attack(target_actor)
    else:
      game.anims.append(AttackAnim(
        duration=Game.ATTACK_DURATION,
        target=game.p1,
        src_cell=source_cell,
        dest_cell=target_cell
      ))
      if target_actor and type(target_actor) is Chest:
        if target_actor.contents:
          contents = target_actor.open()
          game.log.print("You open the lamp")
          game.log.print("Received a " + contents + ".")
        else:
          game.log.print("The lamp is already empty.")
      elif target_tile is Stage.DOOR:
        game.log.print("You open the door.")
        game.stage.set_tile_at(target_cell, Stage.DOOR_OPEN)
      elif target_tile is Stage.DOOR_HIDDEN:
        game.log.print("Discovered a hidden door!")
        game.stage.set_tile_at(target_cell, Stage.DOOR_OPEN)
      game.refresh_fov()
      return False

  def attack(game, target):
    def on_pause_end(_):
      damage = target.attack(game.p1)
      game.log.print("EYEBALL counters")
      game.log.print(game.p1.name.upper() + " suffers " + str(damage) + " damage.")
      game.anims.append(AttackAnim(
        duration=Game.ATTACK_DURATION,
        target=target,
        src_cell=target.cell,
        dest_cell=game.p1.cell,
        on_connect=lambda _:
          game.anims.append(ShakeAnim(
            duration=Game.SHAKE_DURATION,
            target=game.p1
          ))
      ))

    def on_shake_end(_):
      if target.dead:
        game.log.print("Defeated EYEBALL.")
        game.anims.append(FlickerAnim(
          duration=Game.FLICKER_DURATION,
          target=target,
          on_end=lambda _: game.stage.actors.remove(target)
        ))
      elif is_adjacent(game.p1.cell, target.cell):
        print("pause")
        game.anims.append(PauseAnim(
          duration=Game.PAUSE_DURATION,
          target=target,
          on_end=on_pause_end
        ))

    def on_connect(_):
      damage = game.p1.attack(target)
      game.log.print("EYEBALL receives " + str(damage) + " damage.")
      game.anims.append(ShakeAnim(
        duration=Game.SHAKE_DURATION,
        target=target,
        on_end=on_shake_end
      ))

    game.anims.append(AttackAnim(
      duration=Game.ATTACK_DURATION,
      target=game.p1,
      src_cell=game.p1.cell,
      dest_cell=target.cell,
      on_connect=on_connect
    ))



  def swap(game):
    game.p1, game.p2 = (game.p2, game.p1)
    game.refresh_fov()

  def special(game):
    if type(game.p1) is Knight:
      game.shield_bash()
    elif type(game.p1) is Mage:
      game.detect_mana()

  def detect_mana(game):
    game.log.print("MAGE uses Detect Mana")
    cells = game.p1.visible_cells
    for cell in cells:
      tile = game.stage.get_tile_at(cell)
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
    target_actor = game.stage.get_actor_at(target_cell)
    game.log.print("HERO uses Shield Bash")

    if target_actor and target_actor is not game.p2:
      # nudge target actor 1 square in the given direction
      target_x, target_y = target_cell
      nudge_cell = (target_x + delta_x, target_y + delta_y)
      nudge_tile = game.stage.get_tile_at(nudge_cell)
      nudge_actor = game.stage.get_actor_at(nudge_cell)
      game.anims.append(ShakeAnim(duration=Game.SHAKE_DURATION, target=target_actor))
      if not nudge_tile.solid and nudge_actor is None:
        target_actor.cell = nudge_cell
        game.anims.append(MoveAnim(
          duration=Game.MOVE_DURATION,
          target=target_actor,
          src_cell=target_cell,
          dest_cell=nudge_cell
        ))
        if type(target_actor) is Eye:
          game.log.print("EYEBALL is reeling.")
      if type(target_actor) is Eye:
        game.attack(target_actor)
    else:
      game.log.print("But nothing happened...")
      game.anims.append(AttackAnim(
        duration=Game.ATTACK_DURATION,
        target=game.p1,
        src_cell=game.p1.cell,
        dest_cell=target_cell
      ))

  def ascend(game):
    target_tile = game.stage.get_tile_at(game.p1.cell)
    if target_tile is Stage.STAIRS:
      game.log.print("You go upstairs.")
      swapped = type(game.p1) is Mage
      game.reload(swapped)
      return True
    return False
