from dungeon.element import DungeonElement
from assets import load as use_assets
from filters import replace_color
from palette import BLACK, WHITE, GRAY, PURPLE, SAFFRON, SAFFRON_DARK
from sprite import Sprite

class PushTile(DungeonElement):
  def __init__(tile):
    super().__init__(solid=False)
    tile.pushed = False

  def effect(tile, game):
    tile.pushed = True

  def view(tile, anims):
    assets = use_assets()
    tile_image = assets.sprites["push_tile"]
    tile_image = replace_color(tile_image, GRAY, SAFFRON_DARK)
    if tile.pushed:
      tile_image = replace_color(tile_image, WHITE, PURPLE)
    return super().view(Sprite(
      image=tile_image,
      layer="decors"
    ), anims)
