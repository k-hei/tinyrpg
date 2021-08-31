import math
from skills.ailment import AilmentSkill
from anims.bounce import BounceAnim
from anims.flinch import FlinchAnim
from anims.pause import PauseAnim
from dungeon.actors import DungeonActor
from cores.mage import Mage
from lib.cell import is_adjacent
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
  chant_turns: int = 2

  def effect(user, dest, game, on_end=None):
    targets = [e for e in game.floor.elems if (
      isinstance(e, DungeonActor)
      and not e.is_dead()
      and not e.allied(user)
      and e.ailment != "poison"
      and is_adjacent(e.cell, user.cell)
    )]

    def poison():
      try:
        target = targets.pop()
      except IndexError:
        game.camera.blur()
        if on_end:
          on_end()
        return
      target.inflict_ailment("poison")
      game.camera.focus(target.cell)
      if ENABLED_COMBAT_LOG:
        game.log.print((target.token(), " is poisoned."))
      game.anims[0].extend([
        FlinchAnim(duration=45, target=target),
        PauseAnim(duration=60, on_end=poison)
      ])

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
      on_end=lambda: game.anims[0].append(PauseAnim(
        duration=15,
        on_end=on_bounce
      ))
    )])

    return user.cell
