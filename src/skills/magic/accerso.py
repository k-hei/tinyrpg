from skills.magic import MagicSkill
from anims.pause import PauseAnim
from anims.bounce import BounceAnim
from cores.mage import Mage

class Accerso(MagicSkill):
  name = "Accerso"
  desc = "Calls allies to your side"
  element = "shield"
  cost = 12
  range_min = 1
  range_max = 2
  range_type = "radial"
  users = [Mage]
  blocks = (
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
  )

  def effect(user, dest, game, on_end=None):
    def on_bounce():
      game.log.print("But nothing happened...")
      on_end and on_end()

    game.anims.append([BounceAnim(
      duration=20,
      target=user,
      on_end=lambda: game.anims[0].append(PauseAnim(
        duration=15,
        on_end=on_bounce
      ))
    )])
