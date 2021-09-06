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

  def spawn_cloud(game, cell, inclusive=False, on_end=None):
    target_area = neighborhood(cell, radius=2, inclusive=inclusive)
    targets = [e for e in game.floor.elems if (
      isinstance(e, DungeonActor)
      and not e.is_dead()
      and e.ailment != "poison"
      and e.cell in target_area
    )]

    def poison():
      if targets:
        target = targets.pop()
      else:
        game.camera.blur()
        on_end and on_end()
        return
      game.poison_actor(target, on_end=poison)

    for target_cell in target_area:
      game.floor.spawn_elem_at(target_cell, PoisonPuff(origin=cell))
    not game.anims and game.anims.append([])
    game.anims += [
      [PauseAnim(duration=30)],
      [PauseAnim(duration=1, on_end=poison)],
    ]

  def effect(user, dest, game, on_end=None):
    if user.get_hp():
      game.anims.append([BounceAnim(
        target=user,
        on_squash=lambda: Virus.spawn_cloud(game, cell=user.cell, on_end=on_end)
      )])
    else:
      Virus.spawn_cloud(game, cell=user.cell, on_end=on_end)
    return user.cell
