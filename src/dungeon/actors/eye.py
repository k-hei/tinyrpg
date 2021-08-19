from random import randint, choice
from lib.cell import is_adjacent, neighborhood
from dungeon.actors import DungeonActor
from cores import Core, Stats
from assets import sprites
from skills import Skill
from skills.weapon.tackle import Tackle
from skills.armor.hpup import HpUp
from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.bounce import BounceAnim
from anims.awaken import AwakenAnim
from anims.shake import ShakeAnim
from anims.pause import PauseAnim
from items.materials.angeltears import AngelTears
from sprite import Sprite
from filters import replace_color
from colors.palette import BLACK, CYAN
from config import PUSH_DURATION

def IdleSprite(facing):
  if facing == (0, 1):
    return sprites["eyeball"]
  elif facing == (0, -1):
    return sprites["eyeball_up"]
  elif facing[0]:
    return sprites["eyeball_right"]

def MoveSprite(facing):
  if facing == (0, 1):
    return sprites["eyeball_move"]
  elif facing == (0, -1):
    return sprites["eyeball_move_up"]
  elif facing[0]:
    return sprites["eyeball_move_right"]

def FlinchSprite(facing):
  if facing == (0, 1):
    return sprites["eyeball_flinch"]
  elif facing == (0, -1):
    return sprites["eyeball_flinch_up"]
  elif facing[0]:
    return sprites["eyeball_flinch_right"]

def ChargeSprite(facing):
  if facing == (0, 1):
    return sprites["eyeball_charge"]
  elif facing == (0, -1):
    return sprites["eyeball_charge_up"]
  elif facing[0]:
    return sprites["eyeball_charge_right"]

def SleepSprite(facing):
  if facing == (0, 1):
    return sprites["eyeball_sleep"]
  elif facing == (0, -1):
    return sprites["eyeball_sleep_up"]
  elif facing[0]:
    return sprites["eyeball_sleep_right"]

class Meyetosis(Skill):
  name = "Meyetosis"
  chant_turns = 2
  def effect(user, dest, game, on_end=None):
    neighbors = [c for c in neighborhood(user.cell) if game.floor.is_cell_empty(c)]
    if neighbors:
      neighbor = choice(neighbors)
      clone = Eyeball(clone=True, facing=user.facing)
      game.floor.spawn_elem_at(neighbor, clone)
      game.anims.append([
        BounceAnim(
          duration=20,
          target=user
        ),
        PauseAnim(duration=10),
        Eyeball.SplitAnim(
          duration=30,
          target=clone,
          src=user.cell,
          dest=neighbor,
          on_end=on_end
        )
      ])

class Eyeball(DungeonActor):
  drops = [AngelTears]
  skill = HpUp
  CLONES_MAX = 3

  class ChargeAnim(ShakeAnim): pass
  class SplitAnim(MoveAnim): pass

  def __init__(eyeball, faction="enemy", rare=False, chant_skill=None, chant_turns=0, clones=0, clone=False, *args, **kwargs):
    super().__init__(Core(
      name="Eyeball",
      faction=faction,
      stats=Stats(
        hp=14,
        st=12,
        dx=5,
        ag=6,
        lu=3,
        en=11,
      ),
      skills=[Tackle]
    ), *args, **kwargs)
    eyeball.chant_skill = chant_skill
    eyeball.chant_turns = chant_turns
    eyeball.clones = clones
    eyeball.clone = clone
    eyeball.item = None
    if rare:
      eyeball.promote(hp=False)
      eyeball.core.skills.append(HpUp)

  def chant(eyeball, skill, game):
    eyeball.chant_skill = skill
    eyeball.chant_turns = skill.chant_turns
    eyeball.core.anims.append(Eyeball.ChargeAnim(magnitude=0.5))

  def split(eyeball, game):
    if eyeball.chant_skill is None:
      return None
    eyeball.chant_skill = None
    eyeball.chant_turns = 0
    eyeball.core.anims.clear()
    eyeball.clones += 1
    return ("use_skill", Meyetosis)

  def step(eyeball, game):
    enemy = game.find_closest_enemy(eyeball)
    if enemy is None:
      return False

    if eyeball.chant_turns:
      eyeball.chant_turns -= 1
      if eyeball.chant_turns == 0:
        return eyeball.split(game)
      else:
        return None

    if (eyeball.core.hp < eyeball.core.stats.hp
    and not eyeball.clone
    and eyeball.clones < Eyeball.CLONES_MAX
    and randint(1, 3) == 1):
      return eyeball.chant(Meyetosis, game)
    elif is_adjacent(eyeball.cell, enemy.cell):
      return ("attack", enemy)
    else:
      return ("move_to", enemy.cell)

  def view(eyeball, anims):
    image = None
    offset_x, offset_y = (0, 0)
    offset_depth = 0
    offset_layer = None
    for anim_group in anims:
      for anim in [a for a in anim_group if a.target is eyeball]:
        if type(anim) is AwakenAnim:
          return super().view(MoveSprite(eyeball.facing), anims)
    if eyeball.is_dead():
      return super().view(FlinchSprite(eyeball.facing), anims)
    anim_group = [a for a in anims[0] if a.target is eyeball] if anims else []
    anim_group += eyeball.core.anims
    for anim in anim_group:
      if isinstance(anim, MoveAnim) and anim.duration != PUSH_DURATION:
        if type(anim) is Eyeball.SplitAnim:
          offset_depth = -16
        image = MoveSprite(eyeball.facing)
        break
      elif (type(anim) is AttackAnim
      and anim.time >= 0
      and anim.time < anim.duration // 2):
        image = MoveSprite(eyeball.facing)
        break
      elif type(anim) in (FlinchAnim, FlickerAnim):
        image = FlinchSprite(eyeball.facing)
        break
      elif type(anim) is BounceAnim:
        image = MoveSprite(eyeball.facing)
        offset_layer = "vfx"
        break
      elif type(anim) is Eyeball.ChargeAnim:
        image = ChargeSprite(eyeball.facing)
        offset_x = anim.offset
        break
    else:
      if eyeball.ailment == "sleep":
        image = SleepSprite(eyeball.facing)
      else:
        image = IdleSprite(eyeball.facing)
    if eyeball.ailment == "freeze":
      image = FlinchSprite(eyeball.facing)
    sprite = image and Sprite(
      image=image,
      pos=(offset_x, offset_y),
      offset=offset_depth
    ) or None
    if offset_layer:
      sprite.layer = offset_layer
    return super().view(sprite and [sprite] or None, anims)
