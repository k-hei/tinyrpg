from dungeon.actors import DungeonActor
from cores import Core, Stats
from skills.ailment.virus import Virus
from skills.weapon.tackle import Tackle
from lib.cell import is_adjacent
import random
from items.materials.redferrule import RedFerrule
import assets
from sprite import Sprite

from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.shake import ShakeAnim
from config import PUSH_DURATION

class Mushroom(DungeonActor):
  skill = Virus
  drops = [RedFerrule]

  class ChargeAnim(ShakeAnim): pass

  def __init__(mushroom, chant_skill=None, chant_turns=0, *args, **kwargs):
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
    mushroom.chant_skill = chant_skill
    mushroom.chant_turns = chant_turns

  def chant(mushroom, skill, dest, game):
    mushroom.stats.ag = game.hero.stats.ag
    mushroom.chant_skill = skill
    mushroom.chant_turns = skill.chant_turns
    mushroom.core.anims.append(Mushroom.ChargeAnim())

  def cast(mushroom):
    if mushroom.chant_skill is None:
      return None
    command = ("use_skill", mushroom.chant_skill)
    mushroom.chant_skill = None
    mushroom.chant_turns = 0
    mushroom.stats.ag = mushroom.core.stats.ag
    mushroom.core.anims.clear()
    return command

  def step(mushroom, game):
    enemy = game.find_closest_enemy(mushroom)
    if enemy is None:
      return False

    if mushroom.chant_turns:
      mushroom.chant_turns -= 1
      if mushroom.chant_turns == 1:
        return mushroom.cast()
      else:
        return None

    if is_adjacent(mushroom.cell, enemy.cell):
      if random.randint(1, 5) == 1:
        return mushroom.chant(
          game=game,
          skill=Virus,
          dest=game.hero.cell
        )
      else:
        game.attack(mushroom, enemy)
    else:
      game.move_to(mushroom, enemy.cell)

    return True

  def view(mushroom, anims):
    mushroom_image = None
    offset_x, offset_y = 0, 0
    if mushroom.is_dead():
      return super().view(assets.sprites["mushroom_flinch"], anims)
    anim_group = [a for a in anims[0] if a.target is mushroom] if anims else []
    anim_group += mushroom.core.anims
    for anim in anim_group:
      if type(anim) is MoveAnim and anim.duration != PUSH_DURATION:
        mushroom_image = assets.sprites["mushroom_move"]
        break
      elif (type(anim) is AttackAnim
      and anim.time < anim.duration // 2):
        mushroom_image = assets.sprites["mushroom_move"]
        break
      elif type(anim) in (FlinchAnim, FlickerAnim):
        mushroom_image = assets.sprites["mushroom_flinch"]
        break
      elif type(anim) is Mushroom.ChargeAnim:
        mushroom_image = assets.sprites["mushroom_move"]
        offset_x += anim.offset
        break
    else:
      if mushroom.ailment == "sleep":
        mushroom_image = assets.sprites["mushroom_sleep"]
      else:
        mushroom_image = assets.sprites["mushroom"]
    if mushroom.ailment == "freeze":
      mushroom_image = assets.sprites["mushroom_flinch"]
    return super().view([Sprite(
      image=mushroom_image,
      pos=(offset_x, offset_y)
    )], anims)
