from random import random, randint
from lib.cell import add as add_vector
from dungeon.props import Prop
from vfx.poisonpuff import PoisonPuffVfx
import assets
from lib.sprite import Sprite
from anims.offsetmove import OffsetMoveAnim
from config import TILE_SIZE
from lib.filters import replace_color

class PoisonPuff(Prop):
  MAX_TURNS = 7
  expires = True

  def __init__(puff, origin, *args, **kwargs):
    super().__init__(*args, **kwargs)
    puff.turns = PoisonPuff.MAX_TURNS
    puff.origin = origin
    puff.vfx = None
    puff.dissolving = False
    puff.done = False

  def effect(puff, game, actor=None):
    if puff.dissolving:
      return False
    actor = actor or game.hero
    if type(actor).__name__ == "Mushroom":
      return False
    game.inflict_poison(actor)
    return True

  def dissolve(puff):
    if puff.dissolving:
      return False
    puff.dissolving = True
    puff.turns = 0
    for i, fx in enumerate(puff.vfx):
      fx.dissolve(delay=i * 5, on_end=(lambda: (
        setattr(puff, "done", True)
      )) if fx == puff.vfx[-1] else None)

  def step(puff, *_):
    if puff.turns:
      puff.turns -= 1
    elif not puff.dissolving:
      puff.dissolve()

  def update(puff, *_):
    if puff.vfx:
      return []
    src = tuple([x * TILE_SIZE for x in puff.origin])
    dest = tuple([x * TILE_SIZE for x in puff.cell])
    puff.vfx = (
      [PoisonPuffVfx(src, dest, elev=puff.elev, size="large") for _ in range(randint(3, 6))]
      + [PoisonPuffVfx(src, dest, elev=puff.elev, size="medium") for _ in range(randint(3, 6))]
      + [PoisonPuffVfx(src, dest, elev=puff.elev, size="small") for _ in range(randint(3, 6))]
      + [PoisonPuffVfx(src, dest, elev=puff.elev, size="tiny") for _ in range(randint(3, 6))]
    )
    return puff.vfx

  def view(puff, anims):
    return []
