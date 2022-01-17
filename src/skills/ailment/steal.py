from skills.ailment import AilmentSkill
from items.materials import MaterialItem
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from config import ATTACK_DURATION

from dungeon.actors import DungeonActor
from cores.rogue import Rogue

class Steal(AilmentSkill):
  name = "Steal"
  kind = "ailment"
  element = "dark"
  desc = "Steals an item"
  cost = 3
  users = [Rogue]
  blocks = (
    (0, 0),
    (0, 1),
  )

  def effect(user, dest, game, on_end=None):
    source_cell = user.cell
    hero_x, hero_y = source_cell
    delta_x, delta_y = user.facing
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_elem = game.stage.get_elem_at(target_cell, superclass=DungeonActor)
    def on_connect():
      item = next((i for i in game.parent.inventory.items if not isinstance(i, MaterialItem)), None)
      if item:
        game.parent.inventory.items.remove(item)
        user.item = item
        game.log.print((user.token(), " stole ", item().token(), "!"))
      else:
        game.log.print("But nothing happened...")
    game.anims.append([AttackAnim(
      duration=ATTACK_DURATION,
      target=user,
      src=user.cell,
      dest=target_cell,
      on_connect=on_connect
    )])
    return target_cell
