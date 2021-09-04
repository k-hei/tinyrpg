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

class Eyeball(DungeonActor):
  drops = [AngelTears]
  skill = HpUp
  CLONES_MAX = 3

  class ChargeAnim(ShakeAnim): pass
  class SplitAnim(MoveAnim): pass
  class Meyetosis(Skill):
    name = "Meyetosis"
    charge_turns = 3
    def effect(user, dest, game, on_end=None):
      neighbors = [c for c in neighborhood(user.cell) if game.floor.is_cell_empty(c)]
      if neighbors:
        user.clones += 1
        neighbor = choice(neighbors)
        clone = Eyeball(clone=True, faction=user.get_faction(), facing=user.facing)
        game.anims.append([
          BounceAnim(
            duration=20,
            target=user,
            on_return=lambda: (
              game.floor.spawn_elem_at(neighbor, clone),
              game.anims[0].append(
                Eyeball.SplitAnim(
                  duration=15,
                  target=clone,
                  src=user.cell,
                  dest=neighbor,
                  on_end=on_end
                )
              )
            )
          )
        ])
      else:
        game.anims.append([BounceAnim(
          duration=20,
          target=user,
          on_end=on_end
        )])

  def __init__(eyeball, name="Eyeball", faction="enemy", rare=False, clones=0, clone=False, *args, **kwargs):
    super().__init__(Core(
      name=name,
      faction=faction,
      stats=Stats(
        hp=14,
        st=11,
        dx=5,
        ag=6,
        lu=3,
        en=11,
      ),
      skills=[Tackle],
      message=[
        (name, "You looking thick as hell bro! Boutta make me act up. No homo though.")
      ]
    ), *args, **kwargs)
    eyeball.clones = clones
    eyeball.clone = clone
    eyeball.item = None
    if rare:
      eyeball.promote(hp=False)
      eyeball.core.skills.append(HpUp)

  def charge(eyeball, *args, **kwargs):
    super().charge(*args, **kwargs)
    eyeball.core.anims.append(Eyeball.ChargeAnim(magnitude=0.5))

  def discharge(eyeball):
    eyeball.core.anims.clear()
    return super().discharge()

  def step(eyeball, game):
    enemy = game.find_closest_enemy(eyeball)
    if enemy is None:
      return False

    command = eyeball.step_charge()
    if command: return command

    if (eyeball.core.hp < eyeball.core.stats.hp
    and not eyeball.clone
    and eyeball.clones < Eyeball.CLONES_MAX
    and randint(1, 3) == 1):
      return eyeball.charge(Eyeball.Meyetosis)
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
