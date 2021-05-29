from dataclasses import dataclass
from dungeon.props import Prop
from assets import load as use_assets
from anims.frame import FrameAnim
from palette import WHITE, SAFFRON
from filters import replace_color
from sprite import Sprite

@dataclass
class SpriteMap:
  closed: str
  opened: str
  opening_frames: list[str]

class DoorAnim(FrameAnim): pass

class Door(Prop):
  sprites = SpriteMap(
    closed="door_puzzle",
    opened="door_puzzle_open",
    opening_frames=["door_puzzle", "door_puzzle_opening", "door_puzzle_open"]
  )

  def __init__(door):
    super().__init__(solid=True, opaque=True)
    door.opened = False

  def effect(door, game):
    if not door.opened:
      door.open()
      anim_group = [
        DoorAnim(
          duration=30,
          frames=door.sprites.opening_frames,
          target=door
        )
      ]
      if len(game.anims):
        game.anims[-1] += anim_group
      else:
        game.anims.append(anim_group)

  def open(door):
    if not door.opened:
      door.opened = True
      door.solid = False
      return True
    else:
      return False

  def render(door, anims):
    sprites = use_assets().sprites
    will_open = next((g for g in anims if next((a for a in g if a.target is door), None)), None)
    anim_group = [a for a in anims[0] if a.target is door] if anims else []
    for anim in anim_group:
      if type(anim) is DoorAnim:
        image = sprites[anim.frame]
        break
    else:
      if door.opened and not will_open:
        image = sprites[door.sprites.opened]
      else:
        image = sprites[door.sprites.closed]
    image = replace_color(image, WHITE, SAFFRON)
    return Sprite(
      image=image,
      layer="tiles"
    )
