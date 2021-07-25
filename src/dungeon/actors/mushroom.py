from dungeon.actors import DungeonActor
from cores import Core, Stats
from assets import load as use_assets
from skills.ailment.virus import Virus
from skills.weapon.tackle import Tackle
from lib.cell import is_adjacent
import random
from items.materials.redferrule import RedFerrule
from sprite import Sprite

from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from config import PUSH_DURATION

class Mushroom(DungeonActor):
  skill = Virus
  drops = [RedFerrule]

  def __init__(mushroom, *args, **kwargs):
    super().__init__(Core(
      name="Toadstool",
      faction="enemy",
      stats=Stats(
        hp=19,
        st=14,
        dx=4,
        ag=4,
        en=10,
      ),
      skills=[Tackle, Virus]
    ), *args, **kwargs)

  def step(actor, game):
    enemy = game.find_closest_enemy(actor)
    if enemy is None:
      return False

    if is_adjacent(actor.cell, enemy.cell):
      if random.randint(1, 5) == 1:
        game.use_skill(actor, Virus)
      else:
        game.attack(actor, enemy)
    else:
      game.move_to(actor, enemy.cell)

    return True

  def view(mushroom, anims):
    sprites = use_assets().sprites
    sprite = None
    if mushroom.is_dead():
      return super().view(sprites["mushroom_flinch"], anims)
    anim_group = [a for a in anims[0] if a.target is mushroom] if anims else []
    for anim in anim_group:
      if type(anim) is MoveAnim and anim.duration != PUSH_DURATION:
        sprite = sprites["mushroom_move"]
        break
      elif (type(anim) is AttackAnim
      and anim.time < anim.duration // 2):
        sprite = sprites["mushroom_move"]
        break
      elif type(anim) in (FlinchAnim, FlickerAnim):
        sprite = sprites["mushroom_flinch"]
        break
    else:
      if mushroom.ailment == "sleep":
        sprite = sprites["mushroom_sleep"]
      else:
        sprite = sprites["mushroom"]
    if mushroom.ailment == "freeze":
      sprite = sprites["mushroom_flinch"]
    return super().view(sprite, anims)
