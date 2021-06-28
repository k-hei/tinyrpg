from dataclasses import dataclass
from dungeon.props.door import Door
from palette import PURPLE, SAFFRON
from filters import replace_color

class PuzzleDoor(Door):
  def __init__(door):
    super().__init__(locked=True)

  def view(door, anims):
    sprites = super().view(anims)
    if not door.locked and sprites:
      sprite = sprites[0]
      sprite.image = replace_color(sprite.image, SAFFRON, PURPLE)
    return sprites
