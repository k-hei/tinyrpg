import math
from skills.ailment import AilmentSkill
from anims.bounce import BounceAnim
from anims.flinch import FlinchAnim
from anims.pause import PauseAnim
from dungeon.actors import DungeonActor
from cores.mage import Mage
from lib.cell import is_adjacent, neighborhood
from dungeon.props.poisonpuff import PoisonPuff
from config import ENABLED_COMBAT_LOG

ATTACK_DURATION = 12

class Virus(AilmentSkill):
  name: str = "Virus"
  desc: str = "Poisons adjacent targets"
  element: str = "dark"
  cost: int = 4
  users: tuple = (Mage,)
  blocks: tuple = (
    (0, 0),
    (1, 0),
    (1, 1),
  )
  charge_turns: int = 2

  def effect(user, dest, game, on_end=None):
    target_area = neighborhood(cell=user.cell, radius=2)
    targets = [e for e in game.floor.elems if (
      isinstance(e, DungeonActor)
      and not e.is_dead()
      and not e.allied(user)
      and e.ailment != "poison"
      and e.cell in target_area
    )]

    def poison():
      try:
        target = targets.pop()
      except IndexError:
        game.camera.blur()
        if on_end:
          on_end()
        return
      game.poison_actor(target, on_end=poison)

    def spawn_puffs():
      for cell in target_area:
        game.floor.spawn_elem_at(cell, PoisonPuff(origin=user.cell))

    def on_bounce():
      if targets:
        poison()
      else:
        if ENABLED_COMBAT_LOG:
          game.log.print("But nothing happened...")
        if on_end:
          on_end()

    game.anims.append([BounceAnim(
      duration=20,
      target=user,
      on_squash=spawn_puffs,
      on_end=lambda: game.anims[0].append(PauseAnim(
        duration=15,
        on_end=on_bounce
      ))
    )])

    return user.cell
