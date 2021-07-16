from dataclasses import dataclass
from dungeon.props.door import Door
from colors.palette import PURPLE, SAFFRON
from filters import replace_color

class PuzzleDoor(Door):
  def __init__(door, locked=True, *args, **kwargs):
    super().__init__(opened=(not locked), locked=locked, *args, **kwargs)

  def view(door, anims):
    sprites = super().view(anims)
    if not door.locked and sprites:
      sprite = sprites[0]
      sprite.image = replace_color(sprite.image, SAFFRON, PURPLE)
    return sprites
