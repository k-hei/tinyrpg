from dungeon.props import Prop
from assets import load as use_assets
from anims.frame import FrameAnim
from palette import WHITE, SAFFRON
from filters import replace_color

class DoorAnim(FrameAnim): pass

class Door(Prop):
  def __init__(door):
    super().__init__()
    door.opened = False

  def effect(door, game):
    if not door.opened:
      door.open()
      anim_group = [DoorAnim(duration=30, frame_count=3, target=door)]
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
        sprite_id = [
          "door_puzzle",
          "door_puzzle_opening",
          "door_puzzle_open"
        ][anim.frame]
        sprite = sprites[sprite_id]
        break
    else:
      if door.opened and not will_open:
        sprite = sprites["door_puzzle_open"]
      else:
        sprite = sprites["door_puzzle"]
    sprite = replace_color(sprite, WHITE, SAFFRON)
    return sprite
