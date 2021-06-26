from pygame import Surface
from sprite import Sprite

class DungeonElement:
  def __init__(elem, solid=True, opaque=False):
    elem.solid = solid
    elem.opaque = opaque
    elem.cell = None

  def view(elem, sprite, anims=[]):
    if type(sprite) is Surface:
      return [Sprite(image=sprite, layer="elems")]
    if type(sprite) is Sprite:
      return [sprite]
    return sprite
