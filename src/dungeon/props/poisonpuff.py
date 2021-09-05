from random import random, randint
from lib.cell import add as add_vector
from dungeon.props import Prop
from vfx.poisonpuff import PoisonPuffVfx
import assets
from sprite import Sprite
from anims.offsetmove import OffsetMoveAnim
from config import TILE_SIZE
from filters import replace_color

class PoisonPuff(Prop):
  def __init__(puff, origin, *args, **kwargs):
    super().__init__(*args, **kwargs)
    puff.turns = 7
    puff.origin = origin
    puff.vfx = []
    puff.dissolving = False

  def effect(puff, game, actor=None):
    if not puff.dissolving:
      actor = actor or game.hero
      game.poison_actor(actor)

  def step(puff, game):
    if puff.turns:
      puff.turns -= 1
    elif not puff.dissolving:
      puff.dissolving = True
      for i, fx in enumerate(puff.vfx):
        fx.dissolve(delay=i * 5, on_end=(lambda: game.floor.remove_elem(puff)) if fx == puff.vfx[-1] else None)

  def update(puff, *_):
    for fx in puff.vfx:
      if fx.done:
        puff.vfx.remove(fx)
      else:
        fx.update()

  def view(puff, anims):
    if not puff.vfx:
      src = tuple([x * TILE_SIZE for x in puff.origin])
      dest = tuple([x * TILE_SIZE for x in puff.cell])
      puff.vfx = (
        [PoisonPuffVfx(src, dest, size="large") for i in range(randint(3, 6))]
        + [PoisonPuffVfx(src, dest, size="medium") for i in range(randint(3, 6))]
        + [PoisonPuffVfx(src, dest, size="small") for i in range(randint(3, 6))]
        + [PoisonPuffVfx(src, dest, size="tiny") for i in range(randint(3, 6))]
      )
    return super().view([n for m in [fx.view() for fx in puff.vfx] for n in m], anims)
