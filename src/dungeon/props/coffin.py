from dungeon.props import Prop
from assets import load as use_assets
from config import TILE_SIZE
from palette import WHITE, COLOR_TILE
from filters import replace_color
import vfx

class Coffin(Prop):
  def __init__(coffin, contents=None):
    super().__init__()
    coffin.contents = contents
    coffin.opened = False

  def effect(coffin, game):
    coffin.open()
    # x, y = coffin.cell
    # x, y = x * TILE_SIZE, y * TILE_SIZE
    # game.vfx.append(CoffinLid(pos=(x, y)))

  def open(coffin):
    contents = coffin.contents
    coffin.contents = None
    coffin.opened = True
    return contents

  def render(coffin, anims):
    sprites = use_assets().sprites
    if coffin.opened:
      sprite = sprites["coffin_open"]
    else:
      sprite = sprites["coffin"]
    sprite = replace_color(sprite, WHITE, COLOR_TILE)
    return sprite

# class CoffinLid(Vfx):
#   def __init__(vfx, pos):
#     super().__init__(kind="coffin_lid", pos=pos)
