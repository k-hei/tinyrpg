from math import pi, sin
from cores import Core, Stats
import assets
from lib.sprite import Sprite
from lib.filters import ripple
from anims.frame import FrameAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.shake import ShakeAnim

FLOAT_PERIOD = 180
FLOAT_AMP = 2

class Ghost(Core):
  class ChargeAnim(ShakeAnim): pass
  class LaughAnim(FrameAnim):
    frames = assets.sprites["ghost_laugh"]
    frames_duration = 5
    loop = True
  class TurnAnim(FrameAnim):
    frames = [assets.sprites["ghost_turn"]]
    frames_duration = 5
  class WhipAnim(FrameAnim):
    frames = assets.sprites["ghost_whip"]
    frames_duration = [7, 7, 40]

  def __init__(ghost, name="Greedy Ghost", faction="enemy", *args, **kwargs):
    super().__init__(
      name=name,
      faction=faction,
      stats=Stats(
        hp=14,
        st=13,
        dx=7,
        ag=14,
        lu=8,
        en=8,
      ),
      message=[
        (name, "You be squirtin? Or you on the cream team?")
      ],
      *args,
      **kwargs
    )
    ghost.time = 0
    ghost.flipped = False

  def update(ghost):
    super().update()
    ghost.time += 1

  def view(ghost, sprites=[], anims=[]):
    if not sprites:
      return None
    is_flinching = next((a for a in anims if type(a) in (FlinchAnim, FlickerAnim)), False)
    is_whipping = next((a for a in ghost.anims if type(a) is Ghost.WhipAnim), False)
    ghost_sprite, *other_sprites = sprites
    old_flipped = ghost.flipped
    if not ghost.flipped and ghost.facing[0] == -1:
      ghost.flipped = True
    elif ghost.flipped and ghost.facing[0] == 1:
      ghost.flipped = False
    if ghost.flipped != old_flipped:
      turn_anim = Ghost.TurnAnim()
      ghost.anims.append(turn_anim)
      ghost_sprite.image = turn_anim.frame()
    if not is_whipping:
      ghost_sprite.image = ripple(ghost_sprite.image,
        start=(0 if is_flinching else 16),
        end=32,
        waves=(4 if is_flinching else 2),
        period=(45 if is_flinching else 90),
        time=ghost.time,
        pinch=not is_flinching)
      ghost_y = sin(ghost.time % FLOAT_PERIOD / FLOAT_PERIOD * 2 * pi) * FLOAT_AMP
      ghost_sprite.move((0, ghost_y))
    return super().view([ghost_sprite, *other_sprites])
