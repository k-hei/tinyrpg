from pygame import Rect
from dungeon.element import DungeonElement
import assets
from lib.sprite import Sprite
from lib.filters import replace_color
import lib.vector as vector
from colors.palette import WHITE, GOLD
from config import TILE_SIZE

class Altar(DungeonElement):
  solid = True
  static = True
  active = True

  def __init__(altar, on_action=None, *args, **kwargs):
    super().__init__(static=True, size=(1, 2), *args, **kwargs)
    altar.on_action = on_action
    altar.opened = False

  @property
  def rect(door):
    if door._rect is None and door.pos:
      door._rect = Rect(
        vector.subtract(door.pos, (16, 16)),
        (32, 64)
      )
    return door._rect

  def effect(altar, game, *_):
    if altar.opened:
      return False
    altar.opened = True
    altar.on_action and altar.on_action(game.room, game)
    return False

  def view(altar, anims):
    altar_image = assets.sprites["altar"]
    if altar.opened:
      altar_image = assets.sprites["altar_open"]
    altar_image = replace_color(altar_image, WHITE, GOLD)
    altar_sprite = Sprite(
      image=replace_color(altar_image, WHITE, GOLD),
      pos=(0, TILE_SIZE / 2),
      offset=-TILE_SIZE,
      layer="elems"
    )
    return super().view([altar_sprite], anims)
