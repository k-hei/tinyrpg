from dungeon.actors import DungeonActor
from cores.knight import Knight as KnightCore
import assets
from anims.step import StepAnim
from anims.jump import JumpAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.shake import ShakeAnim
from anims.drop import DropAnim
from anims.path import PathAnim
from anims.fall import FallAnim
from anims.pause import PauseAnim
from anims.walk import WalkAnim
from lib.sprite import Sprite

class Knight(DungeonActor):
  speed = 1.5

  def __init__(knight, core=None, ailment=None, ailment_turns=0, *args, **kwargs):
    super().__init__(
      core=core or KnightCore(*args, **kwargs),
      ailment=ailment,
      ailment_turns=ailment_turns
    )

  def start_move(actor, running):
    actor.anims = [WalkAnim(period=30 if running else 60)]
    actor.core.anims = actor.anims.copy()

  def stop_move(actor):
    actor.anims = []
    actor.core.anims = []

  def charge(knight, *args, **kwargs):
    super().charge(*args, **kwargs)
    knight.core.anims.append(KnightCore.ChargeAnim())

  def attack(knight):
    if knight.facing == (0, 1):
      knight.core.anims.append(KnightCore.AttackDownAnim())

  def block(knight):
    if knight.core.anims:
      return
    if knight.facing == (0, -1):
      knight.core.anims = [KnightCore.BlockUpAnim()]
    elif knight.facing == (0, 1):
      knight.core.anims = [KnightCore.BlockDownAnim()]
    else:
      knight.core.anims = [KnightCore.BlockAnim()]

  def view(knight, anims):
    if knight.facing == (0, -1):
      knight_image = assets.sprites["knight_up"]
    elif knight.facing == (0, 1):
      knight_image = assets.sprites["knight_down"]
    else:
      knight_image = assets.sprites["knight"]
    knight_xoffset = 0
    anim_group = [a for a in anims[0] if a.target is knight] if anims else []
    anim_group += knight.core.anims
    for anim in anim_group:
      if type(anim) is PauseAnim:
        break
      if type(anim) is StepAnim or type(anim) is PathAnim or type(anim) is WalkAnim:
        x4_idx = max(0, int((anim.time - 1) % anim.period // (anim.period / 4)))
        if knight.facing == (0, -1):
          knight_image = [
            assets.sprites["knight_up"],
            assets.sprites["knight_walkup0"],
            assets.sprites["knight_up"],
            assets.sprites["knight_walkup1"]
          ][x4_idx]
          break
        if knight.facing == (0, 1):
          knight_image = [
            assets.sprites["knight_down"],
            assets.sprites["knight_walkdown0"],
            assets.sprites["knight_down"],
            assets.sprites["knight_walkdown1"]
          ][x4_idx]
          break
        elif anim.time % (anim.period // 2) >= anim.period // 4:
          knight_image = assets.sprites["knight_walk"]
          break
      elif type(anim) is JumpAnim:
        if knight.facing == (0, -1):
          knight_image = assets.sprites["knight_walkup"]
        elif knight.facing == (0, 1):
          knight_image = assets.sprites["knight_walkdown"]
        else:
          knight_image = assets.sprites["knight_walk"]
        break
      elif type(anim) is AttackAnim and anim.time < anim.duration // 2:
        if knight.facing == (0, -1):
          knight_image = assets.sprites["knight_up"]
        elif knight.facing == (0, 1):
          knight_image = assets.sprites["knight_down"]
        else:
          knight_image = assets.sprites["knight"]
        break
      elif type(anim) in (FlinchAnim, FlickerAnim, ShakeAnim, DropAnim, FallAnim):
        knight_image = assets.sprites["knight_flinch"]
        break
      elif type(anim) is KnightCore.ChargeAnim:
        knight_image = assets.sprites["knight_blockdown"][1]
        knight_xoffset = anim.offset
    if knight.ailment == "freeze":
      knight_image = assets.sprites["knight_flinch"]
    return super().view([Sprite(
      key="knight",
      image=knight_image,
      pos=(knight_xoffset, 0),
    )], anims)
