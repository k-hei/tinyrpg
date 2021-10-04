from pygame import Rect
from dungeon.props import Prop
from lib.sprite import Sprite
import assets
from anims.pause import PauseAnim
from vfx.geyser import GeyserVfx

class Trap(Prop):
  def __init__(trap, *args, **kwargs):
    super().__init__(*args, **kwargs)
    trap.triggered = False

  def effect(trap, game, actor):
    if trap.triggered:
      return False
    trap.triggered = True
    game.vfx.append(GeyserVfx(cell=trap.cell, delay=15))
    game.anims.append([
      PauseAnim(duration=30, on_end=lambda: (
        actor.inflict_ailment("sleep"),
        game.step()
      ))
    ])
    return True

  def view(trap, anims):
    trap_image = assets.sprites["floor"]
    trap_yoffset = 4 if trap.triggered else 0
    if trap_yoffset:
      trap_image = trap_image.subsurface(Rect(
        (0, 0),
        (trap_image.get_width(), trap_image.get_height() - trap_yoffset)
      ))
    return [Sprite(
      image=trap_image,
      pos=(0, -trap_yoffset // 2),
      layer="tiles"
    )]
