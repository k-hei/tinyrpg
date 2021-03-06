from dungeon.actors import DungeonActor
from cores import Core
from skills.weapon.tackle import Tackle
from dungeon.props.chest import Chest
from assets import load as use_assets
from anims.activate import ActivateAnim
from lib.filters import replace_color
from colors.palette import BLACK, RED

class Mimic(DungeonActor):
  def __init__(mimic):
    super().__init__(Core(
      name="Mimic",
      faction="enemy",
      hp=23,
      st=13,
      en=6,
      skills=[Tackle]
    ))
    mimic.idle = True
    mimic.opened = False

  def activate(mimic):
    mimic.idle = False

  def view(mimic, anims):
    sprites = use_assets().sprites
    sprite = sprites["chest"]
    anim_group = [a for a in anims[0] if a.target is mimic] if anims else []
    for anim in anim_group:
      if type(anim) is ActivateAnim and anim.visible:
        sprite = replace_color(sprite, BLACK, RED)
        break
    else:
      if mimic.idle:
        return Chest.render(mimic, anims)
    return super().view(sprite, anims)
