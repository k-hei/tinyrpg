from skills import Skill
from anims.bounce import BounceAnim
from anims.flinch import FlinchAnim
from anims.pause import PauseAnim
import math
from actors import Actor
from actors.mage import Mage
from lib.cell import is_adjacent

ATTACK_DURATION = 12

class Virus(Skill):
  name = "Virus"
  kind = "ailment"
  element = "dark"
  desc = "Poisons adjacent targets"
  cost = 4
  range_type = "radial"
  users = (Mage,)
  blocks = (
    (0, 0),
    (1, 0),
    (1, 1),
  )

  def effect(user, game, on_end=None):
    targets = [e for e in game.floor.elems if (
      isinstance(e, Actor)
      and not e.dead
      and e.faction != user.faction
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
      target.inflict("poison")
      game.camera.focus(target.cell)
      game.log.print(target.token(), " is poisoned.")
      game.anims[0].extend([
        FlinchAnim(duration=45, target=target),
        PauseAnim(duration=120, on_end=poison)
      ])

    def on_bounce():
      if targets:
        poison()
      else:
        game.log.print("But nothing happened...")
        if on_end:
          on_end()

    game.anims.append([BounceAnim(
      duration=20,
      target=user,
      on_end=lambda: game.anims[0].append(PauseAnim(
        duration=60,
        on_end=on_bounce
      ))
    )])

    return user.cell
