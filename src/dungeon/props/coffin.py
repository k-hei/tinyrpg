from random import randint
from dungeon.props import Prop
import assets
from filters import replace_color
from anims.item import ItemAnim
from items.gold import Gold
from config import TILE_SIZE
from colors.palette import WHITE, COLOR_TILE

class Coffin(Prop):
  static = True
  solid = True

  def __init__(coffin, contents=None):
    super().__init__()
    coffin.contents = contents
    coffin.opened = False

  def effect(coffin, game):
    if coffin.contents:
      if type(coffin.contents) is Gold:
        gold = coffin.contents
        game.change_gold(gold.amount)
        game.log.print("Received {} gold.".format(gold.amount))
      game.anims.append([
        ItemAnim(
          duration=30,
          target=coffin,
          item=coffin.contents
        )
      ])
    coffin.open()

  def open(coffin):
    contents = coffin.contents
    coffin.contents = None
    coffin.opened = True
    return contents

  def view(coffin, anims):
    if coffin.opened:
      coffin_image = assets.sprites["coffin_open"]
    else:
      coffin_image = assets.sprites["coffin"]
    coffin_image = replace_color(coffin_image, WHITE, COLOR_TILE)
    return super().view(coffin_image, anims)

# class CoffinLid(Vfx):
#   def __init__(vfx, pos):
#     super().__init__(kind="coffin_lid", pos=pos)
