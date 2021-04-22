from actors import Actor
from props.chest import Chest
from assets import load as use_assets
from anims.activate import ActivateAnim
from filters import replace_color
import palette

class Mimic(Actor):
  def __init__(mimic):
    super().__init__(
      name="Mimic",
      faction="enemy",
      hp=23,
      st=13,
      en=6
    )
    mimic.idle = True
    mimic.opened = False

  def activate(mimic):
    mimic.idle = False

  def render(mimic, anims):
    sprites = use_assets().sprites
    sprite = sprites["chest"]
    anim_group = [a for a in anims[0] if a.target is mimic] if anims else []
    for anim in anim_group:
      if type(anim) is ActivateAnim and anim.visible:
        sprite = replace_color(sprite, palette.BLACK, palette.RED)
        break
    else:
      if mimic.idle:
        return Chest.render(mimic, anims)
    return super().render(sprite, anims)
