from dungeon.props.door import Door
from colors.palette import DARKBLUE
from lib.filters import replace_color

class PuzzleDoor(Door):
  def __init__(door, opened=False, locked=True, *args, **kwargs):
    super().__init__(opened=opened, locked=(not opened or locked), *args, **kwargs)

  def view(door, anims):
    sprites = super().view(anims)
    if not door.locked and sprites:
      sprite = sprites[0]
      sprite.image = replace_color(sprite.image, door.color, DARKBLUE)
    return sprites
