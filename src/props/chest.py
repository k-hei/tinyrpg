from props import Prop
from assets import load as use_assets
from filters import replace_color
from anims.chest import ChestAnim
import palette

class Chest(Prop):
  def __init__(chest, contents, rare=False):
    super().__init__(name="Chest")
    chest.contents = contents
    chest.rare = rare
    chest.opened = False

  def open(chest):
    contents = chest.contents
    chest.contents = None
    chest.opened = True
    return contents

  def render(chest, anims):
    sprites = use_assets().sprites
    anim_group = [a for a in anims[0] if a.target is chest] if anims else []
    for anim in anim_group:
      if type(anim) is ChestAnim:
        frame = anim.frame + 1
        sprite = sprites["chest_open" + str(frame)]
        break
    else:
      if chest.opened:
        sprite = sprites["chest_open"]
      else:
        sprite = sprites["chest"]
    color = palette.PINK if chest.rare else palette.GOLD
    sprite = replace_color(sprite, palette.BLACK, color)
    return sprite
