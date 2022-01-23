from random import randint
from lib.cell import is_adjacent
import assets
from dungeon.actors import DungeonActor
from cores import Core, Stats
from skills.attack.shieldbash import ShieldBash
from skills.weapon.club import Club

class Skeleton(DungeonActor):
  skill = ShieldBash
  drops = [Club]

  def __init__(skeleton, rare=False, *args, **kwargs):
    super().__init__(Core(
      name="Skeleton",
      faction="enemy",
      stats=Stats(
        hp=138,
        st=12,
        dx=7,
        ag=1,
        en=-4,
        lu=-6,
      ),
      skills=[ Club, ShieldBash ]
    ), *args, **kwargs)
    if rare:
      skeleton.promote()

  def step(skeleton, game):
    enemy = game.find_closest_enemy(skeleton)
    if enemy is None:
      return None

    if is_adjacent(skeleton.cell, enemy.cell):
      if randint(1, 3) == 1:
        skeleton.face(enemy.cell)
        return ("use_skill", ShieldBash)
      else:
        return ("attack", enemy)
    else:
      return ("move_to", enemy.cell)

  def view(skeleton, anims):
    return super().view(assets.sprites["skeleton"], anims)
