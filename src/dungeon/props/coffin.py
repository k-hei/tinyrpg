from random import randint
from dungeon.props import Prop
import assets
from filters import replace_color
from anims.item import ItemAnim
from items.gold import Gold
from contexts.dialogue import DialogueContext
from config import TILE_SIZE
from colors.palette import WHITE, COLOR_TILE, DARKBLUE

class Coffin(Prop):
  static = True
  solid = True

  def __init__(coffin, contents=None, locked=False):
    super().__init__()
    coffin.contents = contents
    coffin.locked = locked
    coffin.active = not locked
    coffin.unlocked = False
    coffin.opened = False

  def effect(coffin, game):
    item = coffin.open()
    coffin.contents = None
    item_anim = None
    if item:
      if game.store.obtain(item):
        if type(item) is type:
          item = item()
        game.anims.append([
          item_anim := ItemAnim(
            target=coffin,
            item=item
          )
        ])
        script = [("", ("Obtained ", item.token(), "."))]
      else:
        script = ["Your inventory is already full!"]
    else:
      script = ["It's empty..."]
    game.open(child=DialogueContext(
      lite=True,
      script=script
    ), on_close=lambda: item_anim and item_anim.end())

  def unlock(coffin):
    coffin.locked = False
    coffin.active = True
    coffin.unlocked = True

  def open(coffin):
    coffin.opened = True
    return coffin.contents

  def view(coffin, anims):
    if coffin.opened:
      coffin_image = assets.sprites["coffin_open"]
    else:
      coffin_image = assets.sprites["coffin"]
    coffin_color = DARKBLUE if coffin.unlocked else COLOR_TILE
    coffin_image = replace_color(coffin_image, WHITE, coffin_color)
    return super().view(coffin_image, anims)

# class CoffinLid(Vfx):
#   def __init__(vfx, pos):
#     super().__init__(kind="coffin_lid", pos=pos)
